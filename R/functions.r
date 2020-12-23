
compute_result_beta <- function(beta_true, beta, beta_se, moderator_vars, control_vars, significance_level) 
{
    beta_true_mat <- matrix(0,0,4) 
    for (isim in 1:nsim) 
        beta_true_mat <- rbind(beta_true_mat, beta_true)
    
    p <- length(moderator_vars) + 1
    q <- length(control_vars) + 1
    
    bias <- apply(beta - beta_true_mat, 2, mean)
    sd <- apply(beta, 2, sd)
    rmse <- apply(beta - beta_true_mat, 2, function(v) sqrt(mean(v^2)))
    ave_beta_se <- apply(beta_se, 2, mean)
    
    critical_factor <- qnorm(1 - significance_level/2)
    ci_left <- beta - critical_factor * beta_se
    ci_right <- beta + critical_factor * beta_se
    coverage_prob <- apply((ci_left < beta_true_mat) & (ci_right > beta_true_mat), 2, mean)

    beta_10_true <- beta_true[1]
    beta_11_true <- beta_true[2]
    beta_20_true <- beta_true[3]
    beta_21_true <- beta_true[4]

    compar_mat <- c(beta_10_true, beta_11_true, beta_20_true, beta_21_true)
    for (isim in 1:nsim) 
        compar_mat <- cbind(compar_mat, beta[isim, ])

    compar_mat <- cbind(rep(sample_size, 4), compar_mat)

    colnames_vec <- c("ss", "beta_true")
    for (isim in 1:nsim) 
         colnames_vec <- c(colnames_vec, paste0("sim_", isim))

    colnames(compar_mat) <- colnames_vec
    rownames(compar_mat) <- NULL
    
    return(list(bias = bias, sd=sd, ave_beta_se=ave_beta_se, rmse = rmse, coverage_prob = coverage_prob, compar_mat = compar_mat))
}

estimating_equation_missingness <- function(theta, num_users, num_dec_points, ncol_Z, A, M, I, W, X, p_x, Zdm) 
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
