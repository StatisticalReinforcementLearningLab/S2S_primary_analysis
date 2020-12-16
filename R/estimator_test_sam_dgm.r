
# Last changed on: 29th Nov 2020
# Last changed by: Marianne 

# load required libraries:

library(rootSolve) # for solver function multiroot()

########################################################
# source("dgm.r")

# num_users <- 25
# num_dec_points <- 100
# num_min_prox <- 120 

# set.seed(12323)

# dta <- dgm_sam(num_users, num_dec_points, num_min_prox, c_val = 1)
# M <- NULL
# I <- NULL
########################################################

estimating_equation_dgm_sam <- function(dta, M = NULL, I = NULL, num_min_prox = 120, num_users, num_dec_points) {
    
    ### 1. preparation ###

    Y <- dta$Y
    X <- dta$X
    A <- dta$A
    p_A <- dta$p_A 
    p_X <- dta$p_X

    idVec <- dta$id

    X_arrow <- vector("list", length = num_users)
    Xdm <- vector("list", length = num_users) 
    Ldm <- vector("list", length = num_users) 
    Zdm <- vector("list", length = num_users) 
    g_M_Zdm <- vector("list", length = num_users) 
    g_Y_Zdm <- vector("list", length = num_users) 
    for (i in 1:num_users)
    {
        X_arrow[[i]] <- cbind(X[[i]], 1 - X[[i]]) 
        Xdm[[i]] <- X[[i]]
        Ldm[[i]] <- rep(1, num_dec_points)
        Zdm[[i]] <- rep(1, num_dec_points)
        g_M_Zdm[[i]] <- Zdm[[i]]
        g_Y_Zdm[[i]] <- Ldm[[i]]
    }

    if (is.null(I)) { 

        I <- vector("list", length = num_users) 
        for (i in 1:num_users)
            I[[i]] <- rep(1, num_dec_points)
    }
    
    ncol_X <- 1 # dimension of beta_1 and beta_2
    ncol_L <- 1 # dimension of alpha_1 and alpha_2
    ncol_Z <- 1 # dimension of xi and eta.

    # Set dimensions 
    q <- 1
    dim_rho <- 2 
    dim_eta <- q 
    dim_xi <- q 
    dim_alpha <- 2 * q
    dim_beta <- 4 

    if (is.null(M)) {
        
        M <- vector("list", length = num_users) 
        for (i in 1:num_users)
            M[[i]] <- matrix(rep(1, num_dec_points * num_min_prox), num_min_prox, num_dec_points)
    }
    
    ### 2. estimation ###

    # 2.1 Step 1: Form the marginalization weights:

    Mvec <- unlist(M)
    Ivec <- unlist(I)
    Avec <- unlist(A)
    Xvec <- unlist(X)
    X_arrow_vec <- do.call(rbind, X_arrow)
    Xdm_vec <- unlist(Xdm)
    Ldm_vec <- unlist(Ldm)
    Zdm_vec <- unlist(Zdm)
    g_M_Zdm_vec <- unlist(g_M_Zdm)
    g_Y_Zdm_vec <- unlist(g_Y_Zdm)

    prob_A <- rep(p_A, length(Avec))

    p_x0 <- mean(sum(Ivec * as.numeric(Xvec == 0) * prob_A)) / mean(sum(Ivec * as.numeric(Xvec == 0)))
    p_x1 <- mean(sum(Ivec * as.numeric(Xvec == 1) * prob_A)) / mean(sum(Ivec * as.numeric(Xvec == 1)))
    p_x <- c(p_x0, p_x1)

    p_X <- unlist(lapply(Xvec, function(i){p_x[i+1]}))
    init_weight_val <- ((p_X / prob_A)^{Avec}) * (((1 - p_X) / (1 - prob_A))^{1 - Avec}) 

    # W <- vector("list", length = num_users)
    # Wvec <- NULL
    # for (i in 1:num_users)
    # {
    #     init_weight_val_id <- init_weight_val[idVec == i]
    #     for (t in 1:num_dec_points)
    #     {
    #         A_id_m <- as.numeric(A[[i]][t:(t + num_min_prox - 1)] %>% na.omit)
    #         if (length(A_id_m) > 0) {
    #             W[[i]] <- c(W[[i]], init_weight_val_id[t] * sum(as.numeric(A_id_m == 0)/(1 - p_A)))
    #         }
    #         else {
    #             W[[i]] <- c(W[[i]], init_weight_val_id[t])
    #         }
    #     }
    #     Wvec <- c(Wvec, W[[i]])
    # }

    # assume that A_{t} is once every day and the A_{t+m} are all zero for the next 
    # 120 minutes:

    Wvec <- init_weight_val
    W <- vector("list", length = num_users)
    for (i in 1:num_users) 
        W[[i]] <- Wvec[idVec == i]

    # 2.2 Step 2: Estimating the Missingness Mechanism:

    estimating_equation_missingness <- function(theta) 
    {
        eta <- theta[1:ncol_Z]
        xi <- theta[(ncol_Z+1):(2 * ncol_Z)]

        eem_val_id <- NULL
        for (i in 1:num_users)
        {
            eem_val <- NULL 
            exp_AZEta_i <- exp(-A[[i]] * (Zdm[[i]] * eta))
            exp_ZXi_i <- exp(Zdm[[i]] * xi)
            
            for (t in 1:num_dec_points)
            {
                Zdm_id_t <- Zdm[[i]][t]
                eem_val_t <- (sum(I[[i]][t] * W[[i]][t]
                              * (exp_AZEta_i[t] * M[[i]][,t] - exp_ZXi_i[t]))
                              * c(Zdm_id_t, (A[[i]][t] - p_x[X[[i]][t] + 1]) * Zdm_id_t))
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

    xi_hat <- as.vector(solution_missingness$root[1:dim_xi])
    eta_hat <- as.vector(solution_missingness$root[(dim_xi+1):(dim_xi+dim_eta)])

    exp_ZXi_AZEta <- NULL
    for (i in 1:num_users)
        exp_ZXi_AZEta[[i]] <- as.vector(exp(-(Zdm[[i]] * xi_hat) - (A[[i]] * (Zdm[[i]] * eta_hat))))
    
    # 2.3 Step 3: Estimating beta, the Parameter of Interest:

    Rtm <- function(alpha, beta, k, A, X, Y, L) 
    { 
        alpha <- alpha[k]
        beta <- beta[(k * 2 - 1) : (k * 2)]

        ans <- (exp(- A * ((X * beta[2]) + ((1 - X) * beta[1]))) * as.numeric(Y == k) 
                - as.numeric(exp(L * alpha)))

        return(ans)
    }

    U_func_id <- function(alpha, beta, i) 
    { 
        I_id <- I[[i]]
        W_id <- W[[i]] 
        A_id <- A[[i]] 
        X_id <- X[[i]]
        M_id <- M[[i]]
        Y_id <- Y[[i]]
        Ldm_id <- Ldm[[i]]
        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[[i]]

        eeb_val <- NULL 
        for (t in 1:num_dec_points)
        {            
            I_id_t <- I_id[t]
            W_id_t <- W_id[t]
            M_id_t <- M_id[, t]
            A_id_t <- A_id[t]
            X_id_t <- X_id[t]
            Y_id_t <- Y_id[, t]
            Ldm_id_t <- Ldm_id[t]

            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            eeb_val_t <- c(sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t
                               * Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * Ldm_id_t), 
                           sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t 
                               * Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * Ldm_id_t), 
                           sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t 
                               * Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * (A_id_t  - p_x[X_id_t + 1]) * X_id_t), 
                           sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t 
                               * Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * (A_id_t  - p_x[X_id_t + 1]) * (1 - X_id_t)),
                           sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t 
                               * Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * (A_id_t  - p_x[X_id_t + 1]) * X_id_t),
                           sum(I_id_t * W_id_t * exp_ZXi_AZEta_id_t * M_id_t 
                               * Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t) * (A_id_t  - p_x[X_id_t + 1]) * (1 - X_id_t)))

            eeb_val <- cbind(eeb_val, eeb_val_t)
        }
        return(eeb_val)
    }
    
    ###############
    # estimate rho:
    ###############

    U_N_id <- function(rho_0, rho_1, i) 
    {
        val1 <- sum(I[[i]] * as.numeric(X[[i]] == 0) * (p_A - rho_0))
        val2 <- sum(I[[i]] * as.numeric(X[[i]] == 1) * (p_A - rho_1))
        
        return(c(val1, val2))
    }

    estimating_equation_rho <- function(rho)
    {
        rho_0 <- rho[1]
        rho_1 <- rho[2]

        val1_id <- NULL  ;  val2_id <- NULL
        for (id in 1:num_users)
        {
            U_N_id_val <- U_N_id(rho_0=rho_0, rho_1=rho_1, i=id) 
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
        alpha <- theta[1:dim_alpha]
        beta <- theta[(dim_alpha + 1):(dim_alpha + dim_beta)]

        eeb_val_id <- NULL
        for (id in 1:num_users)
        {   
            eeb_val <- U_func_id(alpha=alpha, beta=beta, i=id) 
            eeb_val_id <- cbind(eeb_val_id, rowSums(eeb_val))
        }
        eeb_val_final <- apply(eeb_val_id, 1, mean)

        return(eeb_val_final)
    }

    estimator_initial_value <- rep(0, length = dim_alpha + dim_beta)

    solution_beta <- tryCatch(
        {
            multiroot(estimating_equation_beta, estimator_initial_value)
        },
        error = function(cond) 
        {
            message("\nCaught error in multiroot inside estimating_equation_beta():")
            message(cond)
            return(list(root = rep(NaN, dim_beta + dim_alpha), msg = cond, f.root = rep(NaN, dim_beta + dim_alpha)))
        }
    )

    alpha_hat <- as.vector(solution_beta$root[1:dim_alpha])
    beta_hat <- as.vector(solution_beta$root[(dim_alpha+1):(dim_alpha+dim_beta)])

    ##################################
    ### Variance-Covariance Estimation 
    ##################################

    U_M_id <- function(eta, xi, i) 
    {
        U_M_id_val <- NULL

        W_id <- W[[i]]
        I_id <- I[[i]]
        M_id <- M[[i]]
        X_id <- X[[i]]
        A_id <- A[[i]] 

        Zdm_id <- Zdm[[i]]
        g_M_Zdm_id <- g_M_Zdm[[i]]
        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[[i]]

        U_M_id_val <- 0
        for (t in 1:num_dec_points)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[, t]
            W_id_t <- W_id[t]
            A_id_t <- A_id[t]

            Zdm_id_t <- Zdm_id[t]
            g_M_Zdm_id_t <- g_M_Zdm_id[t]

            exp_AZEta_id_t <- as.vector(exp(-A_id_t * (Zdm_id_t * eta)))
            exp_gMZxi_id_t <- as.vector(exp(g_M_Zdm_id_t * xi))
            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            U_M_id_t <- (sum(I_id_t * W_id_t * (exp_AZEta_id_t * M_id_t - exp_gMZxi_id_t)) * 
                         c(g_M_Zdm_id_t, (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t))

            U_M_id_val <- U_M_id_val + U_M_id_t
        }
        return(U_M_id_val)
    }

    U_1_id <- function(alpha, beta, eta, xi, i) 
    {
        W_id <- W[[i]]
        I_id <- I[[i]]
        M_id <- M[[i]]
        X_id <- X[[i]]
        A_id <- A[[i]] 
        Y_id <- Y[[i]]

        Zdm_id <- Zdm[[i]]
        Ldm_id <- Ldm[[i]]
        g_M_Zdm_id <- g_M_Zdm[[i]]
        g_Y_Zdm_id <- g_Y_Zdm[[i]]
        X_id_arrow <- X_arrow[[i]]

        exp_ZXi_AZEta_id <- exp_ZXi_AZEta[[i]]

        U_1_id_val <- 0
        for (t in 1:num_dec_points)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[, t]
            X_id_t <- X_id[t]
            W_id_t <- W_id[t]
            A_id_t <- A_id[t]
            Y_id_t <- Y_id[, t]
            exp_ZXi_AZEta_id_t <- exp_ZXi_AZEta_id[t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])

            Zdm_id_t <- Zdm_id[t]
            Ldm_id_t <- Ldm_id[t]
            g_M_Zdm_id_t <- g_M_Zdm_id[t]
            g_Y_Zdm_id_t <- g_Y_Zdm_id[t]

            exp_gMZxiAZEta_id_t <- as.vector(exp(- g_M_Zdm_id_t * xi - A_id_t * (Zdm_id_t * eta)))

            D_t <- rbind(cbind(g_Y_Zdm_id_t, matrix(0,q,1)), 
                         cbind(matrix(0,q,1), g_Y_Zdm_id_t), 
                         cbind((A_id_t - p_x[X_id_t + 1]) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_x[X_id_t + 1]) * X_id_t_arrow))

            U_1_id_t <- D_t %*% rbind(sum(I_id_t * W_id_t * exp_gMZxiAZEta_id_t * M_id_t * Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t)), 
                                      sum(I_id_t * W_id_t * exp_gMZxiAZEta_id_t * M_id_t * Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t)))

            U_1_id_val <- U_1_id_val + U_1_id_t
        }
        return(U_1_id_val)
    }

    U_id <- function(alpha, beta, eta, xi, rho, id) 
    {
        rho_0 <- rho[1]  ;  rho_1 <- rho[2]
        U_id_val <- c(U_N_id(rho_0=rho_0, rho_1=rho_1, i=id), 
                      U_M_id(eta=eta, xi=xi, i=id), 
                      U_1_id(alpha=alpha, beta=beta, eta=eta, xi=xi, i=id)
                     )
        return(U_id_val)
    }

    # Define Sigman: 
    
    Sigman_id_list <- list()
    for (id in 1:num_users)
    {
        U_func_id_val <- U_id(alpha_hat, beta_hat, eta_hat, xi_hat, rho_hat, id) 
        Sigman_id_list[[id]] <- tcrossprod(U_func_id_val)
    }
    Sigman <- apply(simplify2array(Sigman_id_list), 1:2, mean)

    # Define Vn: 

    exp_AZEta <- NULL 
    exp_gMZXi <- NULL
    exp_gMZXi_AZEta <- NULL
    for (i in 1:num_users){
        exp_AZEta[[i]] <- as.vector(exp(-A[[i]] * (Zdm[[i]] * eta_hat)))
        exp_gMZXi[[i]] <- as.vector(exp(g_M_Zdm[[i]] * xi_hat))
        exp_gMZXi_AZEta[[i]] <- as.vector(exp(- (g_M_Zdm[[i]] * xi_hat) - (A[[i]] * (Zdm[[i]] * eta_hat))))
    }
   
    beta_hat_1 <- beta_hat[1:2]
    beta_hat_2 <- beta_hat[3:4]
    
    exp_AXarrowBeta1 <- NULL 
    exp_AXarrowBeta2 <- NULL
    for (i in 1:num_users)
    {
        exp_AXarrowBeta1[[i]] <- as.vector(exp(-A[[i]] * (X_arrow[[i]] %*% beta_hat_1)))
        exp_AXarrowBeta2[[i]] <- as.vector(exp(-A[[i]] * (X_arrow[[i]] %*% beta_hat_2)))
    }

    alpha_hat_1 <- alpha_hat[1]
    alpha_hat_2 <- alpha_hat[2]

    Vn_list <- list()
    for (i in 1:num_users)
    {
        I_id <- I[[i]]
        X_id <- X[[i]]
        A_id <- A[[i]] 
        Y_id <- Y[[i]]
        M_id <- M[[i]]
        W_id <- W[[i]]
        
        exp_AZEta_id <- exp_AZEta[[i]]
        exp_gMZXi_id <- exp_gMZXi[[i]]
        exp_gMZXi_AZEta_id <- exp_gMZXi_AZEta[[i]]
        exp_AXarrowBeta1_id <- exp_AXarrowBeta1[[i]]
        exp_AXarrowBeta2_id <- exp_AXarrowBeta2[[i]]
        X_id_arrow <- X_arrow[[i]]

        g_Y_Zdm_id <- g_Y_Zdm[[i]]
        g_M_Zdm_id <- g_M_Zdm[[i]]
        
        Zdm_id <- Zdm[[i]]
        Ldm_id <- Ldm[[i]]

        V21 <- 0  ;  V22 <- 0  ;  V23 <- 0
        V31 <- 0  ;  V32 <- 0  ;  V33 <- 0  ;  V34 <- 0  ;  V35 <- 0
        for (t in 1:num_dec_points)
        {
            I_id_t <- I_id[t]
            M_id_t <- M_id[,t]
            W_id_t <- W_id[t]
            X_id_t <- X_id[t]
            A_id_t <- A_id[t]
            Y_id_t <- Y_id[,t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])

            exp_AZEta_id_t <- exp_AZEta_id[t]
            exp_gMZXi_id_t <- exp_gMZXi_id[t]
            exp_gMZXi_AZEta_id_t <- exp_gMZXi_AZEta_id[t]
            exp_AXarrowBeta1_id_t <- exp_AXarrowBeta1_id[t]
            exp_AXarrowBeta2_id_t <- exp_AXarrowBeta2_id[t]

            Zdm_id_t <- Zdm_id[t]
            Ldm_id_t <- Ldm_id[t]

            g_Y_Zdm_id_t <- g_Y_Zdm_id[t]
            g_M_Zdm_id_t <- g_M_Zdm_id[t]

            exp_gMZxi_id_t <- as.vector(exp(g_M_Zdm_id_t * xi_hat))
            exp_gYZalpha1_id_t <- as.vector(exp(g_Y_Zdm_id_t * alpha_hat_1))
            exp_gYZalpha2_id_t <- as.vector(exp(g_Y_Zdm_id_t * alpha_hat_2))

            frac_val <- (2 * A_id_t - 1)/((p_x[X_id_t + 1]^A_id_t) * 
                        (1 - p_x[X_id_t + 1])^(1 - A_id_t))

            D_t <- rbind(cbind(g_Y_Zdm_id_t, matrix(0,q,1)), 
                         cbind(matrix(0,q,1), g_Y_Zdm_id_t), 
                         cbind((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow))

            V21_const <- sum(I_id_t * W_id_t * (exp_AZEta_id_t * M_id_t - exp_gMZXi_id_t))

            V21 <- V21 + rbind(V21_const * frac_val * g_M_Zdm_id_t, 
                               V21_const * (frac_val * (A_id_t - p_x[X_id[t] + 1]) - 1) * Zdm_id_t) %*% X_id_t_arrow

            V22 <- V22 + rbind(- I_id_t * W_id_t * exp_gMZXi_id_t * g_M_Zdm_id_t * g_M_Zdm_id_t, 
                               - I_id_t * W_id_t * exp_gMZXi_id_t * (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t * g_M_Zdm_id_t)
            
            V23 <- V23 + rbind(- I_id_t * W_id_t * exp_AZEta_id_t * sum(M_id_t) * g_M_Zdm_id_t * A_id_t * Zdm_id_t, 
                               - I_id_t * W_id_t * exp_AZEta_id_t * sum(M_id_t) * (A_id_t - p_x[X_id[t] + 1]) * Zdm_id_t * A_id_t * Zdm_id_t)

            V3_const <- I_id_t * W_id_t * exp_gMZXi_AZEta_id_t * M_id_t 
            R1tm_val <- Rtm(alpha_hat, beta_hat, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t)
            R2tm_val <- Rtm(alpha_hat, beta_hat, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t)

            V31 <- V31 + (D_t %*% tcrossprod(rbind(sum(V3_const * frac_val * R1tm_val), 
                                                   sum(V3_const * frac_val * R2tm_val)), X_id_t_arrow)
                         + rbind(matrix(0,q,2), 
                                 matrix(0,q,2), 
                                 sum(- V3_const * R1tm_val) * tcrossprod(X_id_t_arrow), 
                                 sum(- V3_const * R2tm_val) * tcrossprod(X_id_t_arrow)))

            V3_vec <- c(sum(V3_const * R1tm_val) * g_Y_Zdm_id_t, 
                        sum(V3_const * R2tm_val) * g_Y_Zdm_id_t, 
                        sum(V3_const * R1tm_val) * (A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, 
                        sum(V3_const * R2tm_val) * (A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow)

            V32 <- V32 - V3_vec * g_M_Zdm_id_t
            V33 <- V33 - V3_vec * A_id_t * Zdm_id_t

            V34 <- V34 + (sum(V3_const) * 
                    rbind(cbind(- exp_gYZalpha1_id_t * as.numeric(tcrossprod(g_Y_Zdm_id_t)), matrix(0, q, q)),
                            cbind(matrix(0, q, q), - exp_gYZalpha2_id_t * tcrossprod(g_Y_Zdm_id_t)), 
                            cbind(- exp_gYZalpha1_id_t * as.numeric(tcrossprod((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, g_Y_Zdm_id_t)), matrix(0, 2, q)),
                            cbind(matrix(0, 2, q), - exp_gYZalpha2_id_t * as.numeric(tcrossprod((A_id_t - p_x[X_id[t] + 1]) * X_id_t_arrow, g_Y_Zdm_id_t)))))

            expY1AtTerm <- sum(V3_const * (-exp_AXarrowBeta1_id_t) * as.numeric(Y_id_t == 1) * A_id_t)
            expY2AtTerm <- sum(V3_const * (-exp_AXarrowBeta2_id_t) * as.numeric(Y_id_t == 2) * A_id_t)

            V35 <- V35 + rbind(cbind(expY1AtTerm * g_Y_Zdm_id_t * t(X_id_t_arrow), 
                                     matrix(0, q, 2)), 
                               cbind(matrix(0, q, 2), 
                                     expY2AtTerm * g_Y_Zdm_id_t * t(X_id_t_arrow)), 
                               cbind(expY1AtTerm * (A_id_t - p_x[X_id[t] + 1]) * tcrossprod(X_id_t_arrow), 
                                     matrix(0, 2, 2)), 
                               cbind(matrix(0, 2, 2), 
                                     expY2AtTerm * (A_id_t - p_x[X_id[t] + 1]) * tcrossprod(X_id_t_arrow)))
        }

        V11_11 <- - sum(I_id * as.numeric(X_id == 0))
        V11_22 <- - sum(I_id * as.numeric(X_id == 1))
        V11 <- cbind(c(V11_11, 0), c(0, V11_22))

        Vn_list[[i]] <- rbind(cbind(V11, matrix(0, 2, 4 * q + 4)), 
                               cbind(V21, V22, V23, matrix(0, 2 * q, 2 * q + 4)),
                               cbind(V31, V32, V33, V34, V35))
    }
    Vn <- apply(simplify2array(Vn_list), 1:2, mean)

    Vn_inv <- solve(Vn)
    varcov <- Vn_inv %*% Sigman %*% t(Vn_inv) / num_users
    beta_se <- sqrt(diag(varcov)[7:10])
    
    ### 6. return the result with variable names ###
    
    names(beta_hat) <- names(beta_se) <- c("beta_01", "beta_11", "beta_02", "beta_12")

    return(list(beta_hat = beta_hat,
                beta_se = beta_se,
                varcov = varcov))
}

