import numpy as np
import pandas as pd
from scipy import stats
from dfply import *

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
# import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV
from treeinterpreter import treeinterpreter as ti

h = .02  # step size in the mesh

# bring in data:
data = pd.read_csv("predict_missing_logistic_df.csv")
del data['Unnamed: 0']

# add baseline covariates to data set:

baseline = pd.read_csv("~/Desktop/baseline.csv")

df = pd.DataFrame(columns=['id', 'day', 'day_num', 'available_decision_point', 
       'available_decision_point_stress_episode', 'episode_type_miss',
       'episode_type_stress', 'episode_type_no_stress', 'episode_length', 'previous_episode_miss',
       'previous_episode_stress', 'previous_episode_no_stress', 'previous_episode_length',
       'prev_day_activity_prop', 'prev_day_bad_qual_rep_prop',
       'prev_day_bad_qual_ecg_prop', 'num_ints_trig_prev_day', 'day1_bmi',
       'sex', 'age', 'age_smoke', 'fagerstromtotal'])

id_list = list(data['id'].unique())
# re-code id with integers:
id_count = 1
for id in id_list:
    df_to_append = data[data['id'] == id]
    len_df_to_append = df_to_append.shape[0]
    baseline_id = baseline[baseline['study_id'] == id]
    df_to_append['day1_bmi'] = [float(baseline_id['day1_bmi'])]*len_df_to_append
    df_to_append['sex'] = [int(baseline_id['sex'])]*len_df_to_append
    df_to_append['age'] = [int(baseline_id['age'])]*len_df_to_append
    df_to_append['age_smoke'] = [float(baseline_id['age_smoke'])]*len_df_to_append
    df_to_append['fagerstromtotal'] = [float(baseline_id['fagerstromtotal'])]*len_df_to_append
    df_to_append['id'] = [id_count]*len_df_to_append
    df = df.append(df_to_append)
    id_count = id_count + 1

df = df.reset_index(drop=True)

# remove outliers from data:

numeric_cols = ['episode_length', 'previous_episode_length', 'prev_day_activity_prop',
  'prev_day_bad_qual_rep_prop', 'prev_day_bad_qual_ecg_prop', 'prev_day_bad_qual_ecg_prop',
  'num_ints_trig_prev_day', 'day1_bmi', 'sex', 'age', 'age_smoke', 'fagerstromtotal']
indices_to_remove = []
for numeric_col in numeric_cols:
    inds = df.index[np.abs(stats.zscore(df[numeric_col])) >= 3].tolist()
    indices_to_remove = indices_to_remove + inds

data_removed_outliers = df.drop(df.index[indices_to_remove])

def get_part_of_day(hour):
    return (
        "morning" if 5 <= hour <= 11
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening" if 18 <= hour <= 22
        else
        "night")

del data_removed_outliers['day']

# data_removed_outliers['episode_type'].value_counts()

