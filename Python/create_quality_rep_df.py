# Last changed: 23 JUL 2020

#  import modules: 

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

# Create data frame with quality rep info:

quality_rep_alternative = pd.read_csv(wd + '/' + "cstress_data_rep_quality_alternative.csv")
uq_ids_quality_rep_alternative = list(quality_rep_alternative.participant_id.unique())
quality_rep_backup = pd.read_csv(wd + '/' + "cstress_data_rep_quality_backup.csv")
uq_ids_quality_rep_backup = list(quality_rep_backup.participant_id.unique())
quality_rep_original = pd.read_csv(wd + '/' + "cstress_data_rep_quality_original.csv")
uq_ids_quality_rep_original = list(quality_rep_original.participant_id.unique())

quality_rep = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_quality_rep_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_rep_backup[quality_rep_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_rep = quality_rep.append(data_to_append)
    elif id in uq_ids_quality_rep_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_rep_original[quality_rep_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_rep = quality_rep.append(data_to_append)
    elif id in uq_ids_quality_rep_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = quality_rep_alternative[quality_rep_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        quality_rep = quality_rep.append(data_to_append)

quality_rep = quality_rep.drop_duplicates().reset_index(drop=True)

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/python_dfs/quality_rep_df.csv"
quality_rep.to_csv(wd_to_save)
