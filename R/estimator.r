
# Last changed on: 25th Oct 2020
# Last changed by: Marianne Menictas

# load required libraries:

library(rootSolve) # for solver function multiroot()

# ##################################################
# dta <- dta
# time_window_for_Y <- 2
# id_varname <- "user_id"
# decision_time_varname <- "total_dec_point"
# treatment_varname <- "A"
# outcome_varname <- "Y"
# control_varname <- control_vars
# miss_at_rand_varname <- miss_at_rand_varnames
# moderator_varname <- moderator_vars
# rand_prob_varname <- "prob_A"
# avail_varname <- NULL
# missing_varname <- NULL
##################################################

estimating_equation <- function(
    dta,
    time_window_for_Y = 2,
    id_varname,
    decision_time_varname,
    treatment_varname,
    outcome_varname,
    control_varname,
    miss_at_rand_varname,
    moderator_varname,
    rand_prob_varname,
    avail_varname = NULL,
    missing_varname = NULL
)
{
    ### 1. preparation ###

    sample_size <- length(unique(dta[, id_varname]))
    dps_per_id <- nrow(dta[dta$user_id == 1, ])
    total_dps <- nrow(dta)
    
    X <- dta[, moderator_varname]
    A <- dta[, treatment_varname]
    prob_A <- dta[, rand_prob_varname]
    Y <- dta[, outcome_varname]
    X_arrow <- cbind(X, 1 - X)

    Xdm <- as.matrix(dta[, moderator_varname]) # X (moderator) design matrix, intercept added
    Ldm <- as.matrix(cbind(dta[, moderator_varname], dta[, control_varname])) # L (control) design matrix, intercept added
    Zdm <- as.matrix(cbind(dta[, moderator_varname], dta[, miss_at_rand_varname])) # Z (missing at random) design matrix, intercept added

    g_M_Zdm <- Zdm
    g_Y_Zdm <- Ldm

    if (is.null(avail_varname)) { 
        I <- rep(1, total_dps)
        dta$I <- I
    } else {
        I <- dta[, avail_varname]
    }

    if (is.null(missing_varname)) {
        M <- rep(1, total_dps)
        dta$M <- M
    } else { 
        M <- dta[, missing_varname]
    }
    
    ncol_X <- length(moderator_varname) + 1 # dimension of beta_1 and beta_2
    ncol_L <- length(control_varname) + 1 # dimension of alpha_1 and alpha_2
    ncol_Z <- length(miss_at_rand_varname) + 1 # dimension of xi and eta.
    
    ### 2. estimation ###

    # 2.1 Step 1: Form the marginalization weights:

    p_x0 <- mean(sum(I * as.numeric(X == 0) * A)) / mean(sum(I * as.numeric(X == 0)))
    p_x1 <- mean(sum(I * as.numeric(X == 1) * A)) / mean(sum(I * as.numeric(X == 1)))
    p_x <- c(p_x0, p_x1)

    p_X <- unlist(lapply(X, function(i){p_x[i+1]}))
    init_weight_val <- ((p_X / prob_A)^{A}) * (((1 - p_X) / (1 - prob_A))^{1 - A}) 

    weight <- NULL
    for (id in 1:sample_size)
    {
        id_inds <- dta$user_id == id
        dta_id <- dta[id_inds,]
        init_weight_val_id <- init_weight_val[id_inds]
        for (t in 1:dps_per_id)
        {
            dta_id_m <- dta_id[t:(t+time_window_for_Y-1),] %>% na.omit
            if (nrow(dta_id_m) > 0) {
                weight <- c(weight, init_weight_val_id[t] * sum(as.numeric(dta_id_m$A == 0)/(1 - dta_id_m$prob_A)))
            }
            else {
                weight <- c(weight, init_weight_val_id[t])
            }
        }
    }

    dta$W <- weight

    # 2.2 Step 2: Estimating the Missingness Mechanism:

    estimating_equation_missingness <- function(theta) 
    {
        eta <- theta[1:ncol_Z]
        xi <- theta[(ncol_Z+1):(2 * ncol_Z)]

        exp_AZEta <- as.vector(exp(-A * (Zdm %*% eta)))
        exp_ZXi <- as.vector(exp(Zdm %*% xi))

        eem_val_id <- NULL
        for (id in 1:sample_size)
        {
            eem_val <- NULL 
            dta_id <- dta[dta$user_id == id,]
            W_id <- dta_id$W
            I_id <- dta_id$I
            M_id <- dta_id$M
            X_id <- dta_id$X
            A_id <- dta_id$A 

            exp_AZEta_id <- exp_AZEta[dta$user_id == id]
            exp_ZXi_id <- exp_ZXi[dta$user_id == id]
            
            Zdm_id <- Zdm[dta$user_id == id,]
            for (t in 1:dps_per_id)
            {
                I_id_t <- I_id[t]
                M_id_t <- M_id[t]
                W_id_t <- W_id[t]
                exp_AZEta_id_t <- exp_AZEta_id[t]
                exp_ZXi_id_t <- exp_ZXi_id[t]
                Zdm_id_t <- Zdm_id[t,]

                M_id_t_plus_m <- M_id[t:(t+time_window_for_Y-1)] %>% na.omit
                if (length(M_id_t_plus_m) > 0) 
                    eem_val_t <-  (I_id_t * W_id_t 
                       * (exp_AZEta_id_t * sum(M_id_t_plus_m) - exp_ZXi_id_t) 
                       * c(Zdm_id_t, (A_id[t] - p_x[X_id[t] + 1]) * Zdm_id_t))

                if (length(M_id_t_plus_m) == 0)
                    next

                eem_val <- cbind(eem_val, eem_val_t)
            }
            eem_val_id <- cbind(eem_val_id, rowSums(eem_val))
        }
        eem_val_final <- apply(eem_val_id, 1, mean)
        return(eem_val_final)
    }
    
    estimator_initial_value <- rep(0, length = 2 * ncol_Z)

    solution_missingness <- tryCatch(
        {
            multiroot(estimating_equation_missingness, estimator_initial_value)
        },
        error = function(cond) 
        {
            message("\nCaught error in multiroot inside estimating_equation_missingness():")
            message(cond)
            return(list(root = rep(NaN, 2 * ncol_Z), msg = cond, f.root = rep(NaN, 2 * ncol_Z)))
        }
    )
    
    xi_hat <- as.vector(solution_missingness$root[1:ncol_Z])
    eta_hat <- as.vector(solution_missingness$root[(ncol_Z+1):(2 * ncol_Z)])

    exp_ZXi_AZEta <- as.vector(exp(- (Zdm %*% xi_hat) - (A * (Zdm %*% eta_hat))))
    
    # 2.3 Step 3: Estimating beta, the Parameter of Interest:

    beta_dim <- 2 * ncol_X
    alpha_dim <- 2 * ncol_L

    Rtm <- function(alpha, beta, k, A, X, Y, L) 
    { 
        alpha <- alpha[(k * 2 - 1) : (k * 2)]
        beta <- beta[(k * 2 - 1) : (k * 2)]

        ans <- (exp(- A * (X * beta[2] + (1 - X) * beta[1])) * as.numeric(Y == k) 
                - as.numeric(exp(L %*% alpha)))

        return(ans)
    }

    U_func_id <- function(data, alpha, beta, id) 
    { 
        eeb_val <- NULL 
        dta_id <- data[data$user_id == id,]
        W_id <- dta_id$W
        I_id <- dta_id$I
        M_id <- dta_id$M
        X_id <- dta_id$X
        A_id <- dta_id$A 
        Y_id <- dta_id$Y

        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[data$user_id == id]

        Ldm_id <- Ldm[data$user_id == id,]

        for (t in 1:dps_per_id)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[t]
            W_id_t <- W_id[t]
            X_id_t <- X_id[t]
            A_id_t <- A_id[t]

            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            Ldm_id_t <- Ldm_id[t,]

            M_id_t_plus_m <- M_id[t:(t+time_window_for_Y-1)] %>% na.omit
            Y_t_plus_m <- Y_id[t:(t+time_window_for_Y-1)] %>% na.omit

            if (length(M_id_t_plus_m) > 0) 
                eeb_val_t <- (I_id_t * W_id_t * exp_ZXi_AZEta_id_t * sum(M_id_t_plus_m)
                    * c(sum(Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t, 
                        sum(Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t,  
                        sum(Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t,     
                        sum(Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * (1 - X_id_t),
                        sum(Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t,   
                        sum(Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * (1 - X_id_t)))
            
            if (length(M_id_t_plus_m) == 0)
                next 

            eeb_val <- cbind(eeb_val, eeb_val_t)
        }
        return(eeb_val)
    }
    
    ###############
    # estimate rho:
    ###############

    U_N_id <- function(data, rho_0, rho_1, id) 
    {
        dta_id <- data[data$user_id == id,]
        I_id <- dta_id$I
        X_id <- dta_id$X
        prob_A_id <- dta_id$prob_A

        val1 <- sum(I_id * as.numeric(X_id == 0) * (prob_A_id - rho_0))
        val2 <- sum(I_id * as.numeric(X_id == 1) * (prob_A_id - rho_1))
        
        return(c(val1, val2))
    }

    estimating_equation_rho <- function(rho)
    {
        rho_0 <- rho[1]
        rho_1 <- rho[2]

        val1_id <- NULL  ;  val2_id <- NULL
        for (id in 1:sample_size)
        {
            U_N_id_val <- U_N_id(dta, rho_0, rho_1, id) 
            val1_id <- c(val1_id, U_N_id_val[1])
            val2_id <- c(val2_id, U_N_id_val[2])
        }
        val1_final <- mean(val1_id)
        val2_final <- mean(val2_id)

        return(c(val1_final, val2_final))
    }

    solution_rho <- tryCatch(
        {
            multiroot(estimating_equation_rho, rep(0, length = 2))
        },
        error = function(cond) 
        {
            message("\nCaught error in multiroot inside estimating_equation_rho():")
            message(cond)
            return(list(root = rep(NaN, 2), msg = cond, f.root = rep(NaN, 2)))
        }
    )

    rho_hat <- as.vector(solution_rho$root)

    ###############
    # estimate beta:
    ###############

    estimating_equation_beta <- function(theta) 
    {
        alpha <- theta[1:alpha_dim]
        beta <- theta[(alpha_dim + 1):(beta_dim + alpha_dim)]

        eeb_val_id <- NULL
        for (id in 1:sample_size)
        {   
            eeb_val <- U_func_id(dta, alpha, beta, id) 
            eeb_val_id <- cbind(eeb_val_id, rowSums(eeb_val))
        }
        eeb_val_final <- apply(eeb_val_id, 1, mean)

        return(eeb_val_final)
    }

    estimator_initial_value <- rep(0, length = beta_dim + alpha_dim)

    solution_beta <- tryCatch(
        {
            multiroot(estimating_equation_beta, estimator_initial_value)
        },
        error = function(cond) 
        {
            message("\nCaught error in multiroot inside estimating_equation_beta():")
            message(cond)
            return(list(root = rep(NaN, beta_dim + alpha_dim), msg = cond, f.root = rep(NaN, beta_dim + alpha_dim)))
        }
    )

    alpha_hat <- as.vector(solution_beta$root[1:alpha_dim])
    beta_hat <- as.vector(solution_beta$root[(alpha_dim+1):(alpha_dim+beta_dim)])

    ##################################
    ### Variance-Covariance Estimation 
    ##################################

    U_M_id <- function(data, eta, xi) 
    {
        U_M_id_val <- NULL

        dta_id <- data[data$user_id == id,]
        W_id <- dta_id$W
        I_id <- dta_id$I
        M_id <- dta_id$M
        X_id <- dta_id$X
        A_id <- dta_id$A 

        Zdm_id <- Zdm[data$user_id == id,]
        g_M_Zdm_id <- g_M_Zdm[data$user_id == id,]
        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[data$user_id == id]

        U_M_id_val <- 0
        for (t in 1:dps_per_id)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[t]
            W_id_t <- W_id[t]
            A_id_t <- A_id[t]

            Zdm_id_t <- Zdm_id[t,]
            g_M_Zdm_id_t <- g_M_Zdm_id[t,]

            exp_AZEta_id_t <- as.vector(exp(-A_id_t * (Zdm_id_t %*% eta)))
            exp_gMZxi_id_t <- as.vector(exp(g_M_Zdm_id_t %*% xi))
            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            M_id_t_plus_m <- M_id[t:(t+time_window_for_Y-1)] %>% na.omit

            if (length(M_id_t_plus_m) > 0) 
                U_M_id_t <- (I_id_t * W_id_t * (exp_AZEta_id_t * sum(M_id_t_plus_m) - exp_gMZxi_id_t) * 
                              c(g_M_Zdm_id_t, (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t))
            
            if (length(M_id_t_plus_m) == 0)
                next 

            U_M_id_val <- U_M_id_val + U_M_id_t
        }
        return(U_M_id_val)
    }

    U_1_id <- function(data, alpha, beta, eta, xi) 
    {
        dta_id <- data[data$user_id == id,]
        W_id <- dta_id$W
        I_id <- dta_id$I
        M_id <- dta_id$M
        X_id <- dta_id$X
        A_id <- dta_id$A 
        Y_id <- dta_id$Y

        Zdm_id <- Zdm[data$user_id == id,]
        Ldm_id <- Ldm[data$user_id == id,]
        g_M_Zdm_id <- g_M_Zdm[data$user_id == id,]
        g_Y_Zdm_id <- g_Y_Zdm[data$user_id == id,]
        X_id_arrow <- X_arrow[data$user_id == id,]

        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[data$user_id == id]

        U_1_id_val <- 0
        for (t in 1:dps_per_id)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[t]
            X_id_t <- X_id[t]
            W_id_t <- W_id[t]
            A_id_t <- A_id[t]
            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])

            Zdm_id_t <- Zdm_id[t,]
            Ldm_id_t <- Ldm_id[t,]
            g_M_Zdm_id_t <- g_M_Zdm_id[t,]
            g_Y_Zdm_id_t <- g_Y_Zdm_id[t,]

            exp_gMZxiAZEta_id_t <- as.vector(exp(- g_M_Zdm_id_t %*% xi - A_id_t * (Zdm_id_t %*% eta)))

            M_id_t_plus_m <- M_id[t:(t+time_window_for_Y-1)] %>% na.omit
            Y_t_plus_m <- Y_id[t:(t+time_window_for_Y-1)] %>% na.omit

            D_t <- rbind(cbind(g_Y_Zdm_id_t, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), g_Y_Zdm_id_t), 
                         cbind((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow))

            if (length(M_id_t_plus_m) > 0) 
                U_1_id_t <- as.vector(I_id_t * W_id_t * exp_gMZxiAZEta_id_t * sum(M_id_t_plus_m) * D_t %*% 
                              c(sum(Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)),
                                sum(Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t))))
            
            if (length(M_id_t_plus_m) == 0)
                next 

            U_1_id_val <- U_1_id_val + U_1_id_t
        }
        return(U_1_id_val)
    }

    U_id <- function(data, alpha, beta, eta, xi, rho, id) 
    {
        rho_0 <- rho[1]  ;  rho_1 <- rho[2]
        U_id_val <- c(U_N_id(data, rho_0, rho_1, id), U_M_id(data, eta, xi), U_1_id(data, alpha, beta, eta, xi))
        return(U_id_val)
    }

    p <- 4  ;  q <- 2

    # Define Sigman: 
    
    Sigman_id_list <- list()
    for (id in 1:sample_size)
    {
        U_func_id_val <- U_id(dta, alpha_hat, beta_hat, eta_hat, xi_hat, rho_hat, id) 
        Sigman_id_list[[id]] <- tcrossprod(U_func_id_val)
    }
    Sigman <- apply(simplify2array(Sigman_id_list), 1:2, mean)

    # Define Vn: 

    exp_AZEta <- as.vector(exp(-A * (Zdm %*% eta_hat)))
    exp_ZXi <- as.vector(exp(Zdm %*% xi_hat))
    exp_gMZXi_AZEta <- as.vector(exp(- (g_M_Zdm %*% xi_hat) - (A * (Zdm %*% eta_hat))))

    beta_hat_1 <- beta_hat[1:2]
    beta_hat_2 <- beta_hat[3:4]

    exp_AXarrowBeta1 <- as.vector(exp(-A * (X_arrow %*% beta_hat_1)))
    exp_AXarrowBeta2 <- as.vector(exp(-A * (X_arrow %*% beta_hat_2)))

    alpha_hat_1 <- alpha_hat[1:2]
    alpha_hat_2 <- alpha_hat[3:4]

    Vn_list <- list()
    for (id in 1:sample_size)
    {
        dta_id <- dta[dta$user_id == id, ]
        I_id <- dta_id$I
        X_id <- dta_id$X
        A_id <- dta_id$A 
        Y_id <- dta_id$Y
        M_id <- dta_id$M
        W_id <- dta_id$W
        
        exp_AZEta_id <- exp_AZEta[dta$user_id == id]
        exp_ZXi_id <- exp_ZXi[dta$user_id == id]
        exp_gMZXi_AZEta_id <- exp_gMZXi_AZEta[dta$user_id == id]
        exp_AXarrowBeta1_id <- exp_AXarrowBeta1[dta$user_id == id]
        exp_AXarrowBeta2_id <- exp_AXarrowBeta2[dta$user_id == id]
        X_id_arrow <- X_arrow[dta$user_id == id,]

        g_Y_Zdm_id <- g_Y_Zdm[dta$user_id == id,]
        g_M_Zdm_id <- g_M_Zdm[dta$user_id == id,]
        
        Zdm_id <- Zdm[dta$user_id == id,]
        Ldm_id <- Ldm[dta$user_id == id,]

        V21 <- 0  ;  V23 <- 0
        V31 <- 0  ;  V32 <- 0  ;  V33 <- 0  ;  V34 <- 0  ;  V35 <- 0
        for (t in 1:dps_per_id)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[t]
            W_id_t <- W_id[t]
            X_id_t <- X_id[t]
            A_id_t <- A_id[t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])

            exp_AZEta_id_t <- exp_AZEta_id[t]
            exp_ZXi_id_t <- exp_ZXi_id[t]
            exp_gMZXi_AZEta_id_t <- exp_gMZXi_AZEta_id[t]
            exp_AXarrowBeta1_id_t <- exp_AXarrowBeta1_id[t]
            exp_AXarrowBeta2_id_t <- exp_AXarrowBeta2_id[t]

            Zdm_id_t <- Zdm_id[t,]
            Ldm_id_t <- Ldm_id[t,]

            g_Y_Zdm_id_t <- g_Y_Zdm_id[t,]
            g_M_Zdm_id_t <- g_M_Zdm_id[t,]

            exp_gMZxi_id_t <- as.vector(exp(g_M_Zdm_id_t %*% xi_hat))
            exp_gYZalpha1_id_t <- as.vector(exp(g_Y_Zdm_id_t %*% alpha_hat_1))
            exp_gYZalpha2_id_t <- as.vector(exp(g_Y_Zdm_id_t %*% alpha_hat_2))

            frac_val <- (2 * A_id_t - 1)/((p_x[X_id[t] + 1]^A_id[t]) * 
                        (1 - p_x[X_id[t] + 1])^(1 - A_id[t]))

            D_t <- rbind(cbind(g_Y_Zdm_id_t, matrix(0,q,1)), 
                         cbind(matrix(0,q,1), g_Y_Zdm_id_t), 
                         cbind((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow))

            M_id_t_plus_m <- M_id[t:(t+time_window_for_Y-1)] %>% na.omit
            Y_t_plus_m <- Y_id[t:(t+time_window_for_Y-1)] %>% na.omit

            if (length(M_id_t_plus_m) > 0)
            {
                V21 <- V21 + (I_id_t * W_id_t 
                       * (exp_AZEta_id_t * sum(M_id_t_plus_m) - exp_ZXi_id_t) * 
                       tcrossprod(c(frac_val * Zdm_id_t, 
                                 (frac_val * (A_id_t - p_x[X_id[t] + 1]) - 1) * Zdm_id_t), 
                               X_id_t_arrow))

                V23 <- V23 + (I_id_t * W_id_t * exp_AZEta_id_t * sum(M_id_t_plus_m) * 
                       tcrossprod(c(Zdm_id_t, (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t), 
                                  - A_id_t * Zdm_id_t))

                V31 <- V31 + (I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                       frac_val * D_t %*% tcrossprod(c(sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)), 
                                                      sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t))), X_id_t_arrow) + 
                              I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                              rbind(matrix(0,q,2), 
                                    matrix(0,q,2), 
                                    - sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * tcrossprod(X_id_t_arrow), 
                                    - sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * tcrossprod(X_id_t_arrow)))

                V32 <- V32 + (I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                       tcrossprod(c(
                            sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t, 
                            sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t,  
                            sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t_arrow,     
                            sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t_arrow), -Zdm_id_t))

                V33 <- V33 + (I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                       tcrossprod(c(
                            sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t, 
                            sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * Ldm_id_t,  
                            sum(Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t_arrow,     
                            sum(Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_t_plus_m, Ldm_id_t)) * (A_id[t] - p_x[X_id[t] + 1]) * X_id_t_arrow), - A_id_t * Zdm_id_t))
                
                V34 <- V34 + (I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                       rbind(cbind(- exp_gYZalpha1_id_t * tcrossprod(g_Y_Zdm_id_t), matrix(0, q, q)),
                             cbind(matrix(0, q, q), - exp_gYZalpha2_id_t * tcrossprod(g_Y_Zdm_id_t)), 
                             cbind(- exp_gYZalpha1_id_t * tcrossprod((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, g_Y_Zdm_id_t), matrix(0, q, q)),
                             cbind(matrix(0, q, q), - exp_gYZalpha2_id_t * tcrossprod((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, g_Y_Zdm_id_t))))
                
                V35 <- V35 + (I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * sum(M_id_t_plus_m) * 
                       rbind(cbind(- exp_AXarrowBeta1_id_t * sum(as.numeric(Y_t_plus_m == 1)) * A_id_t * tcrossprod(g_Y_Zdm_id_t, X_id_t_arrow), matrix(0, q, q)),
                             cbind(matrix(0, q, q), - exp_AXarrowBeta2_id_t * sum(as.numeric(Y_t_plus_m == 2)) * A_id_t * tcrossprod(g_Y_Zdm_id_t, X_id_t_arrow)), 
                             cbind(- exp_AXarrowBeta1_id_t * sum(as.numeric(Y_t_plus_m == 1)) * A_id_t * (A_id_t - p_x[X_id[t] + 1]) * tcrossprod(X_id_t_arrow), matrix(0, q, q)),
                             cbind(matrix(0, q, q), - exp_AXarrowBeta2_id_t * sum(as.numeric(Y_t_plus_m == 2)) * A_id_t * (A_id_t - p_x[X_id[t] + 1]) * tcrossprod(X_id_t_arrow))))
            }

            V22 <- (I_id_t * W_id_t * (-exp_ZXi_id_t) * 
                     tcrossprod(c(g_M_Zdm_id_t, (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t), g_M_Zdm_id_t))
        }

        V11_11 <- - sum(I_id * as.numeric(X_id == 0))
        V11_22 <- - sum(I_id * as.numeric(X_id == 1))
        V11 <- cbind(c(V11_11, 0), c(0, V11_22))

        Vn_list[[id]] <- rbind(cbind(V11, matrix(0, 2, 4 * q + 4)), 
                               cbind(V21, V22, V23, matrix(0, 2 * q, 2 * q + 4)),
                               cbind(V31, V32, V33, V34, V35))
    }
    Vn <- apply(simplify2array(Vn_list), 1:2, mean)

    Vn_inv <- solve(Vn)
    varcov <- Vn_inv %*% Sigman %*% t(Vn_inv) / sample_size
    alpha_se <- sqrt(diag(varcov)[1:q])
    beta_se <- sqrt(diag(varcov)[(q+1):(q+p)])
    
    ### 6. return the result with variable names ###
    
    names(alpha_hat) <- names(alpha_se) <- c("Intercept", "S")
    names(beta_hat) <- names(beta_se) <- c("beta_11", "beta_12", "beta_21", "beta_22")

    return(list(beta_hat = beta_hat, alpha_hat = alpha_hat,
                beta_se = beta_se, alpha_se = alpha_se,
                varcov = varcov,
                dims = list(p = p, q = q),
                f.root = solution_beta$f.root))
}