# create weekday variable, and time of day variable:
data_removed_outliers['dec_point_datetime'] = pd.to_datetime(data_removed_outliers['available_decision_point'])
del data_removed_outliers['available_decision_point']
data_removed_outliers['weekday'] = [i.weekday() for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['hour_of_day'] = [i.hour for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['part_of_day'] = [get_part_of_day(i) for i in data_removed_outliers['hour_of_day']]
del data_removed_outliers['dec_point_datetime']

# how many hours in a day per id: 

hour_diffs = {}
uq_ids = list(data_removed_outliers['id'].unique())
for id_val in uq_ids: 
    print(id_val)
    hour_diffs[id_val] = []
    data_id = data_removed_outliers[data_removed_outliers['id'] == id_val]
    for day_val in range(10): 
        day_val_num = day_val + 1
        data_id_day_hour = data_id[data_id['day_num'] == day_val_num].hour_of_day
        max_hour = np.max(data_id_day_hour)
        min_hour = np.min(data_id_day_hour)
        hour_diff_val = max_hour - min_hour
        print("    ", hour_diff_val)
        hour_diffs[id_val].append(hour_diff_val)

max_per_id = []
for id_val in uq_ids:
    max_per_id.append(np.nanmax(hour_diffs[id_val]))

total_max = np.nanmax(max_per_id)
# 12, aside from one outlier inside id 1's 10th day (in which case this is 23). Note to 
# fix this for primary analysis.

# Create dummy variables:
cat_vars=['part_of_day']
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(data_removed_outliers[var], prefix=var)
    data1 = data_removed_outliers.join(cat_list)
    data_removed_outliers = data1

cat_vars=['part_of_day']
data_vars=data_removed_outliers.columns.values.tolist()
to_keep=[i for i in data_vars if i not in cat_vars]

data_final=data_removed_outliers[to_keep]
data_final.columns.values

data_final['episode_type'] = data_final['episode_type_miss'].astype('int')

# remove nans for now:
data_final = data_final.dropna()

# create training/testing with balanced y in training:

# find if any features in X are highly correlated and remove:
# X.corr()

# make sure dtypes are correct:

X = data_final
del X['episode_type_miss']
del X['episode_type_stress']
del X['episode_type_no_stress']

convert_dict = {
   'id': 'int64',
   'day_num': 'int64',
   'available_decision_point_stress_episode': 'object',
   'episode_length': 'int64',
   'previous_episode_miss': 'object',
   'previous_episode_stress': 'object',
   'previous_episode_no_stress': 'object',
   'previous_episode_length': 'int64',
   'prev_day_activity_prop': 'float64',
   'prev_day_bad_qual_rep_prop': 'float64',
   'prev_day_bad_qual_ecg_prop': 'float64',
   'num_ints_trig_prev_day': 'int64',
   'day1_bmi': 'float64',
   'sex': 'object',
   'age': 'int64',
   'age_smoke': 'int64',
   'fagerstromtotal': 'int64',
   'weekday': 'object',
   'hour_of_day': 'int64',
   'part_of_day_afternoon': 'object',
   'part_of_day_evening': 'object',
   'part_of_day_morning': 'object', 
   'part_of_day_night': 'object',
   'episode_type': 'object'}
X = X.astype(convert_dict)

# standardise all features in X:

scaler = StandardScaler()
num_cols = X.columns[X.dtypes.apply(lambda c: np.issubdtype(c, np.number))]
X[num_cols] = scaler.fit_transform(X[num_cols])

del X['episode_type']

y = data_final.loc[:, data_final.columns == 'episode_type']
y = y.astype('int')

from imblearn.over_sampling import SMOTE
os = SMOTE(random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
columns = X_train.columns

###########################
# RUN GRID SEARCH ON KNN  #
###########################

grid_params = {
  'n_neighbors': [3,5,11,19],
  'weights': ['uniform', 'distance'],
  'metric': ['manhattan']
}

gs = GridSearchCV(
   KNeighborsClassifier(),
   grid_params,
   verbose = 1,
   cv = 3,
   n_jobs = -1,
   scoring = 'recall'
)

gs_results = gs.fit(X_train, y_train.values.ravel())
gs_results.best_score_
gs_results.best_params_

# Now run best model:

clf = gs_results.best_estimator_
clf.fit(X_train, y_train)
train_score = clf.score(X_train, y_train)
test_score = clf.score(X_test, y_test)
print("train_score: ", train_score)
print("test_score: ", test_score)

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix

y_pred = clf.predict(X_test)
best_f1_KNN = recall_score(y_test, y_pred, average="macro")
f1_score(y_test, y_pred, average="macro")

# perform permutation importance
results = permutation_importance(clf, X_test, y_test, scoring='f1')

importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(results.importances_mean)})
# Make sure to sort this by absolute value:
importances_KNN = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)

# The permutation importance of a feature is calculated as follows.
# First, a baseline metric, defined by scoring, is evaluated on a (potentially different)
# dataset defined by the X. Next, a feature column from the validation set is permuted and
# the metric is evaluated again. The permutation importance is defined to be the difference
# between the baseline metric and metric from permutating the feature column.

###########################################
# RUN GRID SEARCH ON Logistic Regression  #
###########################################

grid_params = {
   "C" : np.logspace(-3,3,7),
   "penalty" : ["l1", "l2", "elasticnet", 'none'],
   "dual": [True,False],
   "max_iter": [100, 110, 120, 130, 140],
} # l1 lasso l2 ridge

gs = GridSearchCV(
   LogisticRegression(class_weight = 'balanced'),
   grid_params,
   verbose = 1,
   cv = 10,
   scoring = 'recall',
)

gs_results = gs.fit(X_train, y_train)
gs_results.best_score_
gs_results.best_params_

# Now run best model:

