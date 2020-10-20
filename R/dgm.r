
# Last changed on: 19th Oct 2020
# Last changed by: Marianne Menictas

# load required libraries:

library(dplyr)
library(data.table)

# set flags: 

test_range_y <- FALSE
analytic_vs_numeric <- TRUE

#############################
# sample_size <- 30
# num_days <- 10
# num_dec_points_per_day <- 3
# time_window_for_Y <- 2
#############################

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

        data$prob_Y1[row_index[1]] <-  NA
        data$prob_Y2[row_index[1]] <-  NA
        data$prob_Y3[row_index[1]] <-  NA

        data$prob_Y1[row_index[2]] <- 0.2 * exp(data$A[1] * (beta_11_true * data$X[1] + beta_10_true * (1 - data$X[1])))
        data$prob_Y2[row_index[2]] <- 0.3 * exp(data$A[1] * (beta_21_true * data$X[1] + beta_20_true * (1 - data$X[1])))
        data$prob_Y3[row_index[2]] <- 1 - (data$prob_Y1[row_index[2]] + data$prob_Y2[row_index[2]])

        t_minus_1 <- row_index[-c(1, total_T)]
        t_minus_2 <- row_index[-c(total_T, total_T-1)]

        data$prob_Y1[row_index[-(1:2)]] <- (0.2 * exp(data$A[t_minus_1] * (beta_11_true * data$X[t_minus_1] + beta_10_true * (1 - data$X[t_minus_1])))
                                                * exp(data$A[t_minus_2] * (beta_11_true * data$X[t_minus_2] + beta_10_true * (1 - data$X[t_minus_2]))))
        data$prob_Y2[row_index[-(1:2)]] <- (0.15 * exp(data$A[t_minus_1] * (beta_21_true * data$X[t_minus_1] + beta_20_true * (1 - data$X[t_minus_1])))
                                                * exp(data$A[t_minus_2] * (beta_21_true * data$X[t_minus_2] + beta_20_true * (1 - data$X[t_minus_2]))))
        data$prob_Y3[row_index[-(1:2)]] <- 1 - (data$prob_Y1[row_index[-(1:2)]] + data$prob_Y2[row_index[-(1:2)]])

        data$Y[row_index[1]] <- NA

        data$Y[row_index[-1]] <- extraDistr::rcat(
            n = total_T - 1, 
            p = cbind(data$prob_Y1[row_index[-1]], data$prob_Y2[row_index[-1]], data$prob_Y3[row_index[-1]]), 
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

    sample_size <- 500 # number of users
    num_days <- 10
    num_dec_points_per_day <- 10
    total_dec_points <- num_days * num_dec_points_per_day

    data_model <- dgm_trivariate_categorical_covariate(sample_size, num_days, num_dec_points_per_day)
    data <- data_model[['data']]
    beta_true <- data_model[['beta_true']]
    dt = as.data.table(data)

    data_0_t <- dt[X == 0 & A == 1]
    data_0_c <- dt[X == 0 & A == 0]
    data_1_t <- dt[X == 1 & A == 1]
    data_1_c <- dt[X == 1 & A == 0]

    exp_beta_10_t_vals <- NULL ; exp_beta_10_c_vals <- NULL 
    exp_beta_11_t_vals <- NULL ; exp_beta_11_c_vals <- NULL 
    exp_beta_20_t_vals <- NULL ; exp_beta_20_c_vals <- NULL
    exp_beta_21_t_vals <- NULL ; exp_beta_21_c_vals <- NULL
    
    for (id in 1:sample_size)
    {
        print(paste0("id: ", id))
        data_id <- dt[user_id == id]

        data_id_10_t <- 0  ;  data_id_10_c <- 0
        data_id_11_t <- 0  ;  data_id_11_c <- 0
        data_id_20_t <- 0  ;  data_id_20_c <- 0
        data_id_21_t <- 0  ;  data_id_21_c <- 0

        data_0_t_id <- data_0_t[user_id == id]
        data_0_c_id <- data_0_c[user_id == id]
        data_1_t_id <- data_1_t[user_id == id]
        data_1_c_id <- data_1_c[user_id == id]

        for (dp in 1:total_dec_points) 
        { 
            if (dp == 1 | dp == total_dec_points | dp == (total_dec_points - 1))
                next

            m_dps <- c(dp + 1, dp + 2)
            Y_dp <- data_id$Y[dp]

            if (Y_dp == 1)
            {
                data_id_10_t <- data_0_t_id[total_dec_point %in% m_dps & Y1 == 1]$Y1
                data_id_10_c <- data_0_c_id[total_dec_point %in% m_dps & Y1 == 1]$Y1
                data_id_11_t <- data_1_t_id[total_dec_point %in% m_dps & Y1 == 1]$Y1
                data_id_11_c <- data_1_c_id[total_dec_point %in% m_dps & Y1 == 1]$Y1

                if (length(data_id_10_t) == 0)
                    data_id_10_t <- rep(0, 2)

                if (length(data_id_10_c) == 0)
                    data_id_10_c <- rep(0, 2)

                if (length(data_id_11_t) == 0)
                    data_id_11_t <- rep(0, 2)

                if (length(data_id_11_c) == 0)
                    data_id_11_c <- rep(0, 2)

                if (length(data_id_10_t) == 1)
                    data_id_10_t <- c(data_id_10_t, 0)

                if (length(data_id_10_c) == 1)
                    data_id_10_c <- c(data_id_10_c, 0)

                if (length(data_id_11_t) == 1)
                    data_id_11_t <- c(data_id_11_t, 0)

                if (length(data_id_11_c) == 1)
                    data_id_11_c <- c(data_id_11_c, 0)
            }

            exp_beta_10_t_vals <- c(exp_beta_10_t_vals, data_id_10_t)
            exp_beta_10_c_vals <- c(exp_beta_10_c_vals, data_id_10_c)
            exp_beta_11_t_vals <- c(exp_beta_11_t_vals, data_id_11_t)
            exp_beta_11_c_vals <- c(exp_beta_11_c_vals, data_id_11_c)

            if (Y_dp == 2)
            {
                data_id_20_t <- data_0_t_id[total_dec_point %in% m_dps & Y2 == 1]$Y2
                data_id_20_c <- data_0_c_id[total_dec_point %in% m_dps & Y2 == 1]$Y2
                data_id_21_t <- data_1_t_id[total_dec_point %in% m_dps & Y2 == 1]$Y2
                data_id_21_c <- data_1_c_id[total_dec_point %in% m_dps & Y2 == 1]$Y2

                if (length(data_id_20_t) == 0)
                    data_id_20_t <- rep(0, 2)

                if (length(data_id_20_c) == 0)
                    data_id_20_c <- rep(0, 2)
                
                if (length(data_id_21_t) == 0)
                    data_id_21_t <- rep(0, 2)

                if (length(data_id_21_c) == 0)
                    data_id_21_c <- rep(0, 2)

                if (length(data_id_20_t) == 1)
                    data_id_20_t <- c(data_id_20_t, 0)

                if (length(data_id_20_c) == 1)
                    data_id_20_c <- c(data_id_20_c, 0)
                
                if (length(data_id_21_t) == 1)
                    data_id_21_t <- c(data_id_21_t, 0)

                if (length(data_id_21_c) == 1)
                    data_id_21_c <- c(data_id_21_c, 0)
            }

            exp_beta_20_t_vals <- c(exp_beta_20_t_vals, data_id_20_t)
            exp_beta_20_c_vals <- c(exp_beta_20_c_vals, data_id_20_c)
            exp_beta_21_t_vals <- c(exp_beta_21_t_vals, data_id_21_t)
            exp_beta_21_c_vals <- c(exp_beta_21_c_vals, data_id_21_c)
        }
    }
    
    exp_beta_10_numer <- mean(exp_beta_10_t_vals)
    exp_beta_10_denom <- mean(exp_beta_10_c_vals)
    exp_beta_11_numer <- mean(exp_beta_11_t_vals)
    exp_beta_11_denom <- mean(exp_beta_11_c_vals)
    exp_beta_20_numer <- mean(exp_beta_20_t_vals)
    exp_beta_20_denom <- mean(exp_beta_20_c_vals)
    exp_beta_21_numer <- mean(exp_beta_21_t_vals)
    exp_beta_21_denom <- mean(exp_beta_21_c_vals)

    beta_10_hat <- log(exp_beta_10_numer / exp_beta_10_denom)
    beta_11_hat <- log(exp_beta_11_numer / exp_beta_11_denom)
    beta_20_hat <- log(exp_beta_20_numer / exp_beta_20_denom)
    beta_21_hat <- log(exp_beta_21_numer / exp_beta_21_denom)

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





