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

# Create stress episode classification data: 

full_ep_times_original = pd.read_csv(wd + '/' + "classification_full_episode_original.csv")
uq_ids_ep_times_original = list(full_ep_times_original.participant_id.unique())
full_ep_times_backup = pd.read_csv(wd + '/' + "classification_full_episode_backup.csv")
uq_ids_ep_times_backup = list(full_ep_times_backup.participant_id.unique())
full_ep_times_alternative = pd.read_csv(wd + '/' + "classification_full_episode_alternative.csv")
uq_ids_ep_times_alternative = list(full_ep_times_alternative.participant_id.unique())

episodes = pd.DataFrame(columns = ['date', 'datetime_start', 'datetime_peak', 'datetime_end', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_ep_times_backup:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime_start', 'datetime_peak', 'datetime_end', 'event', 'participant_id'])
        data = full_ep_times_backup[full_ep_times_backup['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime_start'] = [date_time(i) for i in data['StartTime']]
        data_to_append['datetime_peak'] = [date_time(i) for i in data['PeakTime']]
        data_to_append['datetime_end'] = [date_time(i) for i in data['EndTime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime_start']]
        data_to_append['event'] = data['Stress_Episode_Classification']
        data_to_append['participant_id'] = data['participant_id']
        episodes = episodes.append(data_to_append)
    elif id in uq_ids_ep_times_original:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime_start', 'datetime_peak', 'datetime_end', 'event', 'participant_id'])
        data = full_ep_times_original[full_ep_times_original['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime_start'] = [date_time(i) for i in data['StartTime']]
        data_to_append['datetime_peak'] = [date_time(i) for i in data['PeakTime']]
        data_to_append['datetime_end'] = [date_time(i) for i in data['EndTime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime_start']]
        data_to_append['event'] = data['Stress_Episode_Classification']
        data_to_append['participant_id'] = data['participant_id']
        episodes = episodes.append(data_to_append)
    elif id in uq_ids_ep_times_alternative:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime_start', 'datetime_peak', 'datetime_end', 'event', 'participant_id'])
        data = full_ep_times_alternative[full_ep_times_alternative['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime_start'] = [date_time(i) for i in data['StartTime']]
        data_to_append['datetime_peak'] = [date_time(i) for i in data['PeakTime']]
        data_to_append['datetime_end'] = [date_time(i) for i in data['EndTime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime_start']]
        data_to_append['event'] = data['Stress_Episode_Classification']
        data_to_append['participant_id'] = data['participant_id']
        episodes = episodes.append(data_to_append)

episodes = episodes.drop_duplicates().reset_index(drop=True)

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/python_dfs/stress_episode_classification_df.csv"
episodes.to_csv(wd_to_save)