clf = gs_results.best_estimator_
clf.fit(X_train, y_train)
train_score = clf.score(X_train, y_train)
test_score = clf.score(X_test, y_test)
print("train_score: ", train_score)
print("test_score: ", test_score)


import sklearn

y_pred = clf.predict(X_test)
best_recall_LR = sklearn.metrics.recall_score(y_test, y_pred, average="weighted")
best_f1_LR = sklearn.metrics.f1_score(y_test, y_pred, average="weighted")

importance_vals = list(np.std(X_train, 0) * clf.coef_[0])
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(importance_vals)})
# Make sure to sort this by absolute value:
importances_LR = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)

###############################################
# RUN GRID SEARCH ON Random Forest Classifer  #
###############################################

grid_params = {
    'n_estimators': [100],
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth' : [4,5,6,7,8],
    'criterion' :['gini', 'entropy']
}

gs = GridSearchCV(
   RandomForestClassifier(random_state = 42, class_weight = 'balanced'),
   grid_params,
   cv = 5,
   verbose = 1,
   scoring = 'recall'
)

gs_results = gs.fit(X_train, y_train)
gs_results.best_score_
gs_results.best_params_

# Now run best model:

clf = gs_results.best_estimator_
clf.fit(X_train, y_train)
train_score = clf.score(X_train, y_train)
test_score = clf.score(X_test, y_test)
print("train_score: ", train_score)
print("test_score: ", test_score)

y_pred = clf.predict(X_test)
best_f1_RF = recall_score(y_test, y_pred, average="macro")
f1_score(y_test, y_pred, average="macro")

importance_vals = list(clf.feature_importances_)
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': importance_vals})
# Make sure to sort this by absolute value:
importances_RF = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)


###############################################
# RUN GRID SEARCH ON DecisionTreeClassifier   #
###############################################

grid_params = {
    'criterion': ['gini', 'entropy'],
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth': [4,5,6,7,8],
}

gs = GridSearchCV(
   DecisionTreeClassifier(),
   grid_params,
   cv = 5,
   scoring = 'recall',
   verbose = 1
)

gs_results = gs.fit(X_train, y_train)
gs_results.best_score_
gs_results.best_params_

# Now run best model:

clf = gs_results.best_estimator_
clf.fit(X_train, y_train)
train_score = clf.score(X_train, y_train)
test_score = clf.score(X_test, y_test)
print("train_score: ", train_score)
print("test_score: ", test_score)

y_pred = clf.predict(X_test)
best_f1_DT = recall_score(y_test, y_pred, average="macro")
f1_score(y_test, y_pred, average="macro")

importance_vals = list(clf.feature_importances_)
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': importance_vals})
# Make sure to sort this by absolute value:
importances_DT = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)


###############################################
# RUN GRID SEARCH ON ...   #
###############################################

# try different classifiers:

classifiers = [
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]




##################################################################################
# VARIANCE REDUCTION ANALYSIS: 
# Run a model with the 2 variables for variance reduction and longitudinal minute 
# level outcome to see how well they actually do predict the minute level outcomes.
##################################################################################

# bring in data:
var_reduc_data = pd.read_csv("var_reduc_data_df.csv")
del var_reduc_data['Unnamed: 0']

df = pd.DataFrame(columns=['id', 'day', 'daynum', 'available_decision_point',
                           'avai_dec_time_is_stress_vals', 'min_after_dec_point', 'prox_outcome',
                           'mins_stressed_prior', 'mins_active_prior'])

id_list = list(var_reduc_data['id'].unique())
# re-code id with integers:
id_count = 1
for id in id_list:
    df_to_append = var_reduc_data[var_reduc_data['id'] == id]
    len_df_to_append = df_to_append.shape[0]
    df_to_append['id'] = [id_count]*len_df_to_append
    df = df.append(df_to_append)
    id_count = id_count + 1

df = df.reset_index(drop=True)

# remove outliers from data:

numeric_cols = ['min_after_dec_point', 'mins_stressed_prior', 'mins_stressed_prior']
indices_to_remove = []
for numeric_col in numeric_cols:
    inds = df.index[np.abs(stats.zscore(df[numeric_col])) >= 3].tolist()
    indices_to_remove = indices_to_remove + inds

data_removed_outliers = df.drop(df.index[indices_to_remove])

