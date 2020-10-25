
# Last changed on: 24th Oct 2020
# Last changed by: Marianne Menictas

# load required libraries:

library(dplyr)
library(data.table)

# set flags: 

test_range_y <- FALSE
analytic_vs_numeric <- FALSE

dgm_trivariate_categorical_covariate <- function(sample_size, num_days, num_dec_points_per_day, time_window_for_Y) {

    total_T <- num_days * num_dec_points_per_day

    beta_11_true <- 0.1
    beta_10_true <- 0.3
    beta_21_true <- 0.2
    beta_20_true <- 0.4

    xi_true <- -0.5
    eta_true <- -0.45

    prob_a <- 0.2  # randomization probability 
    
    df_names <- c("user_id", "day", "day_dec_point", "total_dec_point", "Y", "Y1", "Y2", "Y3", "A", "S", 
                  "S2", "prob_Y1", "X", "prob_Y2", "prob_Y3", "prob_A", "M", "I")
    
    data <- data.frame(matrix(NA, nrow = sample_size * total_T, ncol = length(df_names)))
    names(data) <- df_names
    
    data$user_id <- rep(1:sample_size, each = total_T)
    data$day <- rep(1:num_days, each = num_dec_points_per_day)
    data$day_dec_point <- rep(1:num_dec_points_per_day, times = num_days)
    data$total_dec_point <- rep(1:total_T, times = sample_size)
    
    for (i in 1:sample_size)
    {
        row_index <- seq(from=((i-1) * total_T + 1), to = i * total_T)
        
        # compute covariates: 

        data$S[row_index] <- sample(c(0,1,2), total_T, replace = TRUE)
        data$S2[row_index] <- ifelse(data$S[row_index] == 2, 1, 0) 
        data$prob_A[row_index] <- rep(prob_a, total_T)
        data$A[row_index] <- rbinom(total_T, 1, data$prob_A[row_index])
        data$X[row_index] <- ifelse(data$S[row_index] == 0, 1, ifelse(data$S[row_index] == 1, 0, 0))

        # following code only works for time_window = 2. 
        ##############################
        # TODO: Make for general m eventually. 
        ##############################

        data$prob_Y1[row_index[1]] <-  0.2 * exp(data$A[1] * (beta_11_true * data$X[1] + beta_10_true * (1 - data$X[1])))
        data$prob_Y2[row_index[1]] <-  0.3 * exp(data$A[1] * (beta_21_true * data$X[1] + beta_20_true * (1 - data$X[1])))
        data$prob_Y3[row_index[1]] <-  1 - (data$prob_Y1[row_index[1]] + data$prob_Y2[row_index[1]])

        t_minus_1 <- row_index[-1]
        t_minus_2 <- row_index[-total_T]

        data$prob_Y1[row_index[-1]] <- (0.2 * exp(data$A[t_minus_1] * (beta_11_true * data$X[t_minus_1] + beta_10_true * (1 - data$X[t_minus_1])))
                                                * exp(data$A[t_minus_2] * (beta_11_true * data$X[t_minus_2] + beta_10_true * (1 - data$X[t_minus_2]))))
        data$prob_Y2[row_index[-1]] <- (0.15 * exp(data$A[t_minus_1] * (beta_21_true * data$X[t_minus_1] + beta_20_true * (1 - data$X[t_minus_1])))
                                                * exp(data$A[t_minus_2] * (beta_21_true * data$X[t_minus_2] + beta_20_true * (1 - data$X[t_minus_2]))))
        data$prob_Y3[row_index[-1]] <- 1 - (data$prob_Y1[row_index[-1]] + data$prob_Y2[row_index[-1]])

        data$Y[row_index] <- extraDistr::rcat(
            n = total_T, 
            p = cbind(data$prob_Y1[row_index], data$prob_Y2[row_index], data$prob_Y3[row_index]), 
            labels = c(1, 2, 3)
        )
        
        data$Y1[row_index] <- as.numeric(data$Y[row_index] == 1)
        data$Y2[row_index] <- as.numeric(data$Y[row_index] == 2)
        data$Y3[row_index] <- as.numeric(data$Y[row_index] == 3)
        
        # missing data indicator: 
        # following code only works for time_window = 2. 
        ##############################
        # TODO: Make for general m eventually. 
        ##############################

        # data$prob_M[row_index[1]] <- NA
        # data$prob_M[row_index[2]] <- NA
        # data$prob_M[row_index[-(1:2)]] <- exp(data$S[t_minus_2] * xi_true + data$A[t_minus_2] * data$S[t_minus_2] * eta_true)
        # data$M[row_index[-(1:2)]] <- rbinom(total_T - 2, 1, data$prob_M[row_index[-(1:2)]])
        
        # # I depends on M_{t-1}: 

        # data$I[row_index[1]] <- 0
        # data$I[row_index[-1]] <- data$M[row_index[-total_T]]

        # # make Y, Y1, Y2 and Y3 unobserved when M = 0: 

        # data$Y[row_index] <- data$M[row_index] * as.numeric(data$Y[row_index])
        # data$Y1[row_index] <- data$M[row_index] * Y1
        # data$Y2[row_index] <- data$M[row_index] * Y2
        # data$Y3[row_index] <- data$M[row_index] * Y3
    }

    return(list(data = data, beta_true = c(beta_11_true, beta_10_true, beta_21_true, beta_20_true)))
}

