
# Last changed on: 2nd Mar 2021
# Last changed by: Marianne 

# set flags: 

useSimpleModel <- FALSE
useSAMdgm <- FALSE 
useNonConstDgm <- !useSAMdgm

# load required libraries and files:

library(foreach)
library(doMC)
library(doRNG)
library(data.table)
library(rootSolve) 

source("dgm.r")
source("functions.r")

if (useSimpleModel)
{
    source("estimator_simple.r")
    num_min_prox_val <- 120
    c_val <- 1
}

if (!useSimpleModel)
{
    source("estimator_complex.r")
    num_min_prox_val <- 120
    c_val <- 1
}

max_cores <- 16
registerDoMC(min(detectCores() - 1, max_cores))

sample_sizes <- c(25, 50, 75)
num_dec_points <- 50
nsim <- 100

result_df_collected <- data.frame()
compar_mat <- data.frame()

for (i_ss in 1:length(sample_sizes)) 
{
    sample_size <- sample_sizes[i_ss]
    print(paste0("sample_size: ", sample_size))

    result <- list() 
    for (isim in 1:nsim) 
    {
        print(paste0("   isim: ", isim))

        set.seed(i_ss * isim)
        I <- NULL

        if (!useSimpleModel)
        {
            M <- NULL 

            if (useSAMdgm)
            {
                dgm <- dgm_sam(
                    num_users = sample_size, 
                    num_dec_points = num_dec_points, 
                    num_min_prox = num_min_prox_val, 
                    c_val = c_val
                )
        
                beta_true <- c(dgm[['beta_10_true']], 
                               dgm[['beta_11_true']], 
                               dgm[['beta_20_true']], 
                               dgm[['beta_21_true']])

                fit_e <- estimating_equation_dgm_sam(
                    dta = dgm, 
                    M = M, 
                    I = I, 
                    num_min_prox = num_min_prox_val, 
                    num_users = sample_size, 
                    num_dec_points = num_dec_points
                )
            }

            if (useNonConstDgm)
            {
                dgm <- dgm_sam_non_const_rand(
                    num_users = sample_size, 
                    num_dec_points = num_dec_points, 
                    num_min_prox = num_min_prox_val, 
                    c_val = c_val
                )
        
                beta_true <- c(dgm[['beta_10_true']], 
                               dgm[['beta_11_true']], 
                               dgm[['beta_20_true']], 
                               dgm[['beta_21_true']])

                fit_e <- estimating_equation_dgm_sam(
                    dta = dgm, 
                    M = M, 
                    I = I, 
                    num_min_prox = num_min_prox_val, 
                    num_users = sample_size, 
                    num_dec_points = num_dec_points
                )
            }
        }
        
        if (useSimpleModel)
        {
            dgm <- dgm_sam(
                    num_users = sample_size, 
                    num_dec_points = num_dec_points, 
                    num_min_prox = num_min_prox_val, 
                    c_val = c_val
                )
        
            beta_true <- c(dgm[['beta_10_true']], 
                           dgm[['beta_11_true']], 
                           dgm[['beta_20_true']], 
                           dgm[['beta_21_true']])

            fit_e <- estimating_equation_simple(
                dta = dgm, 
                I = I, 
                num_min_prox = num_min_prox_val, 
                num_users = sample_size, 
                num_dec_points = num_dec_points
            )
        }
        
        result[isim] <- list(fit_e = fit_e)
    }

    beta_hat_mat <- matrix(0, 0, 4) 
    colnames(beta_hat_mat) <- c("beta_10", "beta_11", "beta_20", "beta_21")
    for (isim in 1:nsim) 
        beta_hat_mat <- rbind(beta_hat_mat, as.vector(result[[isim]]$beta_hat))

    beta_hat_se_mat <- matrix(0, 0, 4) 
    colnames(beta_hat_se_mat) <- c("beta_10", "beta_11", "beta_20", "beta_21")
    for (isim in 1:nsim) 
        beta_hat_se_mat <- rbind(beta_hat_se_mat, as.vector(result[[isim]]$beta_se))

    beta_10_true <- beta_true[1]
    beta_11_true <- beta_true[2]
    beta_20_true <- beta_true[3]
    beta_21_true <- beta_true[4]

    beta_true <- c(beta_10_true, beta_11_true, beta_20_true, beta_21_true)

    beta_hat <- beta_hat_mat
    beta_hat_se <- beta_hat_se_mat

    result <- compute_result_beta(
        beta_true, beta_hat, 
        beta_hat_se, 
        moderator_vars = "X", 
        control_vars = "S", 
        significance_level = 0.05
    )

    result_df <- data.frame(ss = rep(sample_size, 1),
                            bias = result$bias,
                            sd = result$sd,
                            se = result$ave_beta_se,
                            rmse = result$rmse,
                            cp = result$coverage_prob)

    names(result_df) <- c("ss", "bias", "sd", "se", "rmse", "cp")
    rownames(result_df) <- NULL
    
    result_df_collected <- rbind(result_df_collected, result_df)
    compar_mat <- rbind(compar_mat, as.data.frame(result$compar_mat))

    if (sample_size == sample_sizes[length(sample_sizes)])
    {
        print(result_df_collected)
        print(compar_mat)
    }
}