def get_part_of_day(hour):
    return (
        "morning" if 5 <= hour <= 11
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening" if 18 <= hour <= 22
        else
        "night")

del data_removed_outliers['day']

# create weekday variable, and time of day variable:
data_removed_outliers['dec_point_datetime'] = pd.to_datetime(data_removed_outliers['available_decision_point'])
del data_removed_outliers['available_decision_point']
data_removed_outliers['weekday'] = [i.weekday() for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['hour_of_day'] = [i.hour for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['part_of_day'] = [get_part_of_day(i) for i in data_removed_outliers['hour_of_day']]
del data_removed_outliers['dec_point_datetime']

# Create dummy variables:
cat_vars = ['part_of_day']
for var in cat_vars:
    cat_list = 'var'+'_'+var
    cat_list = pd.get_dummies(data_removed_outliers[var], prefix=var)
    data1 = data_removed_outliers.join(cat_list)
    data_removed_outliers = data1

cat_vars = ['part_of_day']
data_vars = data_removed_outliers.columns.values.tolist()
to_keep = [i for i in data_vars if i not in cat_vars]

data_final = data_removed_outliers[to_keep]
data_final.columns.values

# remove nans for now:
data_final = data_final.dropna()

# create training/testing with balanced y in training:

# find if any features in X are highly correlated and remove:
# X.corr()

# make sure dtypes are correct:

X = data_final

# filter to not include rows that have a missing prox outcome: 
X = X.loc[X['prox_outcome'].isin(['detected-stressed', 'not-detected-stressed', 'physically_active'])]

# convert_dict = {
#     'id': 'int64',
#     'daynum': 'int64',
#     'avai_dec_time_is_stress_vals': 'object',
#     'min_after_dec_point': 'int64',
#     'prox_outcome': 'object',
#     'mins_stressed_prior': 'int64',
#     'mins_active_prior': 'int64',
#     'weekday': 'object',
#     'hour_of_day': 'int64',
#     'part_of_day_afternoon': 'object',
#     'part_of_day_evening': 'object',
#     'part_of_day_morning': 'object',
#     'part_of_day_night': 'object'}

convert_dict = {
    'id': 'int64',
    'daynum': 'int64',
    'avai_dec_time_is_stress_vals': 'object',
    'min_after_dec_point': 'int64',
    'prox_outcome': 'object',
    'mins_stressed_prior': 'int64',
    'mins_active_prior': 'int64',
    'weekday': 'object',
    'hour_of_day': 'int64',
    'part_of_day_afternoon': 'object',
    'part_of_day_evening': 'object',
    'part_of_day_morning': 'object',
    'part_of_day_night': 'object'}

X = X.astype(convert_dict)

# standardise all features in X:

scaler = StandardScaler()
num_cols = X.columns[X.dtypes.apply(lambda c: np.issubdtype(c, np.number))]
X[num_cols] = scaler.fit_transform(X[num_cols])

y = X.loc[:, X.columns == 'prox_outcome']
y = y.astype('object')

del X['prox_outcome']

os = SMOTE(random_state=0)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0)
columns = X_train.columns

#######################################################
# RUN GRID SEARCH ON Multinomial Logistic Regression  #
#######################################################

grid_params = {
    "C": np.logspace(-3, 3, 7),
    "penalty": ["l1", "l2", "elasticnet", 'none'],
    "dual": [True, False],
    "max_iter": [100, 110, 120, 130, 140],
}  # l1 lasso l2 ridge

gs = GridSearchCV(
    LogisticRegression(class_weight='balanced', multi_class='multinomial'),
    grid_params,
    verbose=1,
    cv=10,
    scoring='recall',
)

gs_results = gs.fit(X_train, y_train)
gs_results.best_score_
gs_results.best_params_

# Run best model:
clf = gs_results.best_estimator_
clf.fit(X_train, y_train)
train_score = clf.score(X_train, y_train)
test_score = clf.score(X_test, y_test)
print("train_score: ", train_score)
print("test_score: ", test_score)

y_pred = clf.predict(X_test)
sklearn.metrics.recall_score(y_test, y_pred, average="weighted")
sklearn.metrics.f1_score(y_test, y_pred, average="weighted")

importance_vals = list(np.std(X_train, 0) * clf.coef_[0])
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(importance_vals)})
# Sort this by absolute value:
importances_LR = importances.reindex(importances.mean_importances.abs().sort_values(ascending=False).index)





