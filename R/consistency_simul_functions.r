

compute_result_beta <- function(beta_true, beta, beta_se, moderator_vars, control_vars, significance_level, na.rm = FALSE) 
{
    beta_true_mat <- matrix(0,0,4) 
    for (isim in 1:nsim) 
        beta_true_mat <- rbind(beta_true_mat, beta_true)
    
    p <- length(moderator_vars) + 1
    q <- length(control_vars) + 1
    
    bias <- apply(beta - beta_true_mat, 2, mean)
    sd <- apply(beta, 2, sd)
    rmse <- apply(beta - beta_true_mat, 2, function(v) sqrt(mean(v^2)))
    
    critical_factor <- qnorm(1 - significance_level/2)
    ci_left <- beta - critical_factor * beta_se
    ci_right <- beta + critical_factor * beta_se
    coverage_prob <- apply((ci_left < beta_true_mat) & (ci_right > beta_true_mat), 2, mean)
    
    return(list(bias = bias, sd = sd, rmse = rmse, coverage_prob = coverage_prob))
}

