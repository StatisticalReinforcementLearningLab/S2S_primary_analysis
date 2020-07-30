# Last changed: 23 JUL 2020

# import modules: 

import os
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

all_participant_ids = [int(i) for i in all_participant_ids]

# Create data frame with quality ecg info:

quality_ecg_alternative = pd.read_csv(wd + '/' + "cstress_data_ecg_quality_alternative.csv")
uq_ids_quality_ecg_alternative = list(quality_ecg_alternative.participant_id.unique())
quality_ecg_backup = pd.read_csv(wd + '/' + "cstress_data_ecg_quality_backup.csv")
uq_ids_quality_ecg_backup = list(quality_ecg_backup.participant_id.unique())
quality_ecg_original = pd.read_csv(wd + '/' + "cstress_data_ecg_quality_original.csv")
uq_ids_quality_ecg_original = list(quality_ecg_original.participant_id.unique())

quality_ecg = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_quality_ecg_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_ecg_backup[quality_ecg_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_ecg = quality_ecg.append(data_to_append)
    elif id in uq_ids_quality_ecg_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_ecg_original[quality_ecg_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_ecg = quality_ecg.append(data_to_append)
    elif id in uq_ids_quality_ecg_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_ecg_alternative[quality_ecg_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_ecg = quality_ecg.append(data_to_append)

quality_ecg = quality_ecg.drop_duplicates().reset_index(drop=True)

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/quality_ecg_df.pkl"
quality_ecg.to_pickle(wd_to_save)
