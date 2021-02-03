
# Last changed on: 2nd Feb 2021
# Last changed by: Marianne 

library(rootSolve) # for solver function multiroot()
source("functions.r")

#######################################################
# source("dgm.r")

# num_users <- 25
# num_dec_points <- 15
# num_min_prox <- 120 

# set.seed(12323)

# dta <- dgm_sam(
#     num_users, 
#     num_dec_points, 
#     num_min_prox, 
#     c_val = 1
# )
# I <- NULL
########################################################

estimating_equation_simple <- function(
    dta, 
    I = NULL, 
    num_min_prox = 120, 
    num_users, 
    num_dec_points) {
    
    ### 1. preparation ###

    Y <- dta$Y
    X <- dta$X
    A <- dta$A
    p_A <- dta$p_A

    X_arrow <- vector("list", length = num_users)
    Ldm <- vector("list", length = num_users) 
    for (i in 1:num_users)
    {
        X_arrow[[i]] <- cbind(X[[i]], 1 - X[[i]]) 
        Ldm[[i]] <- cbind(rep(1, num_dec_points), X[[i]])
    }
    
    if (is.null(I)) { 

        I <- vector("list", length = num_users) 
        for (i in 1:num_users)
            I[[i]] <- rep(1, num_dec_points)
    }

    # Set dimensions 
    q <- ncol(Ldm[[1]])
    dim_alpha <- 2 * q
    dim_beta <- 4
    
    ### 2. estimation ###

    Avec <- unlist(A)
    Xvec <- unlist(X)
    X_arrow_mat <- do.call(rbind, X_arrow)
    Ldm_vec <- unlist(Ldm)

    # 2.3 Step 3: Estimating beta, the Parameter of Interest:

    Rtm <- function(alpha, beta, k, A, X, Y, L) 
    { 
        alpha_k <- alpha[(k * 2 - 1) : (k * 2)]
        beta_k <- beta[(k * 2 - 1) : (k * 2)]

        ans <- (exp(- A * ((X * beta_k[1]) + ((1 - X) * beta_k[2]))) * as.numeric(Y == k) 
                - as.numeric(exp(L %*% alpha_k)))

        return(ans)
    }

    U_1_id <- function(alpha, beta, i) 
    {
        X_id <- X[[i]]
        A_id <- A[[i]] 
        Y_id <- Y[[i]]
        I_id <- I[[i]]
        Ldm_id <- Ldm[[i]]
        X_id_arrow <- X_arrow[[i]]

        U_1_id_val <- 0
        for (t in 1:num_dec_points)
        {
            X_id_t <- X_id[t]
            A_id_t <- A_id[t]
            Y_id_t <- Y_id[, t]
            I_id_t <- I_id[t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])
            Ldm_id_t <- Ldm_id[t,]

            D_t <- rbind(cbind(Ldm_id_t, matrix(0,q,1)), 
                         cbind(matrix(0,q,1), Ldm_id_t), 
                         cbind((A_id_t - p_A) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_A) * X_id_t_arrow))

            U_1_id_t <- D_t %*% rbind(sum(I_id_t * Rtm(alpha, beta, 1, A_id_t, X_id_t, Y_id_t, Ldm_id_t)), 
                                      sum(I_id_t * Rtm(alpha, beta, 2, A_id_t, X_id_t, Y_id_t, Ldm_id_t)))

            U_1_id_val <- U_1_id_val + U_1_id_t
        }
        return(U_1_id_val)
    }

    ###############
    # estimate beta:
    ###############

    estimating_equation_beta <- function(theta) 
    {
        alpha <- theta[1:dim_alpha]
        beta <- theta[(dim_alpha + 1):(dim_alpha + dim_beta)]

        eeb_val_id <- NULL
        for (id in 1:num_users)
            eeb_val_id <- cbind(eeb_val_id, U_1_id(alpha=alpha, beta=beta, i=id))

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

    # Define Sigman: 
    
    Sigman_id_list <- list()
    for (id in 1:num_users)
        Sigman_id_list[[id]] <- tcrossprod(U_1_id(alpha_hat, beta_hat, id))

    Sigman <- apply(simplify2array(Sigman_id_list), 1:2, mean)

    # Define Vn: 
   
    beta_hat_1 <- beta_hat[1:2]
    beta_hat_2 <- beta_hat[3:4]
    
    alpha_hat_1 <- alpha_hat[1:2]
    alpha_hat_2 <- alpha_hat[3:4]

    Vn_list <- list()
    for (i in 1:num_users)
    {
        I_id <- I[[i]]
        X_id <- X[[i]]
        A_id <- A[[i]] 
        Y_id <- Y[[i]]

        X_id_arrow <- X_arrow[[i]]
        Ldm_id <- Ldm[[i]]

        Vn_list[[i]] <- 0
        for (t in 1:num_dec_points)
        {
            I_id_t <- I_id[t]
            X_id_t <- X_id[t]
            A_id_t <- A_id[t]
            Y_id_t <- Y_id[,t]

            X_id_t_arrow <- as.vector(X_id_arrow[t,])
            Ldm_id_t <- Ldm_id[t,]

            D_t <- rbind(cbind(Ldm_id_t, matrix(0,q,1)), 
                         cbind(matrix(0,q,1), Ldm_id_t), 
                         cbind((A_id_t - p_A) * X_id_t_arrow, matrix(0,2,1)), 
                         cbind(matrix(0,2,1), (A_id_t - p_A) * X_id_t_arrow))

            V11 <- as.vector(- 120 * exp(Ldm_id_t %*% alpha_hat_1) %*% Ldm_id_t)
            V13 <- - as.numeric(exp(- A_id_t * (X_id_t_arrow %*% beta_hat_1))) * sum(as.numeric(Y_id_t == 1)) * A_id_t * X_id_t_arrow
            V22 <- as.vector(- 120 * exp(Ldm_id_t %*% alpha_hat_2) %*% Ldm_id_t)
            V24 <- - as.numeric(exp(- A_id_t * (X_id_t_arrow %*% beta_hat_2))) * sum(as.numeric(Y_id_t == 2)) * A_id_t * X_id_t_arrow

            Vn_list[[i]] <- Vn_list[[i]] + I_id_t * D_t %*% rbind(c(V11, matrix(0, 1, q), V13, matrix(0, 1, 2)), 
                                                                  c(matrix(0, 1, q), V22, matrix(0, 1, 2), V24))
        }     
    }
    Vn <- apply(simplify2array(Vn_list), 1:2, mean)

    Vn_inv <- solve(Vn)
    varcov <- Vn_inv %*% Sigman %*% t(Vn_inv) / num_users
    beta_se <- sqrt(diag(varcov)[5:8])
    
    ### 6. return the result with variable names ###
    
    names(beta_hat) <- names(beta_se) <- c("beta_10", "beta_11", "beta_20", "beta_21")

    return(list(beta_hat = beta_hat,
                beta_se = beta_se,
                varcov = varcov))
}

