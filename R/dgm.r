
# Last changed on: 20th Jan 2021
# Last changed by: Marianne

# set flags: 

test_range_y <- FALSE
analytic_vs_numeric <- FALSE

# # #################################
# num_users <- 100
# num_dec_points <- 100
# num_min_prox <- 120
# c_val <- 1

# pretend that every day is a decision point 
# 100 days 
# 120 minutes after each decision point is the proximal window
#################################

dgm_sam <- function(num_users, num_dec_points, num_min_prox, c_val) 
{
    beta_10 <- -0.5 * c_val 
    beta_11 <- 0.5 * c_val 
    beta_20 <- - c_val
    beta_21 <- c_val

    m_vals <- 1:num_min_prox

    Y <- vector("list", length = num_users)
    X <- vector("list", length = num_users)
    A <- vector("list", length = num_users)

    p_X <- 0.2 
    p_A <- 0.5

    id <- NULL

    p_stress_1 <- vector("list", length = num_users)
    p_phys_1 <- vector("list", length = num_users)
    p_no_stress_1 <- vector("list", length = num_users)

    p_stress_0 <- vector("list", length = num_users)
    p_phys_0 <- vector("list", length = num_users)
    p_no_stress_0 <- vector("list", length = num_users)

    for (i in 1:num_users) 
    {
        # print(paste0("i: ", i))

        X[[i]] <- extraDistr::rbern(n = num_dec_points, prob = p_X)
        A[[i]] <- extraDistr::rbern(n = num_dec_points, prob = p_A) 

        # p_stress_0_fun <- function(X) { 0.5 * exp(-(m_vals - 1)) * (0.5 * X + 0.25 * (1 - X)) }
        # p_phys_0_fun <- function(X) { 0.5 * exp(-(num_min_prox - m_vals)) * (0.25 * X + 0.5 * (1 - X)) }

        p_stress_0_fun <- function(X) { 0.5 * exp(-(m_vals - 1) / num_min_prox) * (0.5 * X + 0.25 * (1 - X)) }
        p_phys_0_fun <- function(X) { 0.5 * exp(-(num_min_prox - m_vals) / num_min_prox) * (0.25 * X + 0.5 * (1 - X)) }

        p_stress_0[[i]] <- apply(X = as.array(X[[i]]), MARGIN = 1, FUN = p_stress_0_fun)
        p_phys_0[[i]] <- apply(X = as.array(X[[i]]), MARGIN = 1, FUN = p_phys_0_fun)
        p_no_stress_0[[i]] <- 1 - (p_stress_0[[i]] + p_phys_0[[i]])

        exp_beta1 <- exp((beta_10 * X[[i]]) + (beta_11 * (1 - X[[i]])))
        exp_beta2 <- exp((beta_20 * X[[i]]) + (beta_21 * (1 - X[[i]])))

        p_stress_1[[i]] <- p_stress_0[[i]] %*% diag(exp_beta1) 
        p_phys_1[[i]] <- p_phys_0[[i]] %*% diag(exp_beta2)
        p_no_stress_1[[i]] <- 1 - (p_stress_1[[i]] + p_phys_1[[i]])

        cat_fun <- function(A, B, C)
            extraDistr::rcat(n = num_min_prox, p = cbind(A, B, C), labels = c(1,2,3))
    
        Y[[i]] <- sapply(1:num_dec_points, 
            function(t) {
                val_A0 <- as.numeric(cat_fun(p_stress_0[[i]][,t], p_phys_0[[i]][,t], p_no_stress_0[[i]][,t]))
                val_A1 <- as.numeric(cat_fun(p_stress_1[[i]][,t], p_phys_1[[i]][,t], p_no_stress_1[[i]][,t]))
                res <- ((1 - A[[i]][t]) * val_A0) + (A[[i]][t] * val_A1)
            })

        id <- c(id, rep(i, num_dec_points))
    }

    data <- list(
        id = id, 
        Y = Y, 
        X = X, 
        A = A, 
        p_A = p_A, 
        p_X = p_X, 
        beta_10_true = beta_10, 
        beta_11_true = beta_11, 
        beta_20_true = beta_20, 
        beta_21_true = beta_21
    )

    return(data)
}

dgm_trivariate_categorical_covariate <- function(sample_size, total_T, time_window_for_Y) {

    beta_11_true <- 0.1
    beta_10_true <- 0.3
    beta_21_true <- 0.2
    beta_20_true <- 0.4

    prob_a <- 0.2  # randomization probability 

    df_names <- c("user_id", "day", "total_dec_point", "Y", "Y1", "Y2", "Y3", "A", "S", 
                  "prob_Y1", "X", "prob_Y2", "prob_Y3", "prob_A", "M", "I")
    
    data <- data.frame(matrix(NA, nrow = sample_size * total_T, ncol = length(df_names)))
    names(data) <- df_names
    
    data$user_id <- rep(1:sample_size, each = total_T)
    data$total_dec_point <- rep(1:total_T, times = sample_size)
    
    for (i in 1:sample_size)
    {
        row_index <- seq(from=((i-1) * total_T + 1), to = i * total_T)
        
        # compute covariates: 

        data$S[row_index] <- sample(c(0,1,2), total_T, replace = TRUE)
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