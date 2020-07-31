# Sense2stop Primary Analysis




## Documentation



### Missing Data 
- The file [Missing_Data_in_Sense2Stop.pdf ](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/Missing_Data_in_Sense2Stop.pdf) provides details on 
the missing data within the Sense2Stop MRT. 

### Primary Analysis Method
- [Supplementary file (Overleaf)](https://www.overleaf.com/4334158856hfhxpnmvcphz)

### Covariate Analysis 

Two sets of analyses were conducted to decide on the final set of covariates for 
inclusion in the primary analysis: 

- [Data analysis for justification of MAR (Python)]()
- [Creating data frame for MAR data analysis (Python)]()

Detailed documentation for these analyses is provided in [Covariate_Analyses.pdf](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/pdf_files/Covariate_Analyses.pdf)



## Code 

### Creating Data Frames: 

- [create_activity_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_activity_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/activity_df.pkl`, a cleaned dataset corresponding to the classification of 
physical activity. 
- [create_log_dicts.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_log_dicts.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/log_dict.pkl`, a cleaned dataset corresponding to the phone log files, specifically at randomization times. 
- [create_quality_ecg_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_quality_ecg_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/quality_ecg_df.pkl`, a cleaned dataset corresponding to ECG quality. 
- [create_quality_rep_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_quality_rep_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/quality_rep_df.pkl`, a cleaned dataset corresponding to REP quality.
- [create_stress_episode_classification_df.py](https://github.com/StatisticalReinforcementLearningLab/S2S_primary_analysis/blob/master/Python/create_stress_episode_classification_df.py) is a Python script used to create `~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/stress_episode_classification_df.pkl`, a cleaned dataset corresponding to stress episode classification.

### Covariate Analyses:

- 
