from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import pandas as pd
from scipy import stats
from user_defined_modules import get_part_of_day
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
import sklearn

# define data directories: 
pickle_jar = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/"
csv_files_dir = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/csv_files/"

missing_df = pd.read_pickle(pickle_jar + "missing_df.pkl")
baseline_df = pd.read_csv(csv_files_dir + "baseline.csv")

del missing_df['isRand']

# add baseline_df to missing_df data set:

df = pd.DataFrame(columns=['id', 'day', 'day_num', 'available_decision_point', 
       'available_decision_point_stress_episode', 'available_decision_point_episode_length',
       'episode_type_miss', 'previous_episode_miss',
       'previous_episode_stress', 'previous_episode_no_stress', 'previous_episode_length',
       'prev_day_activity_prop', 'prev_day_bad_qual_rep_prop',
       'prev_day_bad_qual_ecg_prop', 'num_ints_trig_prev_day', 'day1_bmi',
       'sex', 'age', 'age_smoke', 'fagerstromtotal'])

id_list = list(missing_df['id'].unique())
# re-code id with integers:
id_count = 1
for id in id_list:
    df_to_append = missing_df[missing_df['id'] == id]
    len_df_to_append = df_to_append.shape[0]
    baseline_id = baseline_df[baseline_df['study_id'] == id]
    df_to_append['day1_bmi'] = [float(baseline_id['day1_bmi'])]*len_df_to_append
    df_to_append['sex'] = [int(baseline_id['sex'])]*len_df_to_append
    df_to_append['age'] = [int(baseline_id['age'])]*len_df_to_append
    df_to_append['age_smoke'] = [float(baseline_id['age_smoke'])]*len_df_to_append
    df_to_append['fagerstromtotal'] = [float(baseline_id['fagerstromtotal'])]*len_df_to_append
    df_to_append['id'] = [id_count]*len_df_to_append
    df = df.append(df_to_append)
    id_count = id_count + 1

df = df.dropna().reset_index(drop=True)

# remove outliers from data:

numeric_cols = ['previous_episode_length', 'prev_day_activity_prop',
  'prev_day_bad_qual_rep_prop', 'prev_day_bad_qual_ecg_prop', 'prev_day_bad_qual_ecg_prop',
  'num_ints_trig_prev_day', 'day1_bmi', 'sex', 'age', 'age_smoke', 'fagerstromtotal']
indices_to_remove = []
for numeric_col in numeric_cols:
    inds = df.index[np.abs(stats.zscore(df[numeric_col])) >= 3].tolist()
    print(inds)
    indices_to_remove = indices_to_remove + inds

# remove duplicates: 
final_indices_to_remove = list(dict.fromkeys(indices_to_remove))
data_removed_outliers = df.drop(df.index[final_indices_to_remove])

# we don't require day since we have day_num:
del data_removed_outliers['day']

# create weekday variable, and time of day variable:
data_removed_outliers['dec_point_datetime'] = pd.to_datetime(data_removed_outliers['available_decision_point'])
del data_removed_outliers['available_decision_point']
data_removed_outliers['weekday'] = [i.weekday() for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['hour_of_day'] = [i.hour for i in data_removed_outliers['dec_point_datetime']]
data_removed_outliers['part_of_day'] = [get_part_of_day(i) for i in data_removed_outliers['hour_of_day']]
del data_removed_outliers['dec_point_datetime']

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
data_final = data_final.dropna().reset_index(drop=True)

# remove extreme values from episode_length: 

indices_to_remove = data_final.index[np.abs(stats.zscore(data_final.previous_episode_length)) >= 3].tolist()
final_df = data_final.drop(data_final.index[indices_to_remove])

# create training/testing with balanced y in training:
# make sure dtypes are correct:

X = final_df
del X['episode_type_miss']
# del X['episode_type_stress']
# del X['episode_type_no_stress']

convert_dict = {
   'id': 'int64',
   'day_num': 'int64',
   'available_decision_point_stress_episode': 'object',
   'available_decision_point_episode_length': 'float64',
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

y = final_df.loc[:, final_df.columns == 'episode_type']
y = y.astype('int')

# create training and testing set of data split 70/30:

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
columns = X_train.columns

###########################
# RUN GRID SEARCH ON KNN  #
###########################

# grid_params = {
#   'n_neighbors': [3,5,11,19],
#   'weights': ['uniform', 'distance'],
#   'metric': ['manhattan']
# }

# gs = GridSearchCV(
#    KNeighborsClassifier(),
#    grid_params,
#    verbose = 1,
#    cv = 3,
#    n_jobs = -1,
#    scoring = 'recall'
# )

# gs_results = gs.fit(X_train, y_train.values.ravel())
# gs_results.best_score_
# gs_results.best_params_

# # Now run best model:

# clf = gs_results.best_estimator_
# clf.fit(X_train, y_train)
# train_score = clf.score(X_train, y_train)
# test_score = clf.score(X_test, y_test)
# print("train_score: ", train_score)
# print("test_score: ", test_score)

# from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix

# y_pred = clf.predict(X_test)
# best_f1_KNN = recall_score(y_test, y_pred, average="macro")
# f1_score(y_test, y_pred, average="macro")

# # perform permutation importance
# results = permutation_importance(clf, X_test, y_test, scoring='f1')

# importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(results.importances_mean)})
# # Make sure to sort this by absolute value:
# importances_KNN = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)

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

y_pred = clf.predict(X_test)
best_recall_LR = sklearn.metrics.recall_score(y_test, y_pred, average="weighted")
best_f1_LR = sklearn.metrics.f1_score(y_test, y_pred, average="weighted")

# importance_vals = list(np.std(X_train, 0) * clf.coef_[0])
importance_vals = list(clf.coef_[0])
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(importance_vals)})
# Make sure to sort this by absolute value:
importances_LR = importances.reindex(importances.mean_importances.abs().sort_values(ascending = False).index)

