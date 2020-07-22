############################################
# R code for logistic regression:
require(ggplot2)
require(GGally)
require(reshape2)
require(lme4)
require(compiler)
require(parallel)
require(boot)
require(lattice)
library(ggeffects)
library(dplyr)

# MISSING ANALYSIS: 

# import data:
data <- readr::read_csv("../Python/predict_missing_logistic_df.csv", col_names = TRUE)

# remove index column: 
data <- data[,-1]

# remove ids that have less 1% observations in data: 

num_ids = length(unique(data[['id']]))

cutoff = nrow(data) * 0.01

good_ids_df = data %>% 
  dplyr::group_by(id) %>% 
  dplyr::summarise(observation_count = n()) %>% 
  dplyr::filter(observation_count >= cutoff) %>% 
  dplyr::select(id) 

good_ids = good_ids_df[['id']]

good_data = data %>% 
  dplyr::filter(id %in% good_ids)

# Remove outliers based on episode length:
Q <- quantile(good_data$episode_length, probs=c(.25, .75), na.rm = FALSE)
iqr <- IQR(good_data$episode_length)
up <- Q[2] + (1.5 * iqr) # Upper Range
low <- Q[1] - (1.5 * iqr) # Lower Range﻿

clean_data <- subset(good_data, good_data$episode_length > (Q[1] - (1.5 * iqr)) & good_data$episode_length < (Q[2] + (1.5 * iqr)))

# convert NAs in episode length to 0s:
clean_data$previous_episode_length[is.na(clean_data$previous_episode_length)] <- 0
clean_data$prev_day_activity_prop[is.na(clean_data$prev_day_activity_prop)] <- 0
clean_data$prev_day_bad_qual_rep_prop[is.na(clean_data$prev_day_bad_qual_rep_prop)] <- 0
clean_data$prev_day_bad_qual_ecg_prop[is.na(clean_data$prev_day_bad_qual_ecg_prop)] <- 0

# standardise variables:
episode_length_std <- sjmisc::std(clean_data$episode_length)
previous_episode_length_std <- sjmisc::std(clean_data$previous_episode_length)
prev_day_activity_prop_std <- sjmisc::std(clean_data$prev_day_activity_prop)
prev_day_bad_qual_rep_prop_std <- sjmisc::std(clean_data$prev_day_bad_qual_rep_prop)
prev_day_bad_qual_ecg_prop_std <- sjmisc::std(clean_data$prev_day_bad_qual_ecg_prop)
num_ints_trig_prev_day_std <- sjmisc::std(clean_data$num_ints_trig_prev_day)

clean_data['episode_length_std'] <- episode_length_std
clean_data['previous_episode_length_std'] <- previous_episode_length_std
clean_data['prev_day_activity_prop_std'] <- prev_day_activity_prop_std
clean_data['prev_day_bad_qual_rep_prop_std'] <- prev_day_bad_qual_rep_prop_std
clean_data['prev_day_bad_qual_ecg_prop_std'] <- prev_day_bad_qual_ecg_prop_std
clean_data['num_ints_trig_prev_day_std'] <- num_ints_trig_prev_day_std

# build training and testing set from data:

library(caret)
library(dplyr)
# separate data by id:
uq_ids <- unique(clean_data$id)
train_ids <- sort(sample(uq_ids, 0.8*length(uq_ids)))
test_ids <- uq_ids[!(uq_ids %in% train_ids)]

train_dat <- clean_data %>%
  dplyr::filter(id %in% train_ids)
test_dat <- clean_data %>%
  dplyr::filter(id %in% test_ids)

# create all models on training data:


# colnames(clean_data)
#  [1] "id"                                     
#  [2] "day"                                    
#  [3] "day_num"                                
#  [4] "available_decision_point"               
#  [5] "available_decision_point_stress_episode"
#  [6] "episode_type_miss"                      
#  [7] "episode_type_stress"                    
#  [8] "episode_type_no_stress"                 
#  [9] "episode_length"                         
# [10] "previous_episode_miss"                  
# [11] "previous_episode_stress"                
# [12] "previous_episode_no_stress"             
# [13] "previous_episode_length"                
# [14] "prev_day_activity_prop"                 
# [15] "prev_day_bad_qual_rep_prop"             
# [16] "prev_day_bad_qual_ecg_prop"             
# [17] "num_ints_trig_prev_day"                 
# [18] "episode_length_std"                     
# [19] "previous_episode_length_std"            
# [20] "prev_day_activity_prop_std"             
# [21] "prev_day_bad_qual_rep_prop_std"         
# [22] "prev_day_bad_qual_ecg_prop_std"         
# [23] "num_ints_trig_prev_day_std"    


# logistic regression:
m1_train <- glmer(
    as.factor(episode_type_miss) ~ as.factor(day_num) + episode_length_std + as.factor(previous_episode_miss)  
                   + as.factor(episode_type_stress) + as.factor(episode_type_no_stress)
                   + as.factor(previous_episode_stress) + as.factor(previous_episode_no_stress)
                   + previous_episode_length_std + prev_day_activity_prop_std
                   + prev_day_bad_qual_rep_prop_std + prev_day_bad_qual_ecg_prop_std
                   + num_ints_trig_prev_day_std + (1 | id),
    data = train_dat,
    family = binomial(link = "logit"),
    control = glmerControl(optimizer = "bobyqa"),
    nAGQ = 10
)

# random forest:
library(randomForest)
m2_train = randomForest(
    as.factor(episode_type) ~ day_num + episode_length_std + previous_episode_type
                   + previous_episode_length_std + prev_day_activity_prop_std
                   + prev_day_bad_qual_rep_prop_std + prev_day_bad_qual_ecg_prop_std
                   + num_ints_trig_prev_day_std,
    data = train_dat,
    ntree = 5000,
    importance=TRUE
)



# print the mod results without correlations among fixed effects
print(m1, corr = FALSE)

# For logistic regression models, since ggeffects returns marginal effects on the
# response scale, the predicted values are predicted probabilities. Furthermore,
# for mixed models, the predicted values are typically at the population level,
# not group-specific.
me_day_num <- ggpredict(m1, "day_num")
me_episode_length <- ggpredict(m1, "episode_length_std")
me_previous_episode_type <- ggpredict(m1, "previous_episode_type")
me_previous_episode_length <- ggpredict(m1, "previous_episode_length_std")
me_prev_day_activity_prop <- ggpredict(m1, "prev_day_activity_prop_std")
me_prev_day_bad_qual_rep_prop <- ggpredict(m1, "prev_day_bad_qual_rep_prop_std")
me_prev_day_bad_qual_ecg_prop <- ggpredict(m1, "prev_day_bad_qual_ecg_prop_std")
me_num_ints_trig_prev_day <- ggpredict(m1, "num_ints_trig_prev_day_std")

# plot marginal effects:
plot(me_day_num)
plot(me_episode_length)
plot(me_previous_episode_type)
plot(me_previous_episode_length)
plot(me_prev_day_activity_prop)
plot(me_prev_day_bad_qual_rep_prop)
plot(me_prev_day_bad_qual_ecg_prop)
plot(me_num_ints_trig_prev_day)

# Test model:


mod_fit <- train(
    as.factor(episode_type) ~ as.factor(day_num) + episode_length_std
                              + as.factor(previous_episode_type)
                              + previous_episode_length_std + (1 | id),
    data = training,
    method = "glmer",
    family = binomial(link = "logit"))
############################################
