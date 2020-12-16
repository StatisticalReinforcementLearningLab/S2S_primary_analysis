

library(dplyr)
library(tidyr)
library(data.table)

acc <- read.table("results_simul_100_to_500_acc.txt", header = TRUE)
bias <- read.table("results_simul_100_to_500_bias.txt", header = TRUE)

beta_true <- unique(acc$beta_true)

sims <- c(100,200,300,400,500)
for (ss in sims)
{
    acc_ss <- acc[acc$ss == ss, ]
    beta_est_means <- rowMeans(acc_ss[, -c(1,2)])
    print(paste0("ss: ", ss))
    acc_mat <- cbind(beta_true, beta_est_means, beta_est_means - beta_true)
    colnames(acc_mat) <- c("beta_true", "beta_est", "bias")
    print(acc_mat)

    
}