from sklearn.metrics import confusion_matrix
confusion = confusion_matrix(y_test, y_pred)
print('Confusion Matrix\n')
print(confusion)

#importing accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
print('\nAccuracy: {:.2f}\n'.format(accuracy_score(y_test, y_pred)))

print('Micro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='micro')))
print('Micro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='micro')))
print('Micro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='micro')))

print('Macro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='macro')))
print('Macro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='macro')))
print('Macro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='macro')))

print('Weighted Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='weighted')))
print('Weighted Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='weighted')))
print('Weighted F1-score: {:.2f}'.format(f1_score(y_test, y_pred, average='weighted')))

from sklearn.metrics import classification_report
print('\nClassification Report\n')
print(classification_report(y_test, y_pred, target_names=['observed episode', 'missing episode']))



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

##################################################################################
# VARIANCE REDUCTION ANALYSIS: 
# Run a model with the 2 variables for variance reduction and longitudinal minute 
# level outcome to see how well they actually do predict the minute level outcomes.
##################################################################################

# bring in data:

var_reduc_data = pd.read_pickle(pickle_jar + "var_reduc_data_df.pkl")

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

df = df.dropna().reset_index(drop=True)

# remove outliers from data:

numeric_cols = ['min_after_dec_point', 'mins_stressed_prior', 'mins_stressed_prior']
indices_to_remove = []
for numeric_col in numeric_cols:
    inds = df.index[np.abs(stats.zscore(df[numeric_col])) >= 3].tolist()
    indices_to_remove = indices_to_remove + inds

data_removed_outliers = df.drop(df.index[indices_to_remove])

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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
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

# "weighted" accounts for class imbalance by computing the average of
#  binary metrics in which each class’s score is weighted by its presence 
#  in the true data sample.

sklearn.metrics.recall_score(y_test, y_pred, average=None)
sklearn.metrics.f1_score(y_test, y_pred, average=None)


# importance_vals = list(np.std(X_train, 0) * clf.coef_[0])
importance_vals = list(clf.coef_[0])
importances = pd.DataFrame({'feature': list(X_test.columns), 'mean_importances': list(importance_vals)})
# Sort this by absolute value:
importances_LR = importances.reindex(importances.mean_importances.abs().sort_values(ascending=False).index)

#importing confusion matrix
from sklearn.metrics import confusion_matrix
confusion = confusion_matrix(y_test, y_pred)
print('Confusion Matrix\n')
print(confusion)

#importing accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
print('\nAccuracy: {:.2f}\n'.format(accuracy_score(y_test, y_pred)))

print('Micro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='micro')))
print('Micro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='micro')))
print('Micro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='micro')))

print('Macro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='macro')))
print('Macro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='macro')))
print('Macro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='macro')))

print('Weighted Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='weighted')))
print('Weighted Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='weighted')))
print('Weighted F1-score: {:.2f}'.format(f1_score(y_test, y_pred, average='weighted')))

from sklearn.metrics import classification_report
print('\nClassification Report\n')
print(classification_report(y_test, y_pred, target_names=['detected-stressed', 
                                                          'not-detected-stressed', 'physically_active']))
