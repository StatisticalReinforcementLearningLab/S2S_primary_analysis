# Last changed: 23 JUL 2020

#  import modules: 

import os
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

# Create data frame with start and end of day time info:

day_start_alternative = pd.read_csv(wd + '/' + "study_day_start_phone_alternative.csv")
uq_ids_day_start_alternative = list(day_start_alternative.participant_id.unique())
day_start_backup = pd.read_csv(wd + '/' + "study_day_start_phone_backup.csv")
uq_ids_day_start_backup = list(day_start_backup.participant_id.unique())
day_start_original = pd.read_csv(wd + '/' + "study_day_start_phone_original.csv")
uq_ids_day_start_original = list(day_start_original.participant_id.unique())

day_end_alternative = pd.read_csv(wd + '/' + "study_day_end_phone_alternative.csv")
uq_ids_day_end_alternative = list(day_end_alternative.participant_id.unique())
day_end_backup = pd.read_csv(wd + '/' + "study_day_end_phone_backup.csv")
uq_ids_day_end_backup = list(day_end_backup.participant_id.unique())
day_end_original = pd.read_csv(wd + '/' + "study_day_end_phone_original.csv")
uq_ids_day_end_original = list(day_end_original.participant_id.unique())

day_start = pd.DataFrame(columns=['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_day_start_backup:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_start_backup[day_start_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)
    elif id in uq_ids_day_start_original:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_start_backup[day_start_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)
    elif id in uq_ids_day_start_alternative:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_start_backup[day_start_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)

day_start = day_start.drop_duplicates().reset_index(drop=True)

day_end = pd.DataFrame(columns=['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_day_end_backup:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_end_backup[day_end_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)
    elif id in uq_ids_day_end_original:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_end_backup[day_end_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)
    elif id in uq_ids_day_end_alternative:
        data_to_append = pd.DataFrame(columns=['datetime', 'date', 'timestamp', 'event', 'participant_id'])
        data = day_end_backup[day_end_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)

day_end = day_end.drop_duplicates().reset_index(drop=True)

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/"
day_start.to_pickle(wd_to_save + "day_start_df.pkl")
day_end.to_pickle(wd_to_save + "day_end_df.pkl")
