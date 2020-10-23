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
        
        # TQ: revised this to correct subscript and to have initial values
        # So essentially we are setting A_0 = 0, X_0 = 0. Same initial values will be set in the analysis.
        data$prob_Y1[row_index[1]] <-  0.2 * exp(data$A[1] * (beta_11_true * data$X[1] + beta_10_true * (1 - data$X[1])))
        data$prob_Y2[row_index[1]] <-  0.3 * exp(data$A[1] * (beta_21_true * data$X[1] + beta_20_true * (1 - data$X[1])))
        data$prob_Y3[row_index[1]] <-  1 - (data$prob_Y1[row_index[1]] + data$prob_Y2[row_index[1]])
        
        t_minus_1 <- row_index[-total_T]
        
        data$prob_Y1[row_index[-1]] <- (0.2 * exp(data$A[row_index[-1]] * (beta_11_true * data$X[row_index[-1]] + beta_10_true * (1 - data$X[row_index[-1]])))
                                            * exp(data$A[t_minus_1] * (beta_11_true * data$X[t_minus_1] + beta_10_true * (1 - data$X[t_minus_1]))))
        data$prob_Y2[row_index[-1]] <- (0.15 * exp(data$A[row_index[-1]] * (beta_21_true * data$X[row_index[-1]] + beta_20_true * (1 - data$X[row_index[-1]])))
                                            * exp(data$A[t_minus_1] * (beta_21_true * data$X[t_minus_1] + beta_20_true * (1 - data$X[t_minus_1]))))
        data$prob_Y3[row_index[-1]] <- 1 - (data$prob_Y1[row_index[-1]] + data$prob_Y2[row_index[-1]])
        
        data$Y[row_index] <- extraDistr::rcat(
            n = total_T - 1, 
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
