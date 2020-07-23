# Last changed: 23 JUL 2020

#  import modules: 

import pickle
import os
import ast
import joblib
import pandas as pd
from user_defined_modules import date_time

wd = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/stress_cleaned_data"

file_marker = 'phone_log_backup'
participant_ids_backup = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd) if file_marker in filename]
participant_ids_backup.sort()

file_marker = 'phone_log_original'
participant_ids_original = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd) if file_marker in filename]
participant_ids_original.sort()

file_marker = 'phone_log_alternative'
participant_ids_alternative = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd) if file_marker in filename]
participant_ids_alternative.sort()

all_participant_ids = set(participant_ids_original) | set(participant_ids_backup) | set(participant_ids_alternative)
all_participant_ids = sorted(all_participant_ids)

# Create a dictionary of data frames for the phone logs for each participant:

logs_w_dicts = {}
for id in all_participant_ids:
    f_save = 'phone_log_' + id
    if id in participant_ids_backup:
        f = 'phone_log_backup' + id + '.csv'
        logs_w_dicts[f_save] = pd.read_csv(wd + '/' + f)
    elif id in participant_ids_original:
        f = 'phone_log_original' + id + '.csv'
        logs_w_dicts[f_save] = pd.read_csv(wd + '/' + f)
    elif id in participant_ids_alternative:
        f = 'phone_log_alternative' + id + '.csv'
        logs_w_dicts[f_save] = pd.read_csv(wd + '/' + f)

all_participant_ids = [int(i) for i in all_participant_ids]

# Convert columns with strings of dictionaries to columns and values (this is needed for
# 'emiInfo' and 'logScheduler'):
logs = {}
for idVal in all_participant_ids:
    print(idVal)
    name = 'phone_log_' + str(idVal)
    df = logs_w_dicts[name]
    df['time_stamp'] = df['timestamp']
    # convert string of dictionaries to dictionaries for columns 'emiInfo' and 'logScheduler':
    if 'emiInfo' in df.columns:
        df['emiInfo'] = [ast.literal_eval(d) if isinstance(d, str) else d for d in df['emiInfo']]
        # Add keys as columns and values as cells in columns to original data frame:
        df = pd.concat([df.drop(['emiInfo'], axis=1),df['emiInfo'].apply(pd.Series)], axis=1)
        # remove second timestamp column:
        del df['timestamp']
        # delete redundant '0' columns created by pd.Series:
        del df[0]
    if 'logScheduler' in df.columns:
        df['logSchedule'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['logSchedule']]
        df = pd.concat([df.drop(['logSchedule'], axis=1),df['logSchedule'].apply(pd.Series)], axis=1)
        # remove second timestamp column:
        del df['timestamp']
        # delete redundant '0' columns created by pd.Series:
        del df[0]
    # make datetime object:
    df['date_time'] = [date_time(i) for i in df['time_stamp']]
    df['date'] = [i.date() for i in df['date_time']]
    logs[name] = df

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/log_dict.pkl"

with open(wd_to_save, 'wb') as handle: 
    pickle.dump(logs, handle, protocol=pickle.HIGHEST_PROTOCOL)