# try out the range of Y

if (test_range_y) 
{
    set.seed(123)

    sample_size <- 10 # number of users
    num_days <- 10
    num_dec_points_per_day <- 3

    data <- dgm_trivariate_categorical_covariate(sample_size, num_days, num_dec_points_per_day)[['data']]

    summary(data$prob_Y1)
    summary(data$prob_Y2)
    summary(data$prob_Y3)
    summary(data$prob_A)
}

if (analytic_vs_numeric) {

    # numerically:
    
    set.seed(123)

    sample_size <- 400 # number of users
    num_days <- 10
    num_dec_points_per_day <- 10
    total_dec_points <- num_days * num_dec_points_per_day

    data_model <- dgm_trivariate_categorical_covariate(sample_size, num_days, num_dec_points_per_day)
    data <- data_model[['data']]
    beta_true <- data_model[['beta_true']]
    dt = as.data.table(data)

    denom_111 <- 0  ;  denom_110 <- 0   
    denom_011 <- 0  ;  denom_010 <- 0   
    denom_101 <- 0  ;  denom_100 <- 0   
    denom_001 <- 0  ;  denom_000 <- 0   
    numer_1111 <- 0  ;  numer_1101 <- 0   
    numer_1110 <- 0  ;  numer_1100 <- 0   
    numer_1011 <- 0  ;  numer_1001 <- 0   
    numer_1010 <- 0  ;  numer_1000 <- 0   
    numer_2111 <- 0  ;  numer_2101 <- 0   
    numer_2110 <- 0  ;  numer_2100 <- 0   
    numer_2011 <- 0  ;  numer_2001 <- 0   
    numer_2010 <- 0  ;  numer_2000 <- 0   

    for (id in 1:sample_size)
    {
        print(id)
        data_id <- dt[user_id == id]

        for (dp in 1:total_dec_points) 
        {
            if (dp == 1)
                next
            
            data_id_dp <- data_id[total_dec_point == dp]
            data_id_dp_minus_one <- data_id[total_dec_point == (dp - 1)]

            Y_tplusone <- data_id_dp$Y
            Xt <- data_id_dp$X
            A_tminusone <- data_id_dp_minus_one$A
            A_t <- data_id_dp$A

            # X_t, A_tminusone, A_t
            denom_111 <- denom_111 + as.numeric((Xt == 1) & (A_tminusone == 1) & (A_t == 1))
            denom_110 <- denom_110 + as.numeric((Xt == 1) & (A_tminusone == 1) & (A_t == 0))
            denom_011 <- denom_011 + as.numeric((Xt == 0) & (A_tminusone == 1) & (A_t == 1))
            denom_010 <- denom_010 + as.numeric((Xt == 0) & (A_tminusone == 1) & (A_t == 0))
            denom_101 <- denom_101 + as.numeric((Xt == 1) & (A_tminusone == 0) & (A_t == 1))
            denom_100 <- denom_100 + as.numeric((Xt == 1) & (A_tminusone == 0) & (A_t == 0))
            denom_001 <- denom_001 + as.numeric((Xt == 0) & (A_tminusone == 0) & (A_t == 1))
            denom_000 <- denom_000 + as.numeric((Xt == 0) & (A_tminusone == 0) & (A_t == 0))

            # Y == 1, X == 1
            numer_1111 <- numer_1111 + as.numeric((Y_tplusone == 1) & (Xt == 1) & (A_tminusone == 1) & (A_t == 1))
            numer_1101 <- numer_1101 + as.numeric((Y_tplusone == 1) & (Xt == 1) & (A_tminusone == 0) & (A_t == 1))
            numer_1110 <- numer_1110 + as.numeric((Y_tplusone == 1) & (Xt == 1) & (A_tminusone == 1) & (A_t == 0))
            numer_1100 <- numer_1100 + as.numeric((Y_tplusone == 1) & (Xt == 1) & (A_tminusone == 0) & (A_t == 0))
            
            # Y == 1, X == 0
            numer_1011 <- numer_1011 + as.numeric((Y_tplusone == 1) & (Xt == 0) & (A_tminusone == 1) & (A_t == 1))
            numer_1001 <- numer_1001 + as.numeric((Y_tplusone == 1) & (Xt == 0) & (A_tminusone == 0) & (A_t == 1))
            numer_1010 <- numer_1010 + as.numeric((Y_tplusone == 1) & (Xt == 0) & (A_tminusone == 1) & (A_t == 0))
            numer_1000 <- numer_1000 + as.numeric((Y_tplusone == 1) & (Xt == 0) & (A_tminusone == 0) & (A_t == 0))

            # Y == 2, X == 1
            numer_2111 <- numer_2111 + as.numeric((Y_tplusone == 2) & (Xt == 1) & (A_tminusone == 1) & (A_t == 1))
            numer_2101 <- numer_2101 + as.numeric((Y_tplusone == 2) & (Xt == 1) & (A_tminusone == 0) & (A_t == 1))
            numer_2110 <- numer_2110 + as.numeric((Y_tplusone == 2) & (Xt == 1) & (A_tminusone == 1) & (A_t == 0))
            numer_2100 <- numer_2100 + as.numeric((Y_tplusone == 2) & (Xt == 1) & (A_tminusone == 0) & (A_t == 0))

            # Y == 2, X == 0
            numer_2011 <- numer_2011 + as.numeric((Y_tplusone == 2) & (Xt == 0) & (A_tminusone == 1) & (A_t == 1))
            numer_2001 <- numer_2001 + as.numeric((Y_tplusone == 2) & (Xt == 0) & (A_tminusone == 0) & (A_t == 1))
            numer_2010 <- numer_2010 + as.numeric((Y_tplusone == 2) & (Xt == 0) & (A_tminusone == 1) & (A_t == 0))
            numer_2000 <- numer_2000 + as.numeric((Y_tplusone == 2) & (Xt == 0) & (A_tminusone == 0) & (A_t == 0))
        }
    }

    # Test numerically using Y_{tplusone}, i.e., where m = 1. Can test this also with m = 2. 

    numer_11 <- (numer_1111 / denom_111) * 0.2 + (numer_1101 / denom_101) * 0.8
    denom_11 <- (numer_1110 / denom_110) * 0.2 + (numer_1100 / denom_100) * 0.8

    numer_10 <- (numer_1011 / denom_011) * 0.2 + (numer_1001 / denom_001) * 0.8
    denom_10 <- (numer_1010 / denom_010) * 0.2 + (numer_1000 / denom_000) * 0.8

    numer_21 <- (numer_2111 / denom_111) * 0.2 + (numer_2101 / denom_101) * 0.8
    denom_21 <- (numer_2110 / denom_110) * 0.2 + (numer_2100 / denom_100) * 0.8

    numer_20 <- (numer_2011 / denom_011) * 0.2 + (numer_2001 / denom_001) * 0.8
    denom_20 <- (numer_2010 / denom_010) * 0.2 + (numer_2000 / denom_000) * 0.8 

    beta_11_hat <- log(numer_11 / denom_11)
    beta_10_hat <- log(numer_10 / denom_10)
    beta_21_hat <- log(numer_21 / denom_21)
    beta_20_hat <- log(numer_20 / denom_20)

    beta_11_true <- beta_true[1]
    beta_10_true <- beta_true[2]
    beta_21_true <- beta_true[3]
    beta_20_true <- beta_true[4]

    compar_mat <- as.matrix(
        cbind(
            c(beta_11_true, beta_10_true, beta_21_true, beta_20_true), 
            c(beta_11_hat, beta_10_hat, beta_21_hat, beta_20_hat), 
            c(round(beta_11_hat/beta_11_true,3), round(beta_10_hat/beta_10_true,3), 
              round(beta_21_hat/beta_21_true,3), round(beta_20_hat/beta_20_true,3))
            )
        )

    colnames(compar_mat) <- c("true", "numerically", "ratio")
    print(compar_mat)
}





    # nm <- c('sim_1', 'sim_2', 'sim_3', 'sim_4', 'sim_5', 'sim_6', 'sim_7', 'sim_8', 'sim_9', 'sim_10')
    # estimates %>% 
    #   dplyr::mutate(mean_beta_est = rowMeans(select(., sim_1, sim_2, sim_3, sim_4, sim_5, sim_6, sim_7, sim_8, sim_9, sim_10)), 
    #                 sd_beta_est   = rowSds(as.matrix(.[nm]))) %>% 
    #   dplyr::select(ss, beta_true, mean_beta_est, sd_beta_est)
      

#          ss    beta_true  mean_beta_est sd_beta_est
# beta_10  100       0.3    0.73219574    0.06095904
# beta_11  100       0.1    0.09799466    0.04211833
# beta_20  100       0.4    0.94608234    0.08053777
# beta_21  100       0.2    0.20721341    0.05663128
# beta_10  200       0.3    0.74613585    0.04551376
# beta_11  200       0.1    0.10560195    0.03663264
# beta_20  200       0.4    0.93510711    0.04058724
# beta_21  200       0.2    0.15905888    0.03080495
# beta_10  300       0.3    0.75336714    0.04295278
# beta_11  300       0.1    0.08078576    0.03384844
# beta_20  300       0.4    0.94704583    0.05041064
# beta_21  300       0.2    0.18009016    0.05773039