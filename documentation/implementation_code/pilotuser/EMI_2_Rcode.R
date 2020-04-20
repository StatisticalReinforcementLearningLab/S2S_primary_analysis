# Clean
rm(list=ls())

# Library
library(xlsx)
library(stringr)

# working directory
setwd("~/Dropbox/Cui/2nd user/")

# Input data
# dat <- read.csv("~/Dropbox/Cui/2nd user/EMI_2.csv", header=FALSE)
# save(dat, file="EMI_2.RData")
# dat <- dat[-1, ]
load("EMI_2.RData")
dim(dat) # 

# Step 1: find "status"=>"SCHEDULED" under EMI
loc1 <- apply(dat, 1, function(x) x[2]== "'{\"status\": \"SCHEDULED\"" &
                x[5]==" \"id\": \"EMI\"" )
table(loc1)
# FALSE  TRUE 
# 4208   511 
loc_emi_sch <- as.numeric(which(loc1==TRUE)) # 511

# Step 2: extract each schedule
emi_list <- list()
lth <- NULL
rows <- NULL
for(i in 1:length(loc_emi_sch)){
  print(i)
  start <- loc_emi_sch[i]
  if(i!=length(loc_emi_sch)){
    end <- loc_emi_sch[i+1]-1
  }else{
    end <- dim(dat)[1]
  }
  emi_list[[i]] <- dat[start:end, ]
  rows <- c(rows, rownames(emi_list[[i]])[1])
  lth <- c(lth, dim(emi_list[[i]])[1])
}


# Step 3: Extract all informations
cdlist <- levels(dat[, 7])[2:19]
res <- data.frame(matrix(NA, nrow=length(emi_list), ncol=(length(cdlist)+2)))
colnames(res) <- c("Time", as.character(cdlist), "Availability")
res2 <- data.frame(matrix(NA, nrow=length(emi_list), ncol=12))
for(i in 1:length(emi_list)){
  print(i)
  n <- dim(emi_list[[i]])[1]
  res[i, 1] <- as.numeric(str_sub(emi_list[[i]][1, 4], 15, 27))
  j=2
  while(j<=n){
    loc <- which(cdlist == emi_list[[i]][j, 7])
    allcheck <- str_detect(as.character(emi_list[[i]][j, 5]), " all conditions okay")
    if(allcheck==FALSE){
      res[i, (loc+1)] <- str_detect(as.character(emi_list[[i]][j, 5]), "true")
      if(res[i, (loc+1)] == FALSE){
        j <- 1000
      }
      j <- j+1
      res[i, (length(cdlist)+2)] <- FALSE
    }else{
      res[i, (length(cdlist)+2)] <- TRUE
      if(j<n){
        checkinfo <- str_detect(as.character(emi_list[[i]][(j+1), 5]),"G" )
        if(checkinfo == TRUE){
          print("~~~~~")
          print(i)
          res2[i, ] <- as.matrix(emi_list[[i]][(j+1), c(4:6, 8:16)])
        }
      }
      j <- 1000
    }
  }
}

results <- cbind(rows, res, res2)
colnames(results)[1] <- "rowNumber"

save(results, file="results.RData")
write.xlsx(results, file="results.xlsx")

