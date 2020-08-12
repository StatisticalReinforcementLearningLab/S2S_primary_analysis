# Sense2stop Micro-Randomized Trial Primary Analysis

[https://clinicaltrials.gov/ct2/show/NCT03184389](https://clinicaltrials.gov/ct2/show/NCT03184389)

## 0. About Sense2Stop 

The aim of this research is to build systems that can recognize when people 
are stressed and then provide them with relaxation prompts in the moment 
to reduce their likelihood of being stressed, smoking, or overeating in 
the near future. This should help smokers be more effective in their 
attempts to quit by reducing their tendency to lapse when they are 
stressed or experiencing other negative moods or behaviors.

The Sense2Stop study evaluates whether an app and worn sensors can help 
smokers quit smoking and not relapse.

## 1. About This Repository

This repository contains code for performing analysis of the Sense2stop MRT 
data and documentation. Files corresponding to particular stages of the project 
are placed under the relevant header.

## 2. Documentation

### 2.1 Code: Creating Data Frames

- [create_activity_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_activity_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/activity_df.pkl`, a cleaned dataset corresponding to the classification of 
physical activity. 
- [create_log_dicts.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_log_dicts.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/log_dict.pkl`, a cleaned dataset corresponding to the phone log files, specifically at randomization times. 
- [create_quality_ecg_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_quality_ecg_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/quality_ecg_df.pkl`, a cleaned dataset corresponding to ECG quality. 
- [create_quality_rep_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_quality_rep_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/quality_rep_df.pkl`, a cleaned dataset corresponding to REP quality.
- [create_stress_episode_classification_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_stress_episode_classification_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/stress_episode_classification_df.pkl`, a cleaned dataset corresponding to stress episode classification.

### 2.2 Code: Missing Data

- [show_missing_data.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/show_missing_data.py) is a Python script used to 
show the extent of the missing data in the primary outcome. In addition, this script creates 
a data frame that is used to run one of the covariate analyses in order to predict missing 
episodes within the primary outcome. 

### 2.3 Notes

- [ema_emi_randomization_algorithm.pdf](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/ema_emi_randomization_algorithm.pdf)

- [Exploratory_Analyses.pdf](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/Exploratory_Analyses.pdf)

## 3. Primary Analysis

### 3.1 Missing Data 

- The file [Missing_Data_in_Sense2Stop.pdf](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/Missing_Data_in_Sense2Stop.pdf) provides detail on 
the missing data within the Sense2Stop MRT. 

### 3.2 Covariate Analysis 

Detailed documentation for these analyses is provided in [Covariate_Analyses.pdf](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/Covariate_Analyses.pdf).

### 3.3 Primary Analysis Method
- []

## 4. References 

- [Sarker, H., Tyburski, M., Rahman, M.M., Hovsepian, K., Sharmin, M., Epstein, D.H., Preston, K.L., Furr-Holden, C.D., Milam, A., Nahum-Shani, I. and Al'Absi, M., 2016, May. Finding significant stress episodes in a discontinuous time series of rapidly varying mobile sensor data. In Proceedings of the 2016 CHI conference on human factors in computing systems (pp. 4489-4501). ACM.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5207658/pdf/nihms835269.pdf)

- [Hovsepian, K., al'Absi, M., Ertin, E., Kamarck, T., Nakajima, M. and Kumar, S., 2015, September. cStress: towards a gold standard for continuous stress assessment in the mobile environment. In Proceedings of the 2015 ACM international joint conference on pervasive and ubiquitous computing (pp. 493-504). ACM.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4631393/pdf/nihms728674.pdf)

- [Liao, P., Dempsey, W., Sarker, H., Hossain, S.M., Al'Absi, M., Klasnja, P. and Murphy, S., 2018. Just-in-Time but Not Too Much: Determining Treatment Timing in Mobile Health. Proceedings of the ACM on interactive, mobile, wearable and ubiquitous technologies, 2(4), p.179.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6380673/pdf/nihms-1004611.pdf)