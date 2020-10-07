
# Last changed on: 23rd Sept 2020
# Last changed by: Marianne Menictas

# load required libraries:

library(dplyr)

# set flags: 

analytic_vs_numeric <- FALSE

# sample_size <- 10 # number of users
# num_days <- 10
# num_dec_points_per_day <- 720 # 12 hours X 60 minutes

dgm_trivariate_categorical_covariate <- function(sample_size, num_days, num_dec_points_per_day) {

    total_T <- num_days * num_dec_points_per_day

    beta_11_true <- 0.1
    beta_10_true <- 0.6 
    beta_21_true <- 0.2
    beta_20_true <- 0.6

    prob_a <- 0.2  # randomization probability
    
    df_names <- c("user_id", "day", "day_dec_point", "total_dec_point", "Y", "Y1", "Y2", "Y3", "A", "S", 
                  "S2", "prob_Y1", "X", "prob_Y2", "prob_Y3", "prob_A", "M", "I")
    
    data <- data.frame(matrix(NA, nrow = sample_size * total_T, ncol = length(df_names)))
    names(data) <- df_names
    
    data$user_id <- rep(1:sample_size, each = total_T)
    data$day <- rep(1:num_days, each = num_dec_points_per_day)
    data$day_dec_point <- rep(1:num_dec_points_per_day, times = num_days)
    data$total_dec_point <- rep(1:total_T, times = sample_size)
    
    for (t in 1:total_T) # looping through total dec points: 
    {
        print(paste0("t: ", t))
        row_index <- seq(from = t, by = total_T, length = sample_size)
        
        # compute covariates: 

        data$S[row_index] <- sample(c(0,1,2), sample_size, replace = TRUE)
        data$S2[row_index] <- ifelse(data$S[row_index] == 2, 1, 0) 
        data$prob_A[row_index] <- rep(prob_a, sample_size)
        data$A[row_index] <- rbinom(sample_size, 1, data$prob_A[row_index])
        data$X[row_index] <- ifelse(data$S[row_index] == 0, 1, ifelse(data$S[row_index] == 1, 0, 0))

        data$prob_Y1[row_index] <- 0.2 * exp(data$A[row_index] * (beta_11_true * data$X[row_index] + beta_10_true * (1 - data$X[row_index])))
        data$prob_Y2[row_index] <- 0.3 * exp(data$A[row_index] * (beta_21_true * data$X[row_index] + beta_20_true * (1 - data$X[row_index])))
        data$prob_Y3[row_index] <- 1 - (data$prob_Y1[row_index] + data$prob_Y2[row_index])

        Y <- extraDistr::rcat(
            n = sample_size, 
            p = cbind(data$prob_Y1[row_index], data$prob_Y2[row_index], data$prob_Y3[row_index]), 
            labels = c(1, 2, 3)
        )

        Y1 <- as.numeric(Y == 1)
        Y2 <- as.numeric(Y == 2)
        Y3 <- as.numeric(Y == 3)
        
        # missing data indicator: 

        data$M[row_index] <- rbinom(sample_size, 1, 0.8)
        I <- rbinom(sample_size, 1, 0.75)

        # make Y, Y1, Y2 and Y3 unobserved when M = 0: 

        data$Y[row_index] <- data$M[row_index] * as.numeric(Y)
        data$Y1[row_index] <- data$M[row_index] * Y1
        data$Y2[row_index] <- data$M[row_index] * Y2
        data$Y3[row_index] <- data$M[row_index] * Y3
        data$I[row_index] <- data$M[row_index] * I
    }
    
    return(data)
}

# try out the range of Y

if (0) 
{
    set.seed(123)

    sample_size <- 10 # number of users
    num_days <- 10
    num_dec_points_per_day <- 3

    data <- dgm_trivariate_categorical_covariate(sample_size, num_days, num_dec_points_per_day)

    summary(data$prob_Y1)
    summary(data$prob_Y2)
    summary(data$prob_Y3)
    summary(data$prob_A)
}

# compute marginal beta_trues

if (analytic_vs_numeric) {

    # numerically:
    
    set.seed(123)

    #sample_size <- 500000 # number of users
    sample_size <- 1000 # number of users
    num_days <- 10
    num_dec_points_per_day <- 3

    data <- dgm_trivariate_categorical_covariate(sample_size, num_days, num_dec_points_per_day)

    beta_marginal <- data %>% 
      dplyr::group_by(A, X) %>% 
      dplyr::summarise(Y1_mean = mean(Y1), Y2_mean = mean(Y2), Y3_mean = mean(Y3)) %>% 
      dplyr::ungroup()

    beta_true_marginal_11 <- log(beta_marginal$Y1_mean[4]/beta_marginal$Y1_mean[2])
    beta_true_marginal_10 <- log(beta_marginal$Y1_mean[3]/beta_marginal$Y1_mean[1])
    beta_true_marginal_21 <- log(beta_marginal$Y2_mean[4]/beta_marginal$Y2_mean[2])
    beta_true_marginal_20 <- log(beta_marginal$Y2_mean[3]/beta_marginal$Y2_mean[1])

    beta_11_true <- 0.1
    beta_10_true <- 0.6 
    beta_21_true <- 0.2
    beta_20_true <- 0.6

    compar_mat <- as.matrix(
        cbind(
            c(beta_11_true, beta_10_true, beta_21_true, beta_20_true), 
            c(beta_true_marginal_11, beta_true_marginal_10, beta_true_marginal_21, beta_true_marginal_20), 
            c(round(beta_true_marginal_11/beta_11_true,3), round(beta_true_marginal_10/beta_10_true,3), 
              round(beta_true_marginal_21/beta_21_true,3), round(beta_true_marginal_20/beta_20_true,3))
            )
        )

    colnames(compar_mat) <- c("true", "numerically", "ratio")
    print(compar_mat)
}





