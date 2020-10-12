
# Last changed on: 12th Oct 2020
# Last changed by: Marianne Menictas

# load required libraries and files:

source("dgm.r")
source("estimator.r")
library(foreach)
library(doMC)
library(doRNG)

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

data_generating_process <- dgm_trivariate_categorical_covariate

max_cores <- 16
registerDoMC(min(detectCores() - 1, max_cores))

sample_sizes <- c(30, 50, 100)
num_days <- 10
num_dec_points_per_day <- 3
nsim <- 2  #1000

control_vars <- "S"
moderator_vars <- "X"
miss_at_rand_varnames <- "S"

result_df_collected <- data.frame()

for (i_ss in 1:length(sample_sizes)) {
    
    sample_size <- sample_sizes[i_ss]

    result <- list() 
    for (isim in 1:nsim) 
    {
        dta <- data_generating_process(sample_size, num_days, num_dec_points_per_day)
         
        fit_e <- estimating_equation(
            dta = dta,
            time_window_for_Y = 1,
            id_varname = "user_id",
            decision_time_varname = "total_dec_point",
            treatment_varname = "A",
            outcome_varname = "Y",
            control_varname = control_vars,
            miss_at_rand_varname = miss_at_rand_varnames,
            moderator_varname = moderator_vars,
            rand_prob_varname = "prob_A",
            avail_varname = "I", 
            missing_varname = "M"
        )
        result[isim] <- list(fit_e = fit_e)
    }

    alpha_hat_mat <- matrix(0,0,4) 
    colnames(alpha_hat_mat) <- c("alpha_11", "alpha_12", "alpha_21", "alpha_22")
    for (isim in 1:nsim) 
    {
        alpha_hat_mat <- rbind(alpha_hat_mat, as.vector(result[[isim]]$alpha_hat))
    }

    alpha_hat_se_mat <- matrix(0,0,4) 
    colnames(alpha_hat_se_mat) <- c("alpha_11", "alpha_12", "alpha_21", "alpha_22")
    for (isim in 1:nsim) 
    {
        alpha_hat_se_mat <- rbind(alpha_hat_se_mat, as.vector(result[[isim]]$alpha_se))
    }

    beta_hat_mat <- matrix(0,0,4) 
    colnames(beta_hat_mat) <- c("beta_10", "beta_11", "beta_20", "beta_21")
    for (isim in 1:nsim) 
    {
        beta_hat_mat <- rbind(beta_hat_mat, as.vector(result[[isim]]$beta_hat))
    }

    beta_hat_se_mat <- matrix(0,0,4) 
    colnames(beta_hat_se_mat) <- c("beta_10", "beta_11", "beta_20", "beta_21")
    for (isim in 1:nsim) 
    {
        beta_hat_se_mat <- rbind(beta_hat_se_mat, as.vector(result[[isim]]$beta_se))
    }
    
    beta_11_true <- 0.1
    beta_10_true <- 0.6 
    beta_21_true <- 0.2
    beta_20_true <- 0.6

    beta_true_marginal <- c(beta_11_true, beta_10_true, beta_21_true, beta_20_true)

    beta_true <- beta_true_marginal
    beta <- beta_hat_mat
    beta_se <- beta_hat_se_mat
    alpha <- alpha_hat_mat
    alpha_se <- alpha_hat_se_mat

    result <- compute_result_beta(beta_true_marginal, beta, beta_se, moderator_vars, control_vars, significance_level = 0.05)

    result_df <- data.frame(ss = rep(sample_size, 1),
                            bias = result$bias,
                            sd = result$sd,
                            rmse = result$rmse,
                            cp = result$coverage_prob)

    names(result_df) <- c("ss", "bias", "sd", "rmse", "cp")
    rownames(result_df) <- NULL
    
    result_df_collected <- rbind(result_df_collected, result_df)
}