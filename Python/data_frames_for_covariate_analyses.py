
# Sense2Stop Data Pre-processing

# Last modified: 22 JUN 2020

# import necessary modules:
import pandas as pd
import os
import ast
import numpy as np
from datetime import datetime
from datetime import timedelta
import joblib
import pytz

################################
# Define functions:

# get datetime from timestamp:
def date_time(intime):
    return (datetime.fromtimestamp(int(intime)/1000, tz=pytz.timezone('America/Chicago')))

# define intervention:
def intervention(row):
    val = np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == True), 'class_stress', # available_stress
            np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == False), 'class_notStress', # available_notStress
              np.where((row['id'] == 'EMI') and (row['status'] == 'DELIVERED'), 'delivered', 'other'))) # delivered, other.
    return val    

def minute_rounder(t):
    # Rounds to nearest minute by adding a timedelta minute if seconds >= 30
    return (t.replace(second=0, microsecond=0, minute=t.minute, hour=t.hour)
               +timedelta(minutes=t.second//30))

# create function to extract the el elements in a every key's list within
# a dictionary:
def Extract(dict, el):
    return [item[el] for item in dict.values()]

# define scatterplot:
def scatterplot(x_data, y_data, x_label, y_label, title):
    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data, s = 30, color = '#539caf', alpha = 0.75)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim([min(id_df.date_time), max(id_df.date_time)])
    fig.autofmt_xdate()
################################

wd = "/Users/mariannemenictas/Desktop/stress_cleaned_data4"

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

# First, check which inds have corresponding log files:

all_expected_inds = set(range(201, 271))
all_received_inds = set([int(i) for i in all_participant_ids])
missing_inds = all_expected_inds.difference(all_received_inds) # no missing inds..

# Create a dictionary of DataFrames for the phone logs for each participant:
# To access each df: e.g., "dfs['phone_log202']".

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

day_end_backup = pd.read_csv(wd + '/' + "study_day_end_phone_backup.csv")
uq_ids_day_end_backup = list(day_end_backup.participant_id.unique())
day_end_original = pd.read_csv(wd + '/' + "study_day_end_phone_original.csv")
uq_ids_day_end_original = list(day_end_original.participant_id.unique())
day_end_alternative = pd.read_csv(wd + '/' + "study_day_end_phone_alternative.csv")
uq_ids_day_end_alternative = list(day_end_alternative.participant_id.unique())

day_start_backup = pd.read_csv(wd + '/' + "study_day_start_phone_backup.csv")
uq_ids_day_start_backup = list(day_start_backup.participant_id.unique())
day_start_original = pd.read_csv(wd + '/' + "study_day_start_phone_original.csv")
uq_ids_day_start_original = list(day_start_original.participant_id.unique())
day_start_alternative = pd.read_csv(wd + '/' + "study_day_start_phone_alternative.csv")
uq_ids_day_start_alternative = list(day_start_alternative.participant_id.unique())

all_participant_ids = [int(i) for i in all_participant_ids]

day_end = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_day_end_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_end_backup[day_end_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)
    elif id in uq_ids_day_end_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_end_original[day_end_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)
    elif id in uq_ids_day_end_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_end_alternative[day_end_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_end = day_end.append(data_to_append)

day_end = day_end.reset_index(drop=True)

day_start = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_day_start_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_start_backup[day_start_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)
    elif id in uq_ids_day_start_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_start_original[day_start_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)
    elif id in uq_ids_day_start_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = day_start_alternative[day_start_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        day_start = day_start.append(data_to_append)

day_start = day_start.reset_index(drop=True)

# Create data frame with activity info:
activity_alternative = pd.read_csv(wd + '/' + "stress_activity_phone_alternative.csv")
uq_ids_activity_alternative = list(activity_alternative.participant_id.unique())
activity_backup = pd.read_csv(wd + '/' + "stress_activity_phone_backup.csv")
uq_ids_activity_backup = list(activity_backup.participant_id.unique())
activity_original = pd.read_csv(wd + '/' + "stress_activity_phone_original.csv")
uq_ids_activity_original = list(activity_original.participant_id.unique())

activity = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_activity_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = activity_backup[activity_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        activity = activity.append(data_to_append)
    elif id in uq_ids_activity_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = activity_original[activity_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        activity = activity.append(data_to_append)
    elif id in uq_ids_activity_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = activity_alternative[activity_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        activity = activity.append(data_to_append)

activity = activity.drop_duplicates().reset_index(drop=True)

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


# Episode data:
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

# Record which date is Quit day (Day 4) for each participant. This is Day 1 of the
# 10 day micro-randomized trial period. This is hard coded in from info provided
# by Elyse Daly (study coordinator at NW):

# print unique dates in log files:
for id in all_participant_ids:
    print(id)
    value_name = 'phone_log_' + str(id)
    uq_dates = sorted(set([date_time(i).date() for i in logs_w_dicts[value_name]['timestamp']]))
    print(uq_dates)

# Convert columns with strings of dictionaries to columns and values (this is needed for
# 'emiInfo' and 'logScheduler'):
logs = {}
for idVal in all_participant_ids:
    print(idVal)
    name = 'phone_log_' + str(idVal)
    df = logs_w_dicts[name]
    df['time_stamp'] = df['timestamp']
    # del df['timestamp']
    # convert string of dictionaries to dictionaries for columns 'emiInfo' and 'logScheduler':
    # NB: 'd==d' checks that values are not nan.
    if 'emiInfo' in df.columns:
        # df['emiInfo'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['emiInfo']]
        df['emiInfo'] = [ast.literal_eval(d) if isinstance(d, str) else d for d in df['emiInfo']]
        # df['emiInfo'] = [d if d == d else np.NaN for d in df['emiInfo']]
        # Add keys as columns and values as cells in columns to original data frame:
        df = pd.concat([df.drop(['emiInfo'], axis=1), df['emiInfo'].apply(pd.Series)], axis=1)
        # remove second timestamp column: 
        del df['timestamp']
        # delete redundant '0' columns created by pd.Series:
        del df[0]
    if 'logScheduler' in df.columns:
        df['logSchedule'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['logSchedule']]
        df = pd.concat([df.drop(['logSchedule'], axis=1), df['logSchedule'].apply(pd.Series)], axis=1)
        # remove second timestamp column:
        del df['timestamp']
        # delete redundant '0' columns created by pd.Series:
        del df[0]
    # make datetime object:
    # df['date_time'] = [datetime.strptime(i, '%Y/%m/%d %H:%M:%S %p') for i in df['current_time']]
    df['date_time'] = [date_time(i) for i in df['time_stamp']]
    df['date'] = [i.date() for i in df['date_time']]
    logs[name] = df

no_dec_points = [201, 204, 206, 209, 210, 215, 217, 218, 220, 230, 232, 236,
                 237, 239, 241, 246, 247, 254, 257, 263, 270]
remaining_participant_ids = sorted(set(all_participant_ids).difference(set(no_dec_points)))

# store participant micro-radomization start days for the 47 participants
# we are keeping for analysis:

mrt_start_day = {}
mrt_start_day[202] = (datetime(year = 2017, month = 6, day = 26) + timedelta(days=3)).date()
mrt_start_day[203] = (datetime(year = 2017, month = 8, day = 7) + timedelta(days=3)).date()
mrt_start_day[205] = (datetime(year = 2017, month = 8, day = 18) + timedelta(days=3)).date()
mrt_start_day[207] = (datetime(year = 2017, month = 9, day = 18) + timedelta(days=3)).date()
mrt_start_day[208] = (datetime(year = 2017, month = 9, day = 18) + timedelta(days=3)).date()
mrt_start_day[211] = (datetime(year = 2017, month = 10, day = 2) + timedelta(days=3)).date()
mrt_start_day[212] = (datetime(year = 2017, month = 10, day = 13) + timedelta(days=3)).date()
mrt_start_day[213] = (datetime(year = 2017, month = 10, day = 16) + timedelta(days=3)).date()
mrt_start_day[214] = (datetime(year = 2017, month = 10, day = 23) + timedelta(days=3)).date()
mrt_start_day[216] = (datetime(year = 2017, month = 10, day = 27) + timedelta(days=3)).date()
mrt_start_day[219] = (datetime(year = 2017, month = 11, day = 13) + timedelta(days=3)).date()
mrt_start_day[221] = (datetime(year = 2017, month = 11, day = 27) + timedelta(days=3)).date()
mrt_start_day[222] = (datetime(year = 2017, month = 12, day = 4) + timedelta(days=3)).date()
mrt_start_day[223] = (datetime(year = 2018, month = 1, day = 5) + timedelta(days=3)).date()
mrt_start_day[224] = (datetime(year = 2018, month = 1, day = 22) + timedelta(days=3)).date()
mrt_start_day[225] = (datetime(year = 2018, month = 1, day = 26) + timedelta(days=3)).date()
mrt_start_day[226] = (datetime(year = 2018, month = 2, day = 9) + timedelta(days=3)).date()
mrt_start_day[227] = (datetime(year = 2018, month = 2, day = 9) + timedelta(days=3)).date()
mrt_start_day[228] = (datetime(year = 2018, month = 4, day = 6) + timedelta(days=3)).date()
mrt_start_day[229] = (datetime(year = 2018, month = 4, day = 13) + timedelta(days=3)).date()
mrt_start_day[231] = (datetime(year = 2018, month = 6, day = 18) + timedelta(days=3)).date()
mrt_start_day[233] = (datetime(year = 2018, month = 7, day = 13) + timedelta(days=3)).date()
mrt_start_day[234] = (datetime(year = 2018, month = 7, day = 16) + timedelta(days=3)).date()
mrt_start_day[235] = (datetime(year = 2018, month = 7, day = 20) + timedelta(days=3)).date()
mrt_start_day[238] = (datetime(year = 2018, month = 8, day = 6) + timedelta(days=3)).date()
mrt_start_day[240] = (datetime(year = 2018, month = 8, day = 13) + timedelta(days=3)).date()
mrt_start_day[242] = (datetime(year = 2018, month = 8, day = 24) + timedelta(days=3)).date()
mrt_start_day[243] = (datetime(year = 2018, month = 8, day = 27) + timedelta(days=3)).date()
mrt_start_day[244] = (datetime(year = 2018, month = 9, day = 7) + timedelta(days=3)).date()
mrt_start_day[245] = (datetime(year = 2018, month = 9, day = 10) + timedelta(days=3)).date()
mrt_start_day[248] = (datetime(year = 2018, month = 10, day = 22) + timedelta(days=3)).date()
mrt_start_day[249] = (datetime(year = 2018, month = 10, day = 26) + timedelta(days=3)).date()
mrt_start_day[250] = (datetime(year = 2018, month = 10, day = 29) + timedelta(days=3)).date()
mrt_start_day[251] = (datetime(year = 2018, month = 11, day = 12) + timedelta(days=4)).date()
mrt_start_day[252] = (datetime(year = 2018, month = 11, day = 30) + timedelta(days=3)).date()
mrt_start_day[253] = (datetime(year = 2018, month = 11, day = 30) + timedelta(days=3)).date()
mrt_start_day[255] = (datetime(year = 2019, month = 1, day = 25) + timedelta(days=3)).date()
mrt_start_day[256] = (datetime(year = 2019, month = 2, day = 4) + timedelta(days=3)).date()
mrt_start_day[258] = (datetime(year = 2019, month = 3, day = 15) + timedelta(days=3)).date()
mrt_start_day[259] = (datetime(year = 2019, month = 3, day = 22) + timedelta(days=3)).date()
mrt_start_day[260] = (datetime(year = 2019, month = 3, day = 29) + timedelta(days=3)).date()
mrt_start_day[261] = (datetime(year = 2019, month = 4, day = 12) + timedelta(days=3)).date()
mrt_start_day[262] = (datetime(year = 2019, month = 4, day = 19) + timedelta(days=3)).date()
mrt_start_day[264] = (datetime(year = 2019, month = 5, day = 10) + timedelta(days=3)).date()
mrt_start_day[265] = (datetime(year = 2019, month = 5, day = 31) + timedelta(days=3)).date()
mrt_start_day[266] = (datetime(year = 2019, month = 5, day = 31) + timedelta(days=3)).date()
mrt_start_day[267] = (datetime(year = 2019, month = 6, day = 21) + timedelta(days=3)).date()
mrt_start_day[268] = (datetime(year = 2019, month = 6, day = 28) + timedelta(days=3)).date()
mrt_start_day[269] = (datetime(year = 2019, month = 6, day = 28) + timedelta(days=3)).date()

participants_for_analysis = list(mrt_start_day.keys())

# What fraction of all available decision times is a user classified as being in the 
# unknown episode category?

indexVal = 0
avai_dec_time_stress_classes = pd.DataFrame()
for idVal in participants_for_analysis:
    print("  id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_episodes = episodes[episodes['participant_id'] == idVal]
    day = mrt_id_start_day
    while day <=  mrt_id_tenth_day:
        print("  day: ", day)
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        if available_dec_ponts.shape[0] > 0:
            available_decision_times = list(available_dec_ponts['date_time'])
            avai_dec_time_stress_class = list(available_dec_ponts['isStress'])
            for avai_dec_time, avai_dec_time_class in zip(available_decision_times, avai_dec_time_stress_class):
                # find current stress classification from cStress episode classification data file to make 
                # sure that this matches what the log files indicate: 
                curr_episode = id_episodes_day[(id_episodes_day['datetime_end'] >= avai_dec_time) & (id_episodes_day['datetime_start'] <= avai_dec_time)]
                if curr_episode.shape[0] == 0: 
                    print("WARNING: id ", idVal, " for available decision time ", avai_dec_time, "has no classification for this current episode!!!!!!")
                    ep_class = 'does_not_exist'
                elif curr_episode.shape[0] > 0:
                    if curr_episode.iloc[0].event == 3.0: 
                        ep_class = "unknown"
                    elif curr_episode.iloc[0].event == 2.0: 
                        ep_class = "stress"
                    elif curr_episode.iloc[0].event == 0.0:
                        ep_class = "no_stress"
                rows_to_append = pd.DataFrame({
                                'id': idVal,
                                'day': day,
                                'available_decision_point': avai_dec_time,
                                'rand_alg_is_stress': avai_dec_time_class, 
                                'episode_class': ep_class}, index=[indexVal])
                indexVal = indexVal + 1
                avai_dec_time_stress_classes = avai_dec_time_stress_classes.append(rows_to_append)
        day = day + timedelta(days=1)

# Create row counts in table provided in email to Tim, Soujanya, Shahin and Susan:

isStressTrue = list(avai_dec_time_stress_classes['rand_alg_is_stress'] == True)
isStressFalse = list(
    avai_dec_time_stress_classes['rand_alg_is_stress'] == False)

EpClassStress = list(avai_dec_time_stress_classes['episode_class'] == 'stress')
EpClassNoStress = list(
    avai_dec_time_stress_classes['episode_class'] == 'no_stress')
EpClassUnknown = list(
    avai_dec_time_stress_classes['episode_class'] == 'unknown')
NoEpClass = list(
    avai_dec_time_stress_classes['episode_class'] == 'does_not_exist')

# using the timestamp from the phone log files:

np.sum([i & j for (i, j) in zip(isStressTrue, EpClassStress)])
np.sum([i & j for (i, j) in zip(isStressTrue, EpClassNoStress)])
np.sum([i & j for (i, j) in zip(isStressTrue, EpClassUnknown)])
np.sum([i & j for (i, j) in zip(isStressTrue, NoEpClass)])

np.sum([i & j for (i, j) in zip(isStressFalse, EpClassStress)])
np.sum([i & j for (i, j) in zip(isStressFalse, EpClassNoStress)])
np.sum([i & j for (i, j) in zip(isStressFalse, EpClassUnknown)])
np.sum([i & j for (i, j) in zip(isStressFalse, NoEpClass)])

# Create a data frame with the following information (VAR REDUC):
#   for each individual, each day, each available decision time, create the variables:
#    y1, ..., y120 = each minute's multinomial outcome {detected-stressed, not-detected-stressed, physically-active}.
#    x1 = the number of minutes stressed in the previous 120 minutes
#    x2 = the number of minutes physically active in the previous 120 minutes
#    x3 = the current classificatin of stress or not_stress
# populate data frame with the first missing episode:

var_reduc_data = pd.DataFrame()
for idVal in participants_for_analysis:
    print("  id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == idVal]
    id_episodes = episodes[episodes['participant_id'] == idVal]
    day = mrt_id_start_day
    day_num = 1
    while day <= mrt_id_tenth_day:
        print("  day: ", day)
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        if available_dec_ponts.shape[0] > 0:
            available_decision_times = list(available_dec_ponts['date_time'])
            available_dec_time_is_stress_list = list(available_dec_ponts['isStress'])
            for avai_dec_time, avai_dec_time_is_stress in zip(available_decision_times, available_dec_time_is_stress_list):
                # variables: day, avai_dec_time,
                start_time = avai_dec_time
                plus_120_min_time = start_time + timedelta(hours = 2)
                minus_120_min_time = start_time - timedelta(hours = 2)
                id_episodes_day_2hour_before = id_episodes_day[(id_episodes_day['datetime_end'] >= minus_120_min_time) & (id_episodes_day['datetime_start'] <= start_time)].reset_index(drop=True)
                id_activity_day_2hour_before = id_activity_day[(id_activity_day['datetime'] >= minus_120_min_time) & (id_activity_day['datetime'] <= start_time)].reset_index(drop=True)
                id_episodes_day_2hour_after = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= plus_120_min_time)].reset_index(drop=True)
                id_activity_day_2hour_after = id_activity_day[(id_activity_day['datetime'] >= start_time) & (
                    id_activity_day['datetime'] <= plus_120_min_time)].reset_index(drop=True)
                # count the number of minutes in the prior 2 hours that are within detected-stressed episode(s):
                mins_stressed_prior = 0
                id_stress_eps_2hour_before = id_episodes_day_2hour_before[id_episodes_day_2hour_before['event'] == 2.0].reset_index(
                    drop=True)
                if id_stress_eps_2hour_before.shape[0] > 0:
                    for id, row in id_stress_eps_2hour_before.iterrows():
                        start_val = np.max([minus_120_min_time, row.datetime_start])
                        end_val = np.min([start_time, row.datetime_end])
                        mins_stressed_prior += (minute_rounder(end_val) - minute_rounder(start_val)).seconds//60
                # count the number of minutes in the prior 2 hours that are within not-detected-stressed episode(s):
                mins_not_stressed_prior = 0
                id_not_stress_eps_2hour_before = id_episodes_day_2hour_before[id_episodes_day_2hour_before['event'] == 0.0].reset_index(
                    drop=True)
                if id_not_stress_eps_2hour_before.shape[0] > 0:
                    for id, row in id_not_stress_eps_2hour_before.iterrows():
                        start_val = np.max([minus_120_min_time, row.datetime_start])
                        end_val = np.min([start_time, row.datetime_end])
                        mins_not_stressed_prior += (minute_rounder(end_val) - minute_rounder(start_val)).seconds//60
                # and the number of minutes in the prior 2 hours that are within physical activity episode(s):
                mins_active_prior = 0
                id_unknown_eps_2hour_before = id_episodes_day_2hour_before[id_episodes_day_2hour_before['event'] == 3.0].reset_index(drop=True)
                id_activity_2hour_before = id_activity_day_2hour_before[id_activity_day_2hour_before['event'] == 1.0].reset_index(
                    drop=True)
                if id_unknown_eps_2hour_before.shape[0] > 0:
                    for index,row in id_unknown_eps_2hour_before.iterrows():
                        start_of_unknown_ep = row.datetime_start
                        end_of_unknown_ep = row.datetime_end
                        num_mins_in_ep = (minute_rounder(end_of_unknown_ep) - minute_rounder(start_of_unknown_ep)).seconds//60
                        id_activity_curr_episode = id_activity_2hour_before[(id_activity_2hour_before['datetime'] >= start_of_unknown_ep) & (
                            id_activity_2hour_before['datetime'] <= end_of_unknown_ep)].reset_index(drop=True)
                        if id_activity_curr_episode.shape[0] >= num_mins_in_ep/2:
                            mins_active_prior += num_mins_in_ep
                min_counter = 0
                start_of_curr_time = start_time
                for id, row in id_episodes_day_2hour_after.iterrows():
                    if start_of_curr_time >= plus_120_min_time:
                        break
                    ep_consisting_of_min = id_episodes_day_2hour_after[(id_episodes_day_2hour_after['datetime_start'] <= start_of_curr_time) & (
                        id_episodes_day_2hour_after['datetime_end'] > start_of_curr_time)]
                    if ep_consisting_of_min.shape[0] == 0:
                        # If entering this if statement, current episode is missing. 
                        print("!!! Either no first episode, or missing data !!!")
                        # find next available episode, if it exists: 
                        id_plus_one = id + 1
                        if id_plus_one == id_episodes_day_2hour_after.shape[0]: 
                            # this means that there is no current episode classification and also no 
                            # other episode classifications until the end of the 120 minute period: 
                            start_of_curr_ep = start_of_curr_time
                            end_of_curr_ep = plus_120_min_time
                            num_mins_in_ep = (minute_rounder(end_of_curr_ep) - minute_rounder(start_of_curr_ep)).seconds//60
                            # populate minute and outcome rows:
                            minute_vals = list(range(min_counter + 1, min_counter + num_mins_in_ep + 1))
                            outcome_val = "missing"
                            outcome_vals = [outcome_val] * len(minute_vals)
                            rows_to_append = pd.DataFrame({
                                'id': [idVal] * len(minute_vals),
                                'day': [day] * len(minute_vals),
                                'daynum': [day_num] * len(minute_vals),
                                'available_decision_point': [avai_dec_time] * len(minute_vals),
                                'avai_dec_time_is_stress_vals': [avai_dec_time_is_stress] * len(minute_vals), 
                                'min_after_dec_point': minute_vals,
                                'prox_outcome': outcome_vals,
                                'mins_stressed_prior': [mins_stressed_prior] * len(minute_vals),
                                'mins_active_prior': [mins_active_prior] * len(minute_vals)})
                            var_reduc_data = var_reduc_data.append(rows_to_append)
                            start_of_curr_time = end_of_curr_ep
                            min_counter += num_mins_in_ep
                        else: 
                            next_ep = id_episodes_day_2hour_after.iloc[id_plus_one]
                            if next_ep.shape[0] > 0: 
                                start_of_next_ep = next_ep.datetime_start
                                start_of_curr_ep = start_of_curr_time
                                end_of_curr_ep = start_of_next_ep
                                num_mins_in_ep = (minute_rounder(end_of_curr_ep) - minute_rounder(start_of_curr_ep)).seconds//60
                                # populate minute and outcome rows:
                                minute_vals = list(range(min_counter + 1, min_counter + num_mins_in_ep + 1))
                                outcome_val = "missing"
                                outcome_vals = [outcome_val] * len(minute_vals)
                                rows_to_append = pd.DataFrame({
                                    'id': [idVal] * len(minute_vals),
                                    'day': [day] * len(minute_vals),
                                    'daynum': [day_num] * len(minute_vals),
                                    'available_decision_point': [avai_dec_time] * len(minute_vals),
                                    'avai_dec_time_is_stress_vals': [avai_dec_time_is_stress] * len(minute_vals),
                                    'min_after_dec_point': minute_vals,
                                    'prox_outcome': outcome_vals,
                                    'mins_stressed_prior': [mins_stressed_prior] * len(minute_vals),
                                    'mins_active_prior': [mins_active_prior] * len(minute_vals)})
                                var_reduc_data = var_reduc_data.append(rows_to_append)
                                start_of_curr_time = end_of_curr_ep
                                min_counter += num_mins_in_ep
                            else: 
                                # there is no next episode, so use end time to be the end of the 120 mins: 
                                # start_of_next_ep = next_ep.iloc[0].datetime_start
                                start_of_curr_ep = start_of_curr_time
                                end_of_curr_ep = plus_120_min_time
                                num_mins_in_ep = (minute_rounder(end_of_curr_ep) - minute_rounder(start_of_curr_ep)).seconds//60
                                # populate minute and outcome rows:
                                minute_vals = list(range(min_counter + 1, min_counter + num_mins_in_ep + 1))
                                outcome_val = "missing"
                                outcome_vals = [outcome_val] * len(minute_vals)
                                rows_to_append = pd.DataFrame({
                                    'id': [idVal] * len(minute_vals),
                                    'day': [day] * len(minute_vals),
                                    'daynum': [day_num] * len(minute_vals),
                                    'available_decision_point': [avai_dec_time] * len(minute_vals),
                                    'avai_dec_time_is_stress_vals': [avai_dec_time_is_stress] * len(minute_vals),
                                    'min_after_dec_point': minute_vals,
                                    'prox_outcome': outcome_vals,
                                    'mins_stressed_prior': [mins_stressed_prior] * len(minute_vals),
                                    'mins_active_prior': [mins_active_prior] * len(minute_vals)})
                                var_reduc_data = var_reduc_data.append(rows_to_append)
                                start_of_curr_time = end_of_curr_ep
                                min_counter += num_mins_in_ep
                    elif ep_consisting_of_min.shape[0] == 1:
                        start_of_curr_ep = np.max([ep_consisting_of_min.iloc[0].datetime_start, start_of_curr_time])
                        end_of_curr_ep = np.min([plus_120_min_time, ep_consisting_of_min.iloc[0].datetime_end])
                        num_mins_in_ep = (minute_rounder(end_of_curr_ep) - minute_rounder(start_of_curr_ep)).seconds//60
                        # populate minute and outcome rows:
                        minute_vals = list(range(min_counter + 1, min_counter + num_mins_in_ep + 1))
                        if ep_consisting_of_min.iloc[0].event == 2.0:
                            outcome_val = 'detected-stressed'
                        elif ep_consisting_of_min.iloc[0].event == 0.0:
                            outcome_val = 'not-detected-stressed'
                        elif ep_consisting_of_min.iloc[0].event == 3.0:
                            active_mins_df = id_activity_day_2hour_after[id_activity_day_2hour_after['event'] == 1.0]
                            id_activity_curr_episode = active_mins_df[(
                                active_mins_df['datetime'] >= start_of_curr_ep) & (active_mins_df['datetime'] <= end_of_curr_ep)]
                            if id_activity_curr_episode.shape[0] >= num_mins_in_ep/2:
                                # this unknown ep is due to activity:
                                outcome_val = "physically_active"
                            else:
                                outcome_val = "missing"
                        outcome_vals = [outcome_val] * len(minute_vals)
                        rows_to_append = pd.DataFrame({
                            'id': [idVal] * len(minute_vals),
                            'day': [day] * len(minute_vals),
                            'daynum': [day_num] * len(minute_vals),
                            'available_decision_point': [avai_dec_time] * len(minute_vals),
                            'avai_dec_time_is_stress_vals': [avai_dec_time_is_stress] * len(minute_vals),
                            'min_after_dec_point': minute_vals,
                            'prox_outcome': outcome_vals,
                            'mins_stressed_prior': [mins_stressed_prior] * len(minute_vals),
                            'mins_active_prior': [mins_active_prior] * len(minute_vals)})
                        var_reduc_data = var_reduc_data.append(rows_to_append)
                        start_of_curr_time = ep_consisting_of_min.iloc[0].datetime_end
                        min_counter += num_mins_in_ep
        day = day + timedelta(days=1)
        day_num = day_num + 1

# export dataset:
var_reduc_data.to_csv('var_reduc_data_df.csv')

var_reduc_data2 = pd.read_csv("var_reduc_data_df.csv") 

# Create dictionary that records for each id, for each day from day 0 to day 9:
# - proportion good qual data previous day
# - proportion good phone battery previous day
# - proportion data available previous day
# - proportion physical activity previous day

bad_qual_ecg_props = {}
bad_qual_rep_props = {}
activity_props = {}
for id in participants_for_analysis:
    # start on the day before the first mrt day:
    qual_id_start_day = mrt_start_day[id] - timedelta(days=1)
    qual_id_tenth_day = qual_id_start_day + timedelta(days=9)
    id_qual_ecg_full = quality_ecg[quality_ecg['participant_id'] == id]
    id_qual_ecg_mrt = id_qual_ecg_full[(id_qual_ecg_full['date'] >= qual_id_start_day) & (id_qual_ecg_full['date'] <= qual_id_tenth_day)]
    id_qual_rep_full = quality_rep[quality_rep['participant_id'] == id]
    id_qual_rep_mrt = id_qual_rep_full[(id_qual_rep_full['date'] >= qual_id_start_day) & (id_qual_rep_full['date'] <= qual_id_tenth_day)]
    id_activity_full = activity[activity['participant_id'] == id]
    id_activity_mrt = id_activity_full[(id_activity_full['date'] >= qual_id_start_day) & (id_activity_full['date'] <= qual_id_tenth_day)]
    # Check if participants have given start and end time of days:
    # day_start_id = day_start[day_start['participant_id'] == id]
    # day_start_id_mrt = day_start_id[day_start_id['date'] >= mrt_id_start_day]
    # day_end_id = day_end[day_end['participant_id'] == id]
    # day_end_id_mrt = day_end_id[day_end_id['date'] >= mrt_id_start_day]
    #
    day = qual_id_start_day
    bad_qual_ecg_props[id] = []
    bad_qual_rep_props[id] = []
    activity_props[id] = []
    print(id)
    print("")
    while day <=  qual_id_tenth_day:
        id_qual_ecg_mrt_day = id_qual_ecg_mrt[id_qual_ecg_mrt['date'] == day].reset_index(drop=True)
        num_rows_ecg = id_qual_ecg_mrt_day.shape[0]
        #
        id_qual_rep_mrt_day = id_qual_rep_mrt[id_qual_rep_mrt['date'] == day].reset_index(drop=True)
        num_rows_rep = id_qual_rep_mrt_day.shape[0]
        #
        id_activity_mrt_day = id_activity_mrt[id_activity_mrt['date'] == day].reset_index(drop=True)
        num_rows_act = id_activity_mrt_day.shape[0]
        #
        # every row is meant to give a qual measure for a 2 second period.
        # So, num_rows /(60*60) = num hours of day.
        if num_rows_ecg == 0:
            string = 'Participant ' + str(id) + ' does not have any ECG Quality information on day ' + str(day_num)
            print(string)
            bad_qual_ecg_props[id].append(np.nan)
        else:
            prop_bad_qual_ecg = (id_qual_ecg_mrt_day[id_qual_ecg_mrt_day['event'] != 0.0].shape[0])/num_rows_ecg
            bad_qual_ecg_props[id].append(round(prop_bad_qual_ecg,2))
        #
        if num_rows_rep == 0:
            string = 'Participant ' + str(id) + ' does not have any RIP Quality information on day ' + str(day_num)
            print(string)
            bad_qual_rep_props[id].append(np.nan)
        else:
            prop_bad_qual_rep = (id_qual_rep_mrt_day[id_qual_rep_mrt_day['event'] != 0.0].shape[0])/num_rows_rep
            bad_qual_rep_props[id].append(round(prop_bad_qual_rep,2))
        #
        if num_rows_act == 0:
            string = 'Participant ' + str(id) + ' does not have any activity information on day ' + str(day_num)
            print(string)
            activity_props[id].append(np.nan)
        else:
            prop_act = (id_activity_mrt_day[id_activity_mrt_day['event'] == 1.0].shape[0])/num_rows_act
            activity_props[id].append(round(prop_act,2))
        day =  day + timedelta(days=1)


#######################################################################################
# Find fraction:
# numer = Number of stress & not-stress episodes that resulted in no intervention being
#         sent that also had interventions sent within the subsequent 2 hour period.
# denom = Number of stress & not-stress episodes that resulted in no intervention being
#         sent.
#######################################################################################
num_trigs_after_not_trig_dec_time = {}
for id in participants_for_analysis:
    print("id: ", id)
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == id]
    id_episodes = episodes[episodes['participant_id'] == id]
    day = mrt_id_start_day
    num_trigs_after_not_trig_dec_time[id] = {}
    while day <=  mrt_id_tenth_day:
        print("  on day : ", day)
        num_trigs_after_not_trig_dec_time[id][day] = []
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        # denom: number of stress and not-stress episodes randomized to no message.
        not_trig = id_log_EMI_day[int_not_triggered_condition]
        # numer: number of stress and not-stress episodes randomized to no message for which
        #        within the following 2 hours a message was delivered to the user.
        trig = id_log_EMI_day[int_triggered_condition]
        # trig['date_time_aware'] = [pd.to_datetime(i).tz_localize('America/Chicago', ambiguous = 'NaT') for i in trig['date_time']]
        if not_trig.shape[0] > 0:
            not_trig_times = list(not_trig['date_time'])
            for not_trig_time in not_trig_times:
                # start_time = pd.to_datetime(not_trig_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                start_time = not_trig_time
                # if start_time == 'NaT':
                #     start_time_localize = pd.to_datetime(not_trig_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                # count number of trigs in the two hour window:
                if trig.shape[0] > 0:
                    trig_two_hours = trig[(trig['date_time'] >= start_time) & (
                        trig['date_time'] <= end_time)]
                    num_trigs_2_hr_no_int = trig_two_hours.shape[0]
                else:
                    num_trigs_2_hr_no_int = 0
                num_trigs_after_not_trig_dec_time[id][day].append(num_trigs_2_hr_no_int)
        print("    ", num_trigs_after_not_trig_dec_time[id][day])
        day = day + timedelta(days=1)

# Now produce this fraction for each individual and also on average across individuals:
frac = {}
for id in participants_for_analysis:
    frac[id] = []
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    day = mrt_id_start_day
    while day <=  mrt_id_tenth_day:
        if len(num_trigs_after_not_trig_dec_time[id][day]) != 0:
            numer = sum(i > 0 for i in num_trigs_after_not_trig_dec_time[id][day])
            denom = len(num_trigs_after_not_trig_dec_time[id][day])
            frac_val = numer/denom
            frac[id].append(round(frac_val,2))
        else:
            frac[id].append(np.nan)
        day = day + timedelta(days=1)

# Average frac for each user:
average_per_user_frac = {}
for id in participants_for_analysis:
    if len(frac[id]) == 0:
        average_per_user_frac[id] = np.nan
    else:
        average_per_user_frac[id] = round(np.nanmean(frac[id]), 2)

# average across all users:
ave_frac_across_all_users = round(np.nanmean(list(average_per_user_frac.values())), 2)
#######################################################################################


# look at all available decision times at which a treatment is delivered. Of these what fraction
# of user-decision times have another treatment within 120 min?

num_trigs_after_trig_dec_time = {}
for id in participants_for_analysis:
    print("id: ", id)
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    day = mrt_id_start_day
    num_trigs_after_trig_dec_time[id] = {}
    while day <=  mrt_id_tenth_day:
        print("  on day : ", day)
        num_trigs_after_trig_dec_time[id][day] = []
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        # number of stress and not-stress episodes randomized to no message for which
        # within the following 2 hours a message was delivered to the user:
        trig = id_log_EMI_day[int_triggered_condition]
        # trig['date_time_aware'] = [pd.to_datetime(i).tz_localize('America/Chicago', ambiguous = 'NaT') for i in trig['date_time']]
        if trig.shape[0] > 0:
            trig_times = list(trig['date_time'])
            for trig_time in trig_times:
                start_time = trig_time
                # end_time = start_time + timedelta(hours = 2)
                # the next line is a check to make sure no messages were delivered in the following 60 minutes
                # following an available decision time:
                end_time = start_time + timedelta(hours = 1)
                # count number of trigs in the two hour window:
                trig_two_hours = trig[(trig['date_time'] > start_time) & (trig['date_time'] <= end_time)]
                num_trigs_2_hr_int = trig_two_hours.shape[0]
                num_trigs_after_trig_dec_time[id][day].append(num_trigs_2_hr_int)
        else:
            num_trigs_after_trig_dec_time[id][day].append(np.nan)
        print("    ", num_trigs_after_trig_dec_time[id][day])
        day = day + timedelta(days=1)

# check if anyone gets delivered 2 interventions in the 2 hours following an available
# decision time in which they are provided an intervention:

for id in participants_for_analysis:
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    day = mrt_id_start_day
    while day <=  mrt_id_tenth_day:
        for el in num_trigs_after_trig_dec_time[id][day]:
            if el > 0:
                print("ID: ", id, "  DAY: ", day, "  ELEMENT: ", el)
        day = day + timedelta(days=1)
# 60 mins:
# ID:  202   DAY:  2017-07-08   ELEMENT:  1 !!
# ID:  224   DAY:  2018-01-25   ELEMENT:  1 !!
# ID:  226   DAY:  2018-02-12   ELEMENT:  1 !!

# Now produce this fraction for each individual and also on average across individuals:
frac = {}
for id in participants_for_analysis:
    frac[id] = []
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    day = mrt_id_start_day
    while day <=  mrt_id_tenth_day:
        if np.isnan(num_trigs_after_trig_dec_time[id][day][0]):
            frac[id].append(np.nan)
        elif len(num_trigs_after_trig_dec_time[id][day]) != 0:
            numer = sum(i > 0 for i in num_trigs_after_trig_dec_time[id][day])
            denom = len(num_trigs_after_trig_dec_time[id][day])
            frac_val = numer/denom
            frac[id].append(round(frac_val,2))
        day = day + timedelta(days=1)

# Average frac for each user:
average_per_user_frac = {}
for id in participants_for_analysis:
    if len(frac[id]) == 0:
        average_per_user_frac[id] = np.nan
    else:
        average_per_user_frac[id] = round(np.nanmean(frac[id]), 2)

# average across all users:
ave_frac_across_all_users = round(np.nanmean(list(average_per_user_frac.values())), 2)
#######################################################################################




# Create dataset for predicting missing minutes:

# predict_missing_columns = ['id', 'day', 'available_decision_time', 'episode_type',
#     'previous_episode_type', 'length_of_episode', 'length_of_previous_episode',
#     'prop_good_data', 'prop_good_data_previous_episode']
# predict_missing_df = pd.DataFrame(columns = predict_missing_columns)

# add percent good quality data previous day
# add percent battery high previous day
# add has lapsed ?
# add number of prompts so far (maybe they are getting sick of prompts?)

predict_missing_df = pd.DataFrame()
indexVal = 0
for idVal in participants_for_analysis:
    print("id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == idVal]
    id_episodes = episodes[episodes['participant_id'] == idVal]
    day = mrt_id_start_day
    day_num = 1 
    num_ints_trig_prev_day = 0  
    while day <= mrt_id_tenth_day:
        print("day: ", day)
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        if available_dec_ponts.shape[0] > 0:
            # an available decision time must either be a minute after the peak of either a 
            # detected stressed or not able to detect as stressed episode. Note time and 
            # episode type of each available decision time: 
            available_decision_times = list(available_dec_ponts['date_time'])
            available_decision_time_stress = list(available_dec_ponts['isStress'])
            for avai_dec_time, avai_dec_time_ep_type in zip(available_decision_times, available_decision_time_stress):
                start_time = avai_dec_time
                # start_time = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                # if start_time == 'NaT':
                #     start_time_localize = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                id_episodes_day_2hour = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= end_time)]
                id_activity_day_2hour = id_activity_day[(id_activity_day['datetime'] >= start_time) & (id_activity_day['datetime'] <= end_time)]
                if id_episodes_day_2hour.shape[0] == 0:
                    # This means that there is no current episode recorded in the data, nor for the next 120 minutes!!
                    print("WARNING 1: id ", idVal, " for available decision time ", avai_dec_time, "has no classified episodes from current t to t + 120 minutes!!!!!!")
                else:
                    # Check to see if there is no current classified episode in the data. THIS SHOULD NOT HAPPEN!: 
                    # (e.g., is avai_dec_time within the first row's start and end time?)
                    if (not (id_episodes_day_2hour.iloc[0].datetime_start <= start_time <= id_episodes_day_2hour.iloc[0].datetime_end)): 
                        print("WARNING 2: id ", idVal, " for available decision time ", avai_dec_time, "has no classified episode for current t!!!!!!")
                    # check if the current episode is classified as unknown. THIS SHOULD NOT HAPPEN!
                    elif id_episodes_day_2hour.iloc[0].event == 3.0: 
                        print("WARNING 3: id ", idVal, " for available decision time ", avai_dec_time, "is classified as being within an UNKNOWN episode!!!!!!")
                    else: 
                        # find previous episodes: 
                        prev_eps = id_episodes_day[id_episodes_day['datetime_end'] < start_time]
                        if prev_eps.shape[0] == 0:
                            # this should mean there are no previous daily episodes detected because this
                            # is the start of the day as recognised by the randomization algorithm:
                            prev_ep_type = 'no_previous_daily_episodes'
                            prev_ep_length = np.nan
                        else:
                            # prev ep could be missing. check this by seeing if the start time of the current episode (the one in 
                            # which lies the available decision time) appears as the end time of a previous episode: 
                            prev_ep = prev_eps.iloc[prev_eps.shape[0] - 1]
                            if not id_episodes_day_2hour.iloc[0].datetime_start == prev_ep.datetime_end: 
                                # this means that the previous episode is missing
                                prev_ep_type = 'missing'
                            else: 
                                # this means that the previous episode is not missing: 
                                if prev_ep.event == 0.0:
                                    prev_ep_type = 'no_stress'
                                elif prev_ep.event == 2.0:
                                    prev_ep_type = 'stress'
                                elif prev_ep.event == 3.0:
                                    df = id_activity_day[(id_activity_day['datetime'] >= prev_ep.datetime_start) & (id_activity_day['datetime'] <= prev_ep.datetime_end)]
                                    active_mins = df[df['event'] == 1.0].shape[0]
                                    if active_mins >= ((minute_rounder(prev_ep.datetime_end) - minute_rounder(prev_ep.datetime_start)).seconds//60)/2:
                                        # this unknown ep is due to activity:
                                        prev_ep_type = "physically_active"
                                    else:
                                        prev_ep_type = "missing"
                            prev_ep_length = (minute_rounder(prev_ep.datetime_end) - minute_rounder(prev_ep.datetime_start)).seconds//60
                            # record available_dec_time ep type and ep length: 
                            if avai_dec_time_ep_type: 
                                available_decision_point_episode_type_val = "stress"
                            else: 
                                available_decision_point_episode_type_val = "no_stress"
                            avai_dec_time_ep = id_episodes_day_2hour.iloc[0]
                            avai_dec_time_ep_length_val = (minute_rounder(avai_dec_time) - minute_rounder(avai_dec_time_ep.datetime_start)).seconds//60
                        # Now start iterating through the episodes following the available decision time episode, whilst tracking missing minutes
                        # in-between until 120 minutes is up:
                        prev_end_time = id_episodes_day_2hour.iloc[0].datetime_start
                        for id, row in id_episodes_day_2hour.iterrows():
                            if row.datetime_start != prev_end_time:
                                # we have found a missing episode in-between prev and current row,
                                # so count missing minutes:
                                ep_type = "missing"
                                ep_length = (minute_rounder(row.datetime_start) - minute_rounder(prev_end_time)).seconds//60
                                row_to_append = pd.DataFrame({
                                    'id': idVal,
                                    'day': day,
                                    'daynum': day_num,
                                    'available_decision_point': avai_dec_time,
                                    'available_decision_point_episode_type': available_decision_point_episode_type_val,
                                    'available_decision_point_episode_length': avai_dec_time_ep_length_val,
                                    'curr_ep_type': ep_type,
                                    'curr_ep_length': ep_length,
                                    'previous_episode_type': prev_ep_type,
                                    'previous_episode_length': prev_ep_length,
                                    'prev_day_activity_prop': activity_props[idVal][day_num - 1],
                                    'prev_day_bad_qual_rep_prop': bad_qual_rep_props[idVal][day_num - 1],
                                    'prev_day_bad_qual_ecg_prop': bad_qual_ecg_props[idVal][day_num - 1],
                                    'num_ints_trig_prev_day': num_ints_trig_prev_day}, index=[indexVal])
                                indexVal = indexVal + 1
                                predict_missing_df = predict_missing_df.append(row_to_append)
                                prev_ep_type = ep_type
                                prev_ep_length = ep_length
                                prev_end_time = row.datetime_start
                            else: 
                                # Now append current row info:
                                ep_length = (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                                if row.event == 2.0:
                                    ep_type = "stress"
                                elif row.event == 0.0:
                                    ep_type = "no_stress"
                                elif row.event == 3.0:
                                    df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                                    active_mins = df[df['event'] == 1.0].shape[0]
                                    if active_mins >= ((minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60)/2:
                                        # this unknown ep is due to activity:
                                        ep_type = "physically_active"
                                    else:
                                        ep_type = "missing"
                                row_to_append = pd.DataFrame({
                                    'id': idVal,
                                    'day': day,
                                    'daynum': day_num,
                                    'available_decision_point': avai_dec_time,
                                    'available_decision_point_episode_type': available_decision_point_episode_type_val,
                                    'available_decision_point_episode_length': avai_dec_time_ep_length_val,
                                    'curr_ep_type': ep_type,
                                    'curr_ep_length': ep_length,
                                    'previous_episode_type': prev_ep_type,
                                    'previous_episode_length': prev_ep_length,
                                    'prev_day_activity_prop': activity_props[idVal][day_num - 1],
                                    'prev_day_bad_qual_rep_prop': bad_qual_rep_props[idVal][day_num - 1],
                                    'prev_day_bad_qual_ecg_prop': bad_qual_ecg_props[idVal][day_num - 1],
                                    'num_ints_trig_prev_day': num_ints_trig_prev_day}, index=[indexVal])
                                indexVal = indexVal + 1
                                predict_missing_df = predict_missing_df.append(row_to_append)
                                prev_ep_length = ep_length
                                prev_ep_type = ep_type
                                prev_end_time = row.datetime_end
                    # avai_dec_time_count += 1
        num_ints_trig_prev_day = id_log_EMI_day[int_triggered_condition].shape[0]
        day = day + timedelta(days=1)
        day_num = day_num + 1

                    # if start_time < id_episodes_day_2hour.iloc[0]['datetime_start']:
                    #     # start time is before first classified episode. So, there are missing episodes.
                    #     # For now count the missing minutes until the first classified episode as a missing
                    #     # episode:
                    #     time_missing = (minute_rounder(id_episodes_day_2hour.iloc[0]['datetime_start']) - minute_rounder(start_time)).seconds//60
                    #     # find previous classified episode that exists (if it exists) from start time
                    #     # of this 120 minute window:
                    #     if id_episodes[id_episodes['datetime_end'] < start_time].shape[0] > 0:
                    #         # find missing minutes from before start time:
                    #         time_prev_ep = (minute_rounder(start_time) - minute_rounder(id_episodes[id_episodes['datetime_end'] < start_time].iloc[-1]['datetime_end'])).seconds//60
                    #         type_prev_ep = "missing"
                    #     else:
                    #         time_prev_ep = np.nan
                    #         type_prev_ep = np.nan
                    #     # populate data frame with the first missing episode:
                    #     row_to_append = pd.DataFrame({
                    #         'id': idVal,
                    #         'day': day,
                    #         'daynum': day_num,
                    #         'available_decision_point': avai_dec_time,
                    #         'episode_type': 'missing',
                    #         'episode_length': time_missing,
                    #         'previous_episode_type': type_prev_ep,
                    #         'previous_episode_length': time_prev_ep,
                    #         'prev_day_activity_prop': activity_props[idVal][day_num - 1],
                    #         'prev_day_bad_qual_rep_prop': bad_qual_rep_props[idVal][day_num - 1],
                    #         'prev_day_bad_qual_ecg_prop': bad_qual_ecg_props[idVal][day_num - 1],
                    #         'num_ints_trig_prev_day': num_ints_trig_prev_day}, index=[indexVal])
                    #     indexVal = indexVal + 1
                    #     predict_missing_df = predict_missing_df.append(row_to_append)
                    #     prev_ep_length = time_missing
                    #     prev_ep_type = 'missing'
                    # else:
                        # if we've reached here, we know that the start time is inside a classified
                        # episode. Find the episode type before this episode:
                        

# Build model to predict missingness:
missing_df = pd.DataFrame()
missing_df['id'] = predict_missing_df['id']
missing_df['day'] = predict_missing_df['day']
missing_df['day_num'] = predict_missing_df['daynum']
missing_df['available_decision_point'] = predict_missing_df['available_decision_point']
missing_df['available_decision_point_stress_episode'] = np.where(predict_missing_df['available_decision_point_episode_type'] == 'stress', 1, 0)
missing_df['episode_type_miss'] = np.where(predict_missing_df['curr_ep_type'] == "missing", 1, 0)
missing_df['episode_type_stress'] = np.where(predict_missing_df['curr_ep_type'] == "stress", 1, 0)
missing_df['episode_type_no_stress'] = np.where(predict_missing_df['curr_ep_type'] == "no_stress", 1, 0)
missing_df['episode_length'] = predict_missing_df['curr_ep_length']
missing_df['previous_episode_miss'] = np.where(predict_missing_df['previous_episode_type'] == "missing", 1, 0)
missing_df['previous_episode_stress'] = np.where(predict_missing_df['previous_episode_type'] == "stress", 1, 0)
missing_df['previous_episode_no_stress'] = np.where(predict_missing_df['previous_episode_type'] == "no_stress", 1, 0)
missing_df['previous_episode_length'] = predict_missing_df['previous_episode_length']
missing_df['prev_day_activity_prop'] = predict_missing_df['prev_day_activity_prop']
missing_df['prev_day_bad_qual_rep_prop'] = predict_missing_df['prev_day_bad_qual_rep_prop']
missing_df['prev_day_bad_qual_ecg_prop'] = predict_missing_df['prev_day_bad_qual_ecg_prop']
missing_df['num_ints_trig_prev_day'] = predict_missing_df['num_ints_trig_prev_day']

# export dataset:
missing_df.to_csv('predict_missing_logistic_df.csv')

# How many decision points do we have?

decision_points = {} ; available_decision_points = {}
ints_triggered = {} ; ints_not_triggered = {}
trigg_stress = {} ; trigg_not_stress = {}
trigg_stress_prelapse = {} ; trigg_stress_postlapse = {}
trigg_not_stress_prelapse = {} ; trigg_not_stress_postlapse = {}
pre_lapse_day_vals = {} ; available_s_pre_dec_points = {}
available_s_post_dec_points = {} ; available_ns_pre_dec_points = {}
available_ns_post_dec_points = {} ; not_missing_mins = {}
not_missing_mins_frac = {}  ;  total_bad_mins = {}
total_stress_mins = {}
total_not_stress_mins = {}
total_physical_active_mins = {}
for id in participants_for_analysis:
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == id]
    id_episodes = episodes[episodes['participant_id'] == id]
    day = mrt_id_start_day
    decision_points[id] = [] ; available_decision_points[id] = []
    ints_triggered[id] = [] ; ints_not_triggered[id] = []
    trigg_stress[id] = [] ; trigg_not_stress[id] = []
    trigg_stress_prelapse[id] = [] ; trigg_stress_postlapse[id] = []
    trigg_not_stress_prelapse[id] = [] ; trigg_not_stress_postlapse[id] = []
    pre_lapse_day_vals[id] = [] ; available_s_pre_dec_points[id] = []
    available_s_post_dec_points[id] = [] ; available_ns_pre_dec_points[id] = []
    available_ns_post_dec_points[id] = [] ; not_missing_mins[id] = {}
    not_missing_mins_frac[id] = {}
    total_bad_mins[id] = {}
    total_stress_mins[id] = {}
    total_not_stress_mins[id] = {}
    total_physical_active_mins[id] = {}
    while day <=  mrt_id_tenth_day:
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        available_condition = id_log_EMI_day['message'] == 'true: all conditions okay'
        unavailable_condition = id_log_EMI_day['message'] == 'false: some conditions are failed'
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        # calculate ave. no. of ints:
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        # from each decision point, calculate the minutes in the following 120 minute window
        # that are (1) in a stress episode; (2) in a not-able-to-classify-as-stress episode; and
        # (3) unknown due to physical activity. Then calculate the fraction of the 120 minute
        # window this corresponds to:
        not_missing_mins[id][day] = []
        not_missing_mins_frac[id][day] = []
        total_bad_mins[id][day] = []
        total_stress_mins[id][day] = []
        total_not_stress_mins[id][day] = []
        total_physical_active_mins[id][day] = []
        if available_dec_ponts.shape[0] > 0:
            available_decision_times = list(available_dec_ponts['date_time'])
            for avai_dec_time in available_decision_times:
                start_time = avai_dec_time
                # start_time = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                # if start_time == 'NaT':
                #     start_time_localize = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                id_episodes_day_2hour = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= end_time)]
                id_activity_day_2hour = id_activity_day[(id_activity_day['datetime'] >= start_time) & (id_activity_day['datetime'] <= end_time)]
                # count minutes stressed:
                stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 2.0]
                stress_min_count = 0
                if stress_eps.shape[0] > 0:
                    for index, row in stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                # count minutes not stressed:
                not_stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 0.0]
                not_stress_min_count = 0
                if not_stress_eps.shape[0] > 0:
                    for index, row in not_stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            not_stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                # count minutes active inside unknown episodes:
                unknown_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 3.0]
                unknown_due_to_activity_mins = 0
                unknown_due_to_bad_data_mins = 0
                if unknown_eps.shape[0] > 0:
                    for index, row in unknown_eps.iterrows():
                        if row.datetime_start <= start_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= start_time) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        elif row.datetime_end >= end_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= end_time)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        else:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        #
                        if active_mins >= ((minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60)/2:
                            # this episode is unknown due to activity
                            if row.datetime_start <= start_time:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_activity_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            if row.datetime_start <= start_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                                # this episode is unknown due to bad quality:
                # if (stress_min_count > 0) & (not_stress_min_count > 0) & (unknown_due_to_activity_mins > 0):
                #     print(id)
                #     print(day)
                #     print(avai_dec_time)
                total_stress_mins_val = round(stress_min_count, 2)
                total_not_stress_mins_val = round(not_stress_min_count, 2)
                total_physical_active_mins_val = round(unknown_due_to_activity_mins, 2)
                total_stress_mins[id][day].append(total_stress_mins_val)
                total_not_stress_mins[id][day].append(total_not_stress_mins_val)
                total_physical_active_mins[id][day].append(total_physical_active_mins_val)
                total_mins = stress_min_count + not_stress_min_count + unknown_due_to_activity_mins
                total_mins_frac = round(total_mins/float(120),1)
                not_missing_mins[id][day].append(total_mins)
                not_missing_mins_frac[id][day].append(total_mins_frac)
                total_bad_mins[id][day].append(unknown_due_to_bad_data_mins)
        #
        available_s_pre = available_dec_ponts[(available_dec_ponts['isStress'] == True) & (available_dec_ponts['isPreLapse'] == True)]
        available_s_post = available_dec_ponts[(available_dec_ponts['isStress'] == True) & (available_dec_ponts['isPreLapse'] == False)]
        available_ns_pre = available_dec_ponts[(available_dec_ponts['isStress'] == False) & (available_dec_ponts['isPreLapse'] == True)]
        available_ns_post = available_dec_ponts[(available_dec_ponts['isStress'] == False) & (available_dec_ponts['isPreLapse'] == False)]
        available_s_pre_dec_points[id].append(available_s_pre.shape[0])
        available_s_post_dec_points[id].append(available_s_post.shape[0])
        available_ns_pre_dec_points[id].append(available_ns_pre.shape[0])
        available_ns_post_dec_points[id].append(available_ns_post.shape[0])
        trig = id_log_EMI_day[int_triggered_condition]
        not_trig =id_log_EMI_day[int_not_triggered_condition]
        trigg_stress_df = trig[trig['isStress'] == True]
        trigg_not_stress_df = trig[trig['isStress'] == False]
        trigg_stress[id].append(trigg_stress_df.shape[0])
        trigg_not_stress[id].append(trigg_not_stress_df.shape[0])
        # stress + prelapse
        trigg_stress_prelapse_df = trigg_stress_df[trigg_stress_df['isPreLapse'] == True]
        trigg_stress_prelapse[id].append(trigg_stress_prelapse_df.shape[0])
        # stress + postlapse
        trigg_stress_postlapse_df = trigg_stress_df[trigg_stress_df['isPreLapse'] == False]
        trigg_stress_postlapse[id].append(trigg_stress_postlapse_df.shape[0])
        # not_stress + prelapse
        trigg_not_stress_prelapse_df = trigg_not_stress_df[trigg_not_stress_df['isPreLapse'] == True]
        trigg_not_stress_prelapse[id].append(trigg_not_stress_prelapse_df.shape[0])
        # not_stress + postlapse
        trigg_not_stress_postlapse_df = trigg_not_stress_df[trigg_not_stress_df['isPreLapse'] == False]
        trigg_not_stress_postlapse[id].append(trigg_not_stress_postlapse_df.shape[0])
        num_decision_points = id_log_EMI_day[available_condition | unavailable_condition].shape[0]
        num_available_decision_points = id_log_EMI_day[available_condition].shape[0]
        num_int_triggered = id_log_EMI_day[int_triggered_condition].shape[0]
        num_int_not_triggered = id_log_EMI_day[int_not_triggered_condition].shape[0]
        decision_points[id].append(num_decision_points)
        available_decision_points[id].append(num_available_decision_points)
        ints_triggered[id].append(num_int_triggered) # ints_trig + ints_not_trig = avai_dec_points.
        ints_not_triggered[id].append(num_int_not_triggered)
        pre_lapse_rows = id_log_EMI_day[id_log_EMI_day['isPreLapse'] == True].shape[0]
        post_lapse_rows = id_log_EMI_day[id_log_EMI_day['isPreLapse'] == False].shape[0]
        pre_lapse_cond = pre_lapse_rows > 0
        post_lapse_cond = post_lapse_rows > 0
        if (pre_lapse_cond & (not post_lapse_cond)):
            pre_lapse_val = 1
        elif post_lapse_cond > 0:
            pre_lapse_val = 0
        else:
            pre_lapse_val = np.nan
        pre_lapse_day_vals[id].append(pre_lapse_val)
        day = day + timedelta(days=1)

# calculate summarise for
##### 1. total stress mins
##### 2. total not stress mins
##### 3. total physically active mins
##### ... following:
###### a. available decision times
###### b. available decision times at which the individual is detected stressed
###### c. available decision times at which the individual is not detected stressed

stress_mins_frac = {}
not_stress_mins_frac = {}
active_mins_frac = {}
for id in not_missing_mins.keys():
    stress_mins_frac[id] = {}
    not_stress_mins_frac[id] = {}
    active_mins_frac[id] = {}
    for day in not_missing_mins[id].keys():
        stress_mins_frac[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_stress_mins[id][day], not_missing_mins[id][day])]
        not_stress_mins_frac[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_not_stress_mins[id][day], not_missing_mins[id][day])]
        active_mins_frac[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_physical_active_mins[id][day], not_missing_mins[id][day])]

mean_stress_mins_frac = {}
mean_not_stress_mins_frac = {}
mean_active_mins_frac =  {}
for id in stress_mins_frac.keys():
    mean_stress_mins_frac[id] = []
    mean_not_stress_mins_frac[id] = []
    mean_active_mins_frac[id] =  []
    for day in not_missing_mins[id].keys():
        mean_stress_mins_frac[id].append(round(np.nanmean(stress_mins_frac[id][day]),2))
        mean_not_stress_mins_frac[id].append(round(np.nanmean(not_stress_mins_frac[id][day]),2))
        mean_active_mins_frac[id].append(round(np.nanmean(active_mins_frac[id][day]),2))

mean_across_days_stress_mins = []
mean_across_days_not_stress_mins = []
mean_across_days_active_mins = []
for id in mean_stress_mins_frac.keys():
    mean_across_days_stress_mins.append(round(np.nanmean(mean_stress_mins_frac[id]),2))
    mean_across_days_not_stress_mins.append(round(np.nanmean(mean_not_stress_mins_frac[id]),2))
    mean_across_days_active_mins.append(round(np.nanmean(mean_active_mins_frac[id]),2))

# Now calculate these fractions over the entire 120 mins: 

classifiable_mins_frac = {}
for id in total_stress_mins.keys():
    classifiable_mins_frac[id] = {}
    for day in total_stress_mins[id].keys():
        classifiable_mins_frac[id][day] = [round((i + j + k)/120, 2) for i, j, k in zip(total_stress_mins[id][day], total_not_stress_mins[id][day], total_physical_active_mins[id][day])]

mean_classifiable_mins_frac_days = {}
for id in classifiable_mins_frac.keys():
    mean_classifiable_mins_frac_days[id] = []
    for day in classifiable_mins_frac[id].keys():
        mean_classifiable_mins_frac_days[id].append(round(np.nanmean(classifiable_mins_frac[id][day]),2))


# Now do this filtered by available decision time in which the user is either detected to be stressed
# or not detected to be stressed:

not_missing_mins_S = {}
total_stress_mins_S = {}
total_not_stress_mins_S = {}
total_physical_active_mins_S = {}
not_missing_mins_NS = {}
total_stress_mins_NS = {}
total_not_stress_mins_NS = {}
total_physical_active_mins_NS = {}
for id in participants_for_analysis:
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == id]
    id_episodes = episodes[episodes['participant_id'] == id]
    day = mrt_id_start_day
    not_missing_mins_S[id] = {}
    total_stress_mins_S[id] = {}
    total_not_stress_mins_S[id] = {}
    total_physical_active_mins_S[id] = {}
    not_missing_mins_NS[id] = {}
    total_stress_mins_NS[id] = {}
    total_not_stress_mins_NS[id] = {}
    total_physical_active_mins_NS[id] = {}
    while day <=  mrt_id_tenth_day:
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        available_condition = id_log_EMI_day['message'] == 'true: all conditions okay'
        unavailable_condition = id_log_EMI_day['message'] == 'false: some conditions are failed'
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        # calculate ave. no. of ints:
        available_dec_points = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        available_dec_points_stress = available_dec_points[available_dec_points['isStress'] == True]
        available_dec_points_not_stress = available_dec_points[available_dec_points['isStress'] == False]
        # from each decision point, calculate the minutes in the following 120 minute window
        # that are (1) in a stress episode; (2) in a not-able-to-classify-as-stress episode; and
        # (3) unknown due to physical activity. Then calculate the fraction of the 120 minute
        # window this corresponds to:
        not_missing_mins_S[id][day] = []
        total_stress_mins_S[id][day] = []
        total_not_stress_mins_S[id][day] = []
        total_physical_active_mins_S[id][day] = []
        not_missing_mins_NS[id][day] = []
        total_stress_mins_NS[id][day] = []
        total_not_stress_mins_NS[id][day] = []
        total_physical_active_mins_NS[id][day] = []
        if available_dec_points_stress.shape[0] > 0:
            available_decision_times_stressed = list(available_dec_points_stress['date_time'])
            for avai_dec_time in available_decision_times_stressed:
                start_time = avai_dec_time
                # start_time = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                # if start_time == 'NaT':
                #     start_time_localize = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                id_episodes_day_2hour = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= end_time)]
                id_activity_day_2hour = id_activity_day[(id_activity_day['datetime'] >= start_time) & (id_activity_day['datetime'] <= end_time)]
                # count minutes stressed:
                stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 2.0]
                stress_min_count = 0
                if stress_eps.shape[0] > 0:
                    for index, row in stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                # count minutes not stressed:
                not_stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 0.0]
                not_stress_min_count = 0
                if not_stress_eps.shape[0] > 0:
                    for index, row in not_stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            not_stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                    # count minutes active inside unknown episodes:
                unknown_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 3.0]
                unknown_due_to_activity_mins = 0
                unknown_due_to_bad_data_mins = 0
                if unknown_eps.shape[0] > 0:
                    for index, row in unknown_eps.iterrows():
                        if row.datetime_start <= start_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= start_time) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        elif row.datetime_end >= end_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= end_time)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        else:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        #
                        if active_mins >= ((minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60)/2:
                            # this episode is unknown due to activity
                            if row.datetime_start <= start_time:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_activity_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            if row.datetime_start <= start_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                total_stress_mins_val = round(stress_min_count, 2)
                total_not_stress_mins_val = round(not_stress_min_count, 2)
                total_physical_active_mins_val = round(unknown_due_to_activity_mins, 2)
                total_stress_mins_S[id][day].append(total_stress_mins_val)
                total_not_stress_mins_S[id][day].append(total_not_stress_mins_val)
                total_physical_active_mins_S[id][day].append(total_physical_active_mins_val)
                total_mins = stress_min_count + not_stress_min_count + unknown_due_to_activity_mins
                not_missing_mins_S[id][day].append(total_mins)
        if available_dec_points_not_stress.shape[0] > 0:
            available_decision_times_not_stressed = list(available_dec_points_not_stress['date_time'])
            for avai_dec_time in available_decision_times_not_stressed:
                start_time = avai_dec_time
                # start_time = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                # if start_time == 'NaT':
                #     start_time_localize = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                id_episodes_day_2hour = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= end_time)]
                id_activity_day_2hour = id_activity_day[(id_activity_day['datetime'] >= start_time) & (id_activity_day['datetime'] <= end_time)]
                # count minutes stressed:
                stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 2.0]
                stress_min_count = 0
                if stress_eps.shape[0] > 0:
                    for index, row in stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                # count minutes not stressed:
                not_stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 0.0]
                not_stress_min_count = 0
                if not_stress_eps.shape[0] > 0:
                    for index, row in not_stress_eps.iterrows():
                        if row.datetime_start <= start_time:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                        elif row.datetime_end >= end_time:
                            not_stress_min_count += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            not_stress_min_count += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                # count minutes active inside unknown episodes:
                unknown_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 3.0]
                unknown_due_to_activity_mins = 0
                unknown_due_to_bad_data_mins = 0
                if unknown_eps.shape[0] > 0:
                    for index, row in unknown_eps.iterrows():
                        if row.datetime_start <= start_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= start_time) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        elif row.datetime_end >= end_time:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= end_time)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        else:
                            df = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= row.datetime_end)]
                            active_mins = df[df['event'] == 1.0].shape[0]
                        #
                        if active_mins >= ((minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60)/2:
                            # this episode is unknown due to activity
                            if row.datetime_start <= start_time:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_activity_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                        else:
                            if row.datetime_start <= start_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                total_stress_mins_val = round(stress_min_count, 2)
                total_not_stress_mins_val = round(not_stress_min_count, 2)
                total_physical_active_mins_val = round(unknown_due_to_activity_mins, 2)
                total_stress_mins_NS[id][day].append(total_stress_mins_val)
                total_not_stress_mins_NS[id][day].append(total_not_stress_mins_val)
                total_physical_active_mins_NS[id][day].append(total_physical_active_mins_val)
                total_mins = stress_min_count + not_stress_min_count + unknown_due_to_activity_mins
                not_missing_mins_NS[id][day].append(total_mins)
        day = day + timedelta(days=1)


stress_mins_frac_S = {}
not_stress_mins_frac_S = {}
active_mins_frac_S = {}
for id in not_missing_mins_S.keys():
    stress_mins_frac_S[id] = {}
    not_stress_mins_frac_S[id] = {}
    active_mins_frac_S[id] = {}
    for day in not_missing_mins_S[id].keys():
        stress_mins_frac_S[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_stress_mins_S[id][day], not_missing_mins_S[id][day])]
        not_stress_mins_frac_S[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_not_stress_mins_S[id][day], not_missing_mins_S[id][day])]
        active_mins_frac_S[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_physical_active_mins_S[id][day], not_missing_mins_S[id][day])]

stress_mins_frac_NS = {}
not_stress_mins_frac_NS = {}
active_mins_frac_NS = {}
for id in not_missing_mins_NS.keys():
    stress_mins_frac_NS[id] = {}
    not_stress_mins_frac_NS[id] = {}
    active_mins_frac_NS[id] = {}
    for day in not_missing_mins_NS[id].keys():
        stress_mins_frac_NS[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_stress_mins_NS[id][day], not_missing_mins_NS[id][day])]
        not_stress_mins_frac_NS[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_not_stress_mins_NS[id][day], not_missing_mins_NS[id][day])]
        active_mins_frac_NS[id][day] = [round(i/float(j),2) if j != 0 else np.nan for (i,j) in zip(total_physical_active_mins_NS[id][day], not_missing_mins_NS[id][day])]

mean_stress_mins_frac_S = {}
mean_not_stress_mins_frac_S = {}
mean_active_mins_frac_S =  {}
for id in stress_mins_frac_S.keys():
    mean_stress_mins_frac_S[id] = []
    mean_not_stress_mins_frac_S[id] = []
    mean_active_mins_frac_S[id] =  []
    for day in not_missing_mins_S[id].keys():
        mean_stress_mins_frac_S[id].append(round(np.nanmean(stress_mins_frac_S[id][day]),2))
        mean_not_stress_mins_frac_S[id].append(round(np.nanmean(not_stress_mins_frac_S[id][day]),2))
        mean_active_mins_frac_S[id].append(round(np.nanmean(active_mins_frac_S[id][day]),2))

mean_stress_mins_frac_NS = {}
mean_not_stress_mins_frac_NS = {}
mean_active_mins_frac_NS =  {}
for id in stress_mins_frac_NS.keys():
    mean_stress_mins_frac_NS[id] = []
    mean_not_stress_mins_frac_NS[id] = []
    mean_active_mins_frac_NS[id] =  []
    for day in not_missing_mins_NS[id].keys():
        mean_stress_mins_frac_NS[id].append(round(np.nanmean(stress_mins_frac_NS[id][day]),2))
        mean_not_stress_mins_frac_NS[id].append(round(np.nanmean(not_stress_mins_frac_NS[id][day]),2))
        mean_active_mins_frac_NS[id].append(round(np.nanmean(active_mins_frac_NS[id][day]),2))

mean_across_days_stress_mins_S = []
mean_across_days_not_stress_mins_S = []
mean_across_days_active_mins_S = []
for id in mean_stress_mins_frac_S.keys():
    mean_across_days_stress_mins_S.append(round(np.nanmean(mean_stress_mins_frac_S[id]),2))
    mean_across_days_not_stress_mins_S.append(round(np.nanmean(mean_not_stress_mins_frac_S[id]),2))
    mean_across_days_active_mins_S.append(round(np.nanmean(mean_active_mins_frac_S[id]),2))

mean_across_days_stress_mins_NS = []
mean_across_days_not_stress_mins_NS = []
mean_across_days_active_mins_NS = []
for id in mean_stress_mins_frac_NS.keys():
    mean_across_days_stress_mins_NS.append(round(np.nanmean(mean_stress_mins_frac_NS[id]),2))
    mean_across_days_not_stress_mins_NS.append(round(np.nanmean(mean_not_stress_mins_frac_NS[id]),2))
    mean_across_days_active_mins_NS.append(round(np.nanmean(mean_active_mins_frac_NS[id]),2))


# Make sure that total_bad_mins and not_missing_mins sum to close to 120:
total_total_mins = {}
count_120 = 0
count_total = 0
count_not_missing = 0
for id in total_bad_mins.keys():
    total_total_mins[id] = {}
    for day in total_bad_mins[id].keys():
        total_total_mins[id][day] = [sum(i) for i in zip(total_bad_mins[id][day], not_missing_mins[id][day])]
        for i in total_total_mins[id][day]:
            if i == 120:
                count_120 += 1
            count_total += 1
        for i in not_missing_mins[id][day]:
            if i == 120:
                count_not_missing += 1

# calculate median not missing data per day per id:

median_not_missing_mins_frac = {}
average_not_missing_mins_frac = {}
for id in not_missing_mins_frac.keys():
    median_not_missing_mins_frac[id] = []
    average_not_missing_mins_frac[id] = []
    for day in not_missing_mins_frac[id].keys():
        median_val = round(np.median(not_missing_mins_frac[id][day]), 2)
        average_val = round(np.mean(not_missing_mins_frac[id][day]), 2)
        median_not_missing_mins_frac[id].append(median_val)
        average_not_missing_mins_frac[id].append(average_val)

total_dec_points_per_participant = {}
total_available_dec_points_per_participant = {}
total_frac_dec_unavailable = {}
total_frac_dec_available = {}
total_ints_triggered = {}
frac_ints_per_day = {}
frac_ints_stress_per_day = {}
frac_ints_not_stress_per_day = {}
total_ints_triggered_stressed = {}
total_ints_triggered_not_stressed = {}
frac_ints_stress_prelapse_per_day = {}
frac_ints_stress_postlapse_per_day = {}
frac_ints_not_stress_prelapse_per_day = {}
frac_ints_not_stress_postlapse_per_day = {}
frac_ints_stress_prelapse_per_day_2 = {}
frac_ints_stress_postlapse_per_day_2 = {}
frac_ints_not_stress_prelapse_per_day_2 = {}
frac_ints_not_stress_postlapse_per_day_2 = {}
generated_decision_points = {}
total_days_generated_decision_points = {}
s_pre_dec_point_day = {}
total_days_s_pre_dec_points = {}
s_post_dec_point_day = {}
total_days_s_post_dec_points = {}
ns_pre_dec_point_day = {}
total_days_ns_pre_dec_points = {}
ns_post_dec_point_day = {}
total_days_ns_post_dec_points = {}
sum_trig_stress_prelapse = {}
sum_trig_stress_postlapse = {}
sum_trig_not_stress_prelapse = {}
sum_trig_not_stress_postlapse = {}
for id in participants_for_analysis:
    total_dec_points_per_participant[id] = sum(decision_points[id])
    total_available_dec_points_per_participant[id] = sum(available_decision_points[id])
    frac1 = (total_dec_points_per_participant[id] - total_available_dec_points_per_participant[id])/float(total_dec_points_per_participant[id])
    total_frac_dec_unavailable[id] = round(frac1,2)
    frac2 = total_available_dec_points_per_participant[id]/float(total_dec_points_per_participant[id])
    total_frac_dec_available[id] = round(frac2,2)
    total_ints_triggered[id] = sum(ints_triggered[id])
    frac_ints_per_day[id] = np.mean(ints_triggered[id])
    total_ints_triggered_stressed[id] = sum(trigg_stress[id])
    frac_ints_stress_per_day[id] = np.mean(trigg_stress[id])
    total_ints_triggered_not_stressed[id] = sum(trigg_not_stress[id])
    frac_ints_not_stress_per_day[id] = np.mean(trigg_not_stress[id])
    frac_ints_stress_prelapse_per_day[id] = np.mean(trigg_stress_prelapse[id])
    frac_ints_stress_postlapse_per_day[id] = np.mean(trigg_stress_postlapse[id])
    frac_ints_not_stress_prelapse_per_day[id] = np.mean(trigg_not_stress_prelapse[id])
    frac_ints_not_stress_postlapse_per_day[id] = np.mean(trigg_not_stress_postlapse[id])
    #
    s_pre_dec_point_day[id] = [0 if i==0 else 1 for i in available_s_pre_dec_points[id]]
    total_days_s_pre_dec_points[id] = sum(s_pre_dec_point_day[id])
    s_post_dec_point_day[id] = [0 if i==0 else 1 for i in available_s_post_dec_points[id]]
    total_days_s_post_dec_points[id] = sum(s_post_dec_point_day[id])
    ns_pre_dec_point_day[id] = [0 if i==0 else 1 for i in available_ns_pre_dec_points[id]]
    total_days_ns_pre_dec_points[id] = sum(ns_pre_dec_point_day[id])
    ns_post_dec_point_day[id] = [0 if i==0 else 1 for i in available_ns_post_dec_points[id]]
    total_days_ns_post_dec_points[id] = sum(ns_post_dec_point_day[id])
    generated_decision_points[id] = [0 if i==0 else 1 for i in decision_points[id]]
    total_days_generated_decision_points[id] = sum(generated_decision_points[id])
    sum_trig_stress_prelapse[id] = np.sum(trigg_stress_prelapse[id])
    sum_trig_stress_postlapse[id] = np.sum(trigg_stress_postlapse[id])
    sum_trig_not_stress_prelapse[id] = np.sum(trigg_not_stress_prelapse[id])
    sum_trig_not_stress_postlapse[id] = np.sum(trigg_not_stress_postlapse[id])
    frac_ints_stress_prelapse_per_day_2[id] = round(np.sum(trigg_stress_prelapse[id])/total_days_generated_decision_points[id],2)
    frac_ints_stress_postlapse_per_day_2[id] = round(np.sum(trigg_stress_postlapse[id])/total_days_generated_decision_points[id],2)
    frac_ints_not_stress_prelapse_per_day_2[id] = round(np.sum(trigg_not_stress_prelapse[id])/total_days_generated_decision_points[id],2)
    frac_ints_not_stress_postlapse_per_day_2[id] = round(np.sum(trigg_not_stress_postlapse[id])/total_days_generated_decision_points[id],2)

# there were X total generated decision points:
sum(total_dec_points_per_participant.values())

# there were X total available decision points:
sum(total_available_dec_points_per_participant.values())

# There were X total interventions delivered:
sum(total_ints_triggered.values())

# There were X total interventions delivered at stressed times:
sum(total_ints_triggered_stressed.values())

# There were X total interventions delivered at not stressed times:
sum(total_ints_triggered_not_stressed.values())

# On average, participants received X reminders each day:
mean_val = np.mean(list(frac_ints_per_day.values()))
sd_val = np.std(list(frac_ints_per_day.values()))

mean_val_s = np.mean(list(frac_ints_stress_per_day.values()))
sd_val_s = np.std(list(frac_ints_stress_per_day.values()))

mean_val_ns = np.mean(list(frac_ints_not_stress_per_day.values()))
sd_val_ns = np.std(list(frac_ints_not_stress_per_day.values()))

mean_val_s_prelapse = np.mean(list(frac_ints_stress_prelapse_per_day.values()))
sd_val_s_prelapse = np.std(list(frac_ints_stress_prelapse_per_day.values()))

mean_val_s_postlapse = np.mean(list(frac_ints_stress_postlapse_per_day.values()))
sd_val_s_postlapse = np.std(list(frac_ints_stress_postlapse_per_day.values()))

mean_val_ns_prelapse = np.mean(list(frac_ints_not_stress_prelapse_per_day.values()))
sd_val_ns_prelapse = np.std(list(frac_ints_not_stress_prelapse_per_day.values()))

mean_val_ns_postlapse = np.mean(list(frac_ints_not_stress_postlapse_per_day.values()))
sd_val_ns_postlapse = np.std(list(frac_ints_not_stress_postlapse_per_day.values()))

#

mean_val_s_prelapse_2 = np.mean(list(frac_ints_stress_prelapse_per_day_2.values()))
sd_val_s_prelapse_2 = np.std(list(frac_ints_stress_prelapse_per_day_2.values()))

mean_val_s_postlapse_2 = np.mean(list(frac_ints_stress_postlapse_per_day_2.values()))
sd_val_s_postlapse_2 = np.std(list(frac_ints_stress_postlapse_per_day_2.values()))

mean_val_ns_prelapse_2 = np.mean(list(frac_ints_not_stress_prelapse_per_day_2.values()))
sd_val_ns_prelapse_2 = np.std(list(frac_ints_not_stress_prelapse_per_day_2.values()))

mean_val_ns_postlapse_2 = np.mean(list(frac_ints_not_stress_postlapse_per_day_2.values()))
sd_val_ns_postlapse_2 = np.std(list(frac_ints_not_stress_postlapse_per_day_2.values()))

# to get a fair representation of average number of interventions sent, find the
# total number of interventions sent in the 10 day period divided by the number of
# days that had randomizations (i.e., days that generated decision times):

# Look into first detected smoking episode:

smoking_ep_backup = pd.read_csv(wd + '/' + "puffmarker_smoking_episode_backup.csv")
uq_ids_smoking_ep_backup = list(smoking_ep_backup.participant_id.unique())
smoking_ep_original = pd.read_csv(wd + '/' + "puffmarker_smoking_episode_original.csv")
uq_ids_smoking_ep_original = list(smoking_ep_original.participant_id.unique())
smoking_ep_alternative = pd.read_csv(wd + '/' + "puffmarker_smoking_episode_alternative.csv")
uq_ids_smoking_ep_alternative = list(smoking_ep_alternative.participant_id.unique())

smoking_eps = pd.DataFrame(columns = ['datetime', 'timestamp', 'event', 'participant_id'])
for id in participants_for_analysis:
    if id in uq_ids_smoking_ep_backup:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = smoking_ep_backup[smoking_ep_backup['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        smoking_eps = smoking_eps.append(data_to_append)
    elif id in uq_ids_smoking_ep_original:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = smoking_ep_original[smoking_ep_original['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        smoking_eps = smoking_eps.append(data_to_append)
    elif id in uq_ids_smoking_ep_alternative:
        data_to_append = pd.DataFrame(columns = ['timestamp', 'event', 'participant_id'])
        data = smoking_ep_alternative[smoking_ep_alternative['participant_id'] == id]
        data_to_append['timestamp'] = data['timestamp']
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        smoking_eps = smoking_eps.append(data_to_append)

smoking_eps = smoking_eps.reset_index(drop=True)

# record day in mrt when first smoking ep was detected per participant:

first_smoking_ep_detected = {}
for id in participants_for_analysis:
    smoking_eps_id = smoking_eps[smoking_eps['participant_id'] == id]
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    day = mrt_id_start_day
    day_val = 1
    while day <=  mrt_id_tenth_day:
        first_smoking_ep_detected[id] = np.nan
        smoking_eps_id_day = smoking_eps_id[smoking_eps_id['date'] == day]
        num_rows = smoking_eps_id_day.shape[0]
        if num_rows > 0:
            first_smoking_ep_detected[id] = day_val
            break
        day = day + timedelta(days=1)
        day_val = day_val + 1

# Make boxplot of decision points:

day1 = Extract(decision_points, 0)
day2 = Extract(decision_points, 1)
day3 = Extract(decision_points, 2)
day4 = Extract(decision_points, 3)
day5 = Extract(decision_points, 4)
day6 = Extract(decision_points, 5)
day7 = Extract(decision_points, 6)
day8 = Extract(decision_points, 7)
day9 = Extract(decision_points, 8)
day10 = Extract(decision_points, 9)

box_plot_data=[day1,day2,day3,day4,day5,day6,day7,day8,day9,day10]

import matplotlib.pyplot as plt
plt.xlabel('Day in Sense2Stop MRT')
plt.ylabel('Number of Decision Points')
plt.title('Boxplots of Number of Decision Points Per Day')
plt.boxplot(box_plot_data)
# plt.show()

# day1 = Extract(available_decision_points, 0)
# day2 = Extract(available_decision_points, 1)
# day3 = Extract(available_decision_points, 2)
# day4 = Extract(available_decision_points, 3)
# day5 = Extract(available_decision_points, 4)
# day6 = Extract(available_decision_points, 5)
# day7 = Extract(available_decision_points, 6)
# day8 = Extract(available_decision_points, 7)
# day9 = Extract(available_decision_points, 8)
# day10 = Extract(available_decision_points, 9)
#
# box_plot_data=[day1,day2,day3,day4,day5,day6,day7,day8,day9,day10]
#
# plt.xlabel('Day in Sense2Stop MRT')
# plt.ylabel('Number of Available Decision Points')
# plt.title('Boxplots of Number of Decision Points Per Day')
# plt.boxplot(box_plot_data)
# plt.show()

# Find proportion of day that participant has bad quality data. Do this for
# the participant level and day in study level. Here, we are trying to
# understand why some participants have very few candidate decision points
# generated within the 10-day MRT period:

quality_ecg = {}
quality_rep = {}
activity = {}
for id in participants_for_analysis:
    print("id: ", id)
    if str(id) in participant_ids_backup:
        g = 'cstress_data_ecg_quality_backup.csv'
        h = 'cstress_data_rep_quality_backup.csv'
        i = 'stress_activity_phone_backup.csv'
        # ECG QUALITY:
        data_ecg_quality = pd.read_csv(wd + '/' + g)
        quality_ecg[id] = data_ecg_quality[data_ecg_quality['participant_id'] == int(id)]
        quality_ecg[id]['date_time'] = [date_time(i) for i in quality_ecg[id]['timestamp']]
        quality_ecg[id]['date'] = [i.date() for i in quality_ecg[id]['date_time']]
        # REP QUALITY:
        data_rep_quality = pd.read_csv(wd + '/' + h)
        quality_rep[id] = data_rep_quality[data_rep_quality['participant_id'] == int(id)]
        quality_rep[id]['date_time'] = [date_time(i) for i in quality_rep[id]['timestamp']]
        quality_rep[id]['date'] = [i.date() for i in quality_rep[id]['date_time']]
        # ACTIVITY:
        stress_activity = pd.read_csv(wd + '/' + i)
        activity[id] = stress_activity[stress_activity['participant_id'] == int(id)]
        activity[id]['date_time'] = [date_time(i) for i in activity[id]['timestamp']]
        activity[id]['date'] = [i.date() for i in activity[id]['date_time']]
    elif str(id) in participant_ids_original:
        g = 'cstress_data_ecg_quality_original.csv'
        h = 'cstress_data_rep_quality_original.csv'
        i = 'stress_activity_phone_original.csv'
        # ECG QUALITY:
        data_ecg_quality = pd.read_csv(wd + '/' + g)
        quality_ecg[id] = data_ecg_quality[data_ecg_quality['participant_id'] == int(id)]
        quality_ecg[id]['date_time'] = [date_time(i) for i in quality_ecg[id]['timestamp']]
        quality_ecg[id]['date'] = [i.date() for i in quality_ecg[id]['date_time']]
        # REP QUALITY:
        data_rep_quality = pd.read_csv(wd + '/' + h)
        quality_rep[id] = data_rep_quality[data_rep_quality['participant_id'] == int(id)]
        quality_rep[id]['date_time'] = [date_time(i) for i in quality_rep[id]['timestamp']]
        quality_rep[id]['date'] = [i.date() for i in quality_rep[id]['date_time']]
        # ACTIVITY:
        stress_activity = pd.read_csv(wd + '/' + i)
        activity[id] = stress_activity[stress_activity['participant_id'] == int(id)]
        activity[id]['date_time'] = [date_time(i) for i in activity[id]['timestamp']]
        activity[id]['date'] = [i.date() for i in activity[id]['date_time']]
    elif str(id) in participant_ids_alternative:
        g = 'cstress_data_ecg_quality_alternative.csv'
        h = 'cstress_data_rep_quality_alternative.csv'
        i = 'stress_activity_phone_alternative.csv'
        # ECG QUALITY:
        data_ecg_quality = pd.read_csv(wd + '/' + g)
        quality_ecg[id] = data_ecg_quality[data_ecg_quality['participant_id'] == int(id)]
        quality_ecg[id]['date_time'] = [date_time(i) for i in quality_ecg[id]['timestamp']]
        quality_ecg[id]['date'] = [i.date() for i in quality_ecg[id]['date_time']]
        # REP QUALITY:
        data_rep_quality = pd.read_csv(wd + '/' + h)
        quality_rep[id] = data_rep_quality[data_rep_quality['participant_id'] == int(id)]
        quality_rep[id]['date_time'] = [date_time(i) for i in quality_rep[id]['timestamp']]
        quality_rep[id]['date'] = [i.date() for i in quality_rep[id]['date_time']]
        # ACTIVITY:
        stress_activity = pd.read_csv(wd + '/' + i)
        activity[id] = stress_activity[stress_activity['participant_id'] == int(id)]
        activity[id]['date_time'] = [date_time(i) for i in activity[id]['timestamp']]
        activity[id]['date'] = [i.date() for i in activity[id]['date_time']]

#
bad_qual_ecg_props = {}
bad_qual_rep_props = {}
activity_props = {}
for id in participants_for_analysis:
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_qual_ecg_full = quality_ecg[id]
    id_qual_ecg_mrt = id_qual_ecg_full[(id_qual_ecg_full['date'] >= mrt_id_start_day) & (id_qual_ecg_full['date'] <= mrt_id_tenth_day)]
    id_qual_rep_full = quality_rep[id]
    id_qual_rep_mrt = id_qual_rep_full[(id_qual_rep_full['date'] >= mrt_id_start_day) & (id_qual_rep_full['date'] <= mrt_id_tenth_day)]
    id_activity_full = activity[id]
    id_activity_mrt = id_activity_full[(id_activity_full['date'] >= mrt_id_start_day) & (id_activity_full['date'] <= mrt_id_tenth_day)]
    # Check if participants have given start and end time of days:
    # day_start_id = day_start[day_start['participant_id'] == id]
    # day_start_id_mrt = day_start_id[day_start_id['date'] >= mrt_id_start_day]
    # day_end_id = day_end[day_end['participant_id'] == id]
    # day_end_id_mrt = day_end_id[day_end_id['date'] >= mrt_id_start_day]
    day = mrt_id_start_day
    day_num = 1
    bad_qual_ecg_props[id] = []
    bad_qual_rep_props[id] = []
    activity_props[id] = []
    print(id)
    print("")
    while day <=  mrt_id_tenth_day:
        id_qual_ecg_mrt_day = id_qual_ecg_mrt[id_qual_ecg_mrt['date'] == day].reset_index(drop=True)
        num_rows_ecg = id_qual_ecg_mrt_day.shape[0]
        #
        id_qual_rep_mrt_day = id_qual_rep_mrt[id_qual_rep_mrt['date'] == day].reset_index(drop=True)
        num_rows_rep = id_qual_rep_mrt_day.shape[0]
        #
        id_activity_mrt_day = id_activity_mrt[id_activity_mrt['date'] == day].reset_index(drop=True)
        num_rows_act = id_activity_mrt_day.shape[0]
        #
        # every row is meant to give a qual measure for a 2 second period.
        # So, num_rows /(60*60) = num hours of day.
        if num_rows_ecg == 0:
            string = 'Participant ' + str(id) + ' does not have any ECG Quality information on day ' + str(day_num)
            print(string)
            bad_qual_ecg_props[id].append(np.nan)
        else:
            prop_bad_qual_ecg = (id_qual_ecg_mrt_day[id_qual_ecg_mrt_day['event'] != 0.0].shape[0])/num_rows_ecg
            bad_qual_ecg_props[id].append(round(prop_bad_qual_ecg,2))
        #
        if num_rows_rep == 0:
            string = 'Participant ' + str(id) + ' does not have any RIP Quality information on day ' + str(day_num)
            print(string)
            bad_qual_rep_props[id].append(np.nan)
        else:
            prop_bad_qual_rep = (id_qual_rep_mrt_day[id_qual_rep_mrt_day['event'] != 0.0].shape[0])/num_rows_rep
            bad_qual_rep_props[id].append(round(prop_bad_qual_rep,2))
        #
        if num_rows_act == 0:
            string = 'Participant ' + str(id) + ' does not have any activity information on day ' + str(day_num)
            print(string)
            activity_props[id].append(np.nan)
        else:
            prop_act = (id_activity_mrt_day[id_activity_mrt_day['event'] == 1.0].shape[0])/num_rows_act
            activity_props[id].append(round(prop_act,2))
        day =  day + timedelta(days=1)
        day_num = day_num + 1


# define intervention:
def intervention(row):
    val = np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == True), 'class_stress', # available_stress
            np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == False), 'class_notStress', # available_notStress
              np.where((row['id'] == 'EMI') and (row['status'] == 'DELIVERED'), 'delivered', 'other'))) # delivered, other.
    return val

# Add summary table for participants that don't have decision times. E.g., are they
# only in the study for 2 days or less than number of pre-quit days?

all_id_decision_times = {}
ids_w_no_decision_times = []
days_in_study = []
randomised = []
days_present = []
received_intervention = []
for id in all_participant_ids:
    name = 'phone_log_' + str(id)
    df = logs[name]
    # df['date_time_w_tz'] = [i.tz_localize(tz=pytz.timezone('America/Chicago'), ambiguous = 'NaT') for i in df['date_time']]
    if np.sum(df['operation'] == 'EMI_INFO') == 0:
        string = 'Participant ' + str(id) + ' does not have any decision times.'
        min_date = min(df['date_time'])
        max_date = max(df['date_time'])
        df['date'] = [i.date() for i in df['date_time']]
        days_present.append(df['date'].nunique())
        diff = max_date - min_date
        diff_days = int(diff.days)
        print(string)
        print('...in the study for ' + str(diff_days) + 'days, from ' + str(min_date) + ' to ' + str(max_date))
        ids_w_no_decision_times.append(id)
        days_in_study.append(diff_days)
        randomised.append("No")
        received_intervention.append("No")
    else:
        df['date'] = [i.date() for i in df['date_time']]
        days_present.append(df['date'].nunique())
        df['intervention'] = df.apply(intervention, axis=1)
        id_decision_times = df[(df.intervention == 'class_stress') | (df.intervention == 'class_notStress')].reset_index(drop=True)
        all_id_decision_times[name] = id_decision_times
        min_date = min(df['date_time'])
        max_date = max(df['date_time'])
        diff = max_date - min_date
        diff_days = int(diff.days)
        days_in_study.append(diff_days)
        randomised.append("Yes")
        if (df[df['isTriggered'] == True].shape[0] == 0):
            received_intervention.append("No")
        elif (df[df['isTriggered'] == True].shape[0] > 0):
            received_intervention.append("Yes")


decision_times = pd.DataFrame(columns=['date_time', 'participant_id', 'isStress', 'isTriggered'])
for key in all_id_decision_times.keys():
    df = all_id_decision_times[key][['date_time', 'participant_id', 'isStress', 'isTriggered']].copy()
    decision_times = decision_times.append(df, ignore_index=True)

joblib.dump(decision_times, 'decision_times.pkl')
decision_times.to_csv('decision_times.csv', index=False)

# of individuals that were randomised at least once throughout the study,
# how many days were they randomised? average randomisations per day?
# how many interventions? average interventions per day?

decision_times['date'] = [i.date() for i in decision_times.date_time_w_tz]
dec_times_stats = decision_times.groupby(['participant_id'])['date'].nunique().reset_index(name = 'days_randomised')
num_rand_throughout_study = decision_times.groupby(['participant_id']).size().values
num_days_rand = decision_times.groupby(['participant_id'])['date'].nunique().values
dec_times_stats['avg_rand_per_day'] = [float(i)/float(j) for i,j in zip(num_rand_throughout_study, num_days_rand)]

dec_times_stats.to_csv('dec_times_stats.csv', index=False)

intervention_received = decision_times[decision_times['isTriggered'] == True]
int_times_stats = intervention_received.groupby(['participant_id'])['date'].nunique().reset_index(name = 'days_w_intervention')
num_int_throughout_study = intervention_received.groupby(['participant_id']).size().values
num_days_int = intervention_received.groupby(['participant_id'])['date'].nunique().values
int_times_stats['num_days_rand'] = dec_times_stats['days_randomised']
int_times_stats['avg_int_per_rand_day'] = [float(i)/float(j) for i,j in zip(num_int_throughout_study, num_days_rand)]

int_times_stats.to_csv('int_times_stats.csv', index=False)

# plot informative scattter plot for ids with no decision times to understand phone log
# activity:
# import matplotlib.pyplot as plt
#
# for id in ids_w_no_decision_times:
# name = 'phone_log_' + id
# df = logs[name]
# min_date = min(df.date_time)
# max_date = max(df.date_time)
# new_df = df.groupby(['date_time']).size().reset_index(name='num_log_activity')
# fig, ax = plt.subplots()
# x = np.array(new_df.date_time)
# y = np.array(new_df.num_log_activity)
# s = 5*y
# ax.scatter(x,y,s=s)
# ax.set_xlim([min_date, max_date])
# plt.show()


#################
# Summary info: #
#################

# Episodes are at the minute level!
# Every minute is either
# - CLASSIFIED BY CSTRESS = {"Stress", "Not Stress"}; or
# - NOT ABLE TO BE CLASSIFIED BY CSTRESS = {"Unknown"}
#
# final_df is every RANDOMISED episode within the study that was able to be classified
# as  either 'Stressed' or 'Not Stressed'. Create columns to add to this df that show:
# - % minutes within following 2 hour window that has CLASSIFIED BY CSTRESS (either Stress or Not Stress) episode
#     - % minutes within following 2 hour window that had 'Stress' episode
#     - % minutes within following 2 hour window that had 'Not Stressed' episode


# bring in episode start and end times:
wd = "/Users/mariannemenictas/Desktop/stress_cleaned_data/"

full_ep_times_original = pd.read_csv(filepath_or_buffer = wd + "classification_full_episode_original.csv")
full_ep_times_backup = pd.read_csv(filepath_or_buffer = wd + "classification_full_episode_backup.csv")
full_ep_times_alternative = pd.read_csv(filepath_or_buffer = wd + "classification_full_episode_alternative.csv")

full_ep_times_original['start_date_time'] = [functions.date_time(i) for i in full_ep_times_original['StartTime']]
full_ep_times_original['peak_date_time'] = [functions.date_time(i) for i in full_ep_times_original['PeakTime']]
full_ep_times_original['end_date_time'] = [functions.date_time(i) for i in full_ep_times_original['EndTime']]

full_ep_times_backup['start_date_time'] = [functions.date_time(i) for i in full_ep_times_backup['StartTime']]
full_ep_times_backup['peak_date_time'] = [functions.date_time(i) for i in full_ep_times_backup['PeakTime']]
full_ep_times_backup['end_date_time'] = [functions.date_time(i) for i in full_ep_times_backup['EndTime']]

full_ep_times_alternative['start_date_time'] = [functions.date_time(i) for i in full_ep_times_alternative['StartTime']]
full_ep_times_alternative['peak_date_time'] = [functions.date_time(i) for i in full_ep_times_alternative['PeakTime']]
full_ep_times_alternative['end_date_time'] = [functions.date_time(i) for i in full_ep_times_alternative['EndTime']]

all_ids_w_decision_times = decision_times['participant_id'].unique()
full_ep_times = pd.DataFrame(columns=['participant_id', 'start_date_time', 'peak_date_time', 'end_date_time', 'Stress_Episode_Classification'])

for id in all_ids_w_decision_times:
    if str(id) in participant_ids_backup:
        full_ep_times_id = full_ep_times_backup[full_ep_times_backup['participant_id'] == id]
        full_ep_times = pd.concat([full_ep_times, full_ep_times_id[['participant_id','start_date_time', 'peak_date_time', 'end_date_time', 'Stress_Episode_Classification']]], axis=0)
    elif str(id) in participant_ids_original:
        full_ep_times_id = full_ep_times_original[full_ep_times_original['participant_id'] == id]
        full_ep_times = pd.concat([full_ep_times, full_ep_times_id[['participant_id','start_date_time', 'peak_date_time', 'end_date_time', 'Stress_Episode_Classification']]], axis=0)
    elif str(id) in participant_ids_alternative:
        full_ep_times_id = full_ep_times_alternative[full_ep_times_alternative['participant_id'] == id]
        full_ep_times = pd.concat([full_ep_times, full_ep_times_id[['participant_id','start_date_time', 'peak_date_time', 'end_date_time', 'Stress_Episode_Classification']]], axis=0)

# filter full_ep_times to only include episodes that are classified as either
# stressed (2) or NotStressed (0):
stressed = full_ep_times['Stress_Episode_Classification'] == 2.0
not_stressed = full_ep_times['Stress_Episode_Classification'] == 0.0

full_ep_times_class = full_ep_times[stressed | not_stressed]

df = decision_times[['date_time_w_tz', 'participant_id', 'isStress', 'isTriggered']].copy()
# df = pd.read_csv('decision_times.csv')
df = df.drop_duplicates().reset_index(drop=True)
# df['date_time'] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in df.date_time]

#########################################################
# Count minutes classified as either 'stress' or
# 'not-able-to-classify-as-stress' within 2 hours of
# randomisation time.
#########################################################

count_eps_2hrs = []
count_mins_2hrs = []
count_eps_stress_2hrs = []
count_eps_not_stress_2hrs = []
count_eps_prompt = []
prev_end_time = min(df['date_time_w_tz'])
for index, row in df.iterrows():
    start = row['date_time_w_tz']
    # start and end time of current randomisation episode:
    end = start + timedelta(hours = 2)
    # get current participant_id:
    id = row['participant_id']
    df_id = df[df['participant_id'] == id]
    id_ep_times = full_ep_times_class[full_ep_times_class['participant_id'] == id]
    # get episodes within the next two hours:
    class_eps_2hrs = id_ep_times[(id_ep_times['end_date_time'] >= start) & (id_ep_times['start_date_time'] <= end)]
    df_id_2hrs = df_id[(df_id['date_time_w_tz'] >= start) & (df_id['date_time_w_tz'] <= end)]
    # class_eps_2hrs = class_eps_2hrs.drop(index)
    if class_eps_2hrs.shape[0] == 0:
        count_eps_2hrs.append(0)
        count_mins_2hrs.append(0)
        count_eps_stress_2hrs.append(0)
        count_eps_not_stress_2hrs.append(0)
        count_eps_prompt.append(0)
    else:
        prompts = df_id_2hrs['isTriggered'] == True
        prompts_df = df_id_2hrs[prompts]
        count_eps_prompt.append(prompts_df.shape[0])
        # these are the classified episodes within the next two hours. Now,
        # calculate how many minutes they lasted:
        count_eps_2hrs.append(class_eps_2hrs.shape[0])
        # mark as stress or no_stress episode:
        stress_eps = class_eps_2hrs['Stress_Episode_Classification'] == 2.0
        not_stress_eps = class_eps_2hrs['Stress_Episode_Classification'] == 0.0
        stress_eps_df = class_eps_2hrs[stress_eps]
        not_stress_eps_df = class_eps_2hrs[not_stress_eps]
        nrow_stress = stress_eps_df.shape[0]
        nrow_not_stress = not_stress_eps_df.shape[0]
        count_eps_stress_2hrs.append(nrow_stress)
        count_eps_not_stress_2hrs.append(nrow_not_stress)
        class_count = 0
        for index2, row2 in class_eps_2hrs.iterrows():
            if row2['start_date_time'] <= start:
                # this is the episde whos peak is start.
                cutoff_end = row2['end_date_time']
                cutoff_start = start
                if row2['end_date_time'] >= end:
                    cutoff_end = end
                diff =  cutoff_end - cutoff_start
                minutes = float(diff.seconds)/float(60)
                class_count += minutes
            elif row2['end_date_time'] >= end:
                # this episode's end time proceeds past end. Only count until end:
                cutoff_end = end
                cutoff_start = row2['start_date_time']
                diff =  cutoff_end - cutoff_start
                minutes = float(diff.seconds)/float(60)
                class_count += minutes
            else:
                cutoff_end = row2['end_date_time']
                cutoff_start = row2['start_date_time']
                diff =  cutoff_end - cutoff_start
                minutes = float(diff.seconds)/float(60)
                class_count += minutes
        count_mins_2hrs.append(class_count)

df['count_class_mins_2hrs'] = count_mins_2hrs
df['percent_class_mins_2hrs'] = df['count_class_mins_2hrs']/float(120)
df['count_eps_2hrs'] = count_eps_2hrs
df['count_eps_stress_2hrs'] = count_eps_stress_2hrs
df['count_eps_not_stress_2hrs'] = count_eps_not_stress_2hrs
df['count_eps_prompt'] = count_eps_prompt

# How many episodes does a person usually have in 2 hours?
# How long does an episode usually last?

df['avg_ep_duration_each_2hrs'] = [float(i)/float(j) if j > 0 else 0 for i, j in zip(df['count_class_mins_2hrs'], df['count_eps_2hrs'])]
eps_in_2_hours = df.groupby(['participant_id'])['count_eps_2hrs'].median().reset_index(name = 'avg_eps_in_2hrs')
eps_in_2_hours['avg_ep_duration_2hrs'] = df.groupby(['participant_id'])['avg_ep_duration_each_2hrs'].median().values
eps_in_2_hours['avg_percent_class_2hrs'] = df.groupby(['participant_id'])['percent_class_mins_2hrs'].median().values
eps_in_2_hours.to_csv('eps_in_2_hours.csv', index=False)

[f(x) if condition else g(x) for x in sequence]
# Fraction of quality readings in 2 hour windows following an intervention prompt,
# fraction of quality readings in 2 hour windows that do not begin with an intervention
# prompt.

interventions = df['isTriggered'] == True
not_interventions = df['isTriggered'] == False
interventions_df = df[interventions]
not_interventions_df = df[not_interventions]

interventions_df['avg_ep_duration_each_2hrs'] = [float(i)/float(j) if j > 0 else 0 for i, j in zip(interventions_df['count_class_mins_2hrs'], interventions_df['count_eps_2hrs'])]
eps_in_2_hours_following_ints = interventions_df.groupby(['participant_id'])['count_eps_2hrs'].median().reset_index(name = 'avg_eps_in_2hrs')
eps_in_2_hours_following_ints['avg_ep_duration_2hrs'] = interventions_df.groupby(['participant_id'])['avg_ep_duration_each_2hrs'].median().values
eps_in_2_hours_following_ints['avg_percent_class_2hrs'] = interventions_df.groupby(['participant_id'])['percent_class_mins_2hrs'].median().values
eps_in_2_hours_following_ints.to_csv('eps_in_2_hours_following_ints.csv', index=False)

not_interventions_df['avg_ep_duration_each_2hrs'] = [float(i)/float(j) if j > 0 else 0 for i, j in zip(not_interventions_df['count_class_mins_2hrs'], not_interventions_df['count_eps_2hrs'])]
eps_in_2_hours_following_not_ints = not_interventions_df.groupby(['participant_id'])['count_eps_2hrs'].median().reset_index(name = 'avg_eps_in_2hrs')
eps_in_2_hours_following_not_ints['avg_ep_duration_2hrs'] = not_interventions_df.groupby(['participant_id'])['avg_ep_duration_each_2hrs'].median().values
eps_in_2_hours_following_not_ints['avg_percent_class_2hrs'] = not_interventions_df.groupby(['participant_id'])['percent_class_mins_2hrs'].median().values
eps_in_2_hours_following_not_ints.to_csv('eps_in_2_hours_following_not_ints.csv', index=False)

# Fraction of 2 hour windows that do not begin with an intervention prompt
# but a prompt occurs during the two hours.

not_int_summary = not_interventions_df.groupby('participant_id')['count_eps_prompt'].sum().reset_index(name = 'num_prompts_in2hrs')
not_int_summary['num_rands_not_int'] = not_interventions_df.groupby('participant_id')['count_eps_prompt'].size().values
not_int_summary['prop_prompts_in_2hrs'] = [float(i)/float(j) for i,j in zip(not_int_summary['num_prompts_in2hrs'], not_int_summary['num_rands_not_int'])]
not_int_summary.to_csv('not_int_summary.csv', index=False)

# An initial recommendation for which 2 hour
# windows we can actually use for intervention assessment.

df1 = df.groupby(['participant_id']).size()


cutoff_obs = df['percent_class_mins_2hrs'] > 0.5
cutoff_df = df[cutoff_obs]
df2 = cutoff_df.groupby(['participant_id']).size()

cutoff_obs = df['percent_class_mins_2hrs'] > 0.6
cutoff_df = df[cutoff_obs]
df3 = cutoff_df.groupby(['participant_id']).size()

cutoff_obs = df['percent_class_mins_2hrs'] > 0.7
cutoff_df = df[cutoff_obs]
df4 = cutoff_df.groupby(['participant_id']).size()

cutoff_obs = df['percent_class_mins_2hrs'] > 0.8
cutoff_df = df[cutoff_obs]
df5 = cutoff_df.groupby(['participant_id']).size()

cutoff_table = pd.concat([df1,df2,df3,df4,df5], ignore_index=False, axis=1).reset_index()
cutoff_table.columns = ['participant_id', 'num_rands', 'cutoff_0.5', 'cutoff_0.6', 'cutoff_0.7', 'cutoff_0.8']
cutoff_table.to_csv('cutoff_table.csv', index=False)

##############################################
# PLOT: Percent classified stress/not-stress episodes
# episodes within 2 hours following a randomisation
# decision pint for participant 202. Each point in the plot
# represents a randomisation decision point where either an
# intervention was delivered (orange) or it was not (blue).
##############################################

plt.close("all")

id_df = df[df['participant_id'] == 202]

ax = sns.scatterplot(x='date_time', y='percent_class_mins_2hrs', hue='isTriggered', data=id_df)
ax.set_xlim(id_df['date_time'].min() - timedelta(days=1), id_df['date_time'].max()+timedelta(days=1))

ax.set(
  xlabel = 'Day',
  ylabel = 'Percent classified stress/not-stress episodes within 2 hours'
)
ax.set_title('Participant 202')
plt.show()

#########


df = pd.read_csv('percent_episodes_2hr.csv')
# add date to df:
df['date_time'] = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in df.date_time]
df['date'] = df.date_time.dt.date

new_df = df[['date_time', 'participant_id', 'percent_episodes_2hr']]


# Make day number column (from first randomisation):
rand_day_in_study = []
for index, row in df.iterrows():
    id = row['participant_id']
    min_id_date = min(df[df['participant_id'] == id].date)
    curr_date = row['date']
    delta = curr_date - min_id_date
    days = delta.days + 1
    rand_day_in_study.append(days)

df['rand_day_in_study'] = rand_day_in_study

# Filter by intervention:
int_given = df['isTriggered'] == True
int_not_given = df['isTriggered'] == False

int = df[int_given]
int_not = df[int_not_given]

stressed_int = int['isStress'] == True
not_stress_int = int['isStress'] == False

int_stressed = int[stressed_int]
int_not_stressed = int[not_stress_int]

int_stress_groups = int_stressed.groupby(['date', 'participant_id']).size().reset_index(name='int_per_day')
int_stress_groups['isStress'] = np.repeat(True, int_stress_groups.shape[0], axis=0)

int_not_stress_groups = int_not_stressed.groupby(['date', 'participant_id']).size().reset_index(name='int_per_day')
int_not_stress_groups['isStress'] = np.repeat(False, int_not_stress_groups.shape[0], axis=0)

int_df = pd.concat([int_stress_groups, int_not_stress_groups], ignore_index=True)

# Make day number column (from first randomisation):
rand_day_in_study = []
for index, row in int_df.iterrows():
    id = row['participant_id']
    min_id_date = min(df[df['participant_id'] == id].date)
    curr_date = row['date']
    delta = curr_date - min_id_date
    days = delta.days + 1
    rand_day_in_study.append(days)

int_df['rand_day_in_study'] = rand_day_in_study

##############################################
# Number of interventions grouped by 'stress'
# and 'not_stressed' per day within the study
# (starting from first randomisation day).
##############################################

sns.set(style="ticks", palette="pastel")

ax = sns.boxplot(x="rand_day_in_study", y="int_per_day",
            hue="isStress", palette=["m", "g"],
            data=int_df)

medians = int_df.groupby(['rand_day_in_study', 'isStress'])['int_per_day'].median().reset_index(name='median')
nobs = int_df.groupby(['rand_day_in_study', 'isStress'])['participant_id'].nunique().apply(lambda x: 'n: {}'.format(x)).reset_index(name='nobs')

graph_dict = {}
uq_days = int_df.rand_day_in_study.unique()
uq_stress = int_df.isStress.unique()
for day in uq_days:
    graph_dict[str(day)] = {}
    for stress in uq_stress:
        graph_dict[str(day)][str(stress)] = []

for index, row in medians.iterrows():
    day = str(row['rand_day_in_study'])
    stress = str(row['isStress'])
    graph_dict[day][stress].append(row['median'])
    row_nobs = nobs.iloc[index]
    graph_dict[day][stress].append(row_nobs['nobs'])

for tick, label in enumerate(ax.get_xticklabels()):
    ax_day = label.get_text()
    for j, ax_stress in enumerate(ax.get_legend_handles_labels()[1]):
        x_offset = (j - 0.5) * 2/5
        med_val = graph_dict[ax_day][ax_stress][0]
        num = graph_dict[ax_day][ax_stress][1]
        ax.text(tick + x_offset, med_val + 0.1, num,
                horizontalalignment='center', size='x-small', color='black', weight='semibold')

ax.set(
  xlabel = 'Day',
  ylabel = 'Number of interventions'
)

plt.show()

##############################################
# Number of interventions per day within the study
# (starting from first randomisation day).
##############################################

ax3 = sns.boxplot(
    x = "rand_day_in_study",
    y = "int_per_day", data=int_df)

# Calculate number of obs per group & median to position labels
medians = int_df.groupby(['rand_day_in_study'])['int_per_day'].median().values
nobs = int_df.groupby(['rand_day_in_study'])['participant_id'].nunique().values
nobs = [str(x) for x in nobs.tolist()]
nobs = ["n: " + i for i in nobs]

# Add it to the plot
pos = range(len(nobs))
for tick,label in zip(pos, ax3.get_xticklabels()):
    ax3.text(pos[tick], medians[tick] + 0.03, nobs[tick],
    horizontalalignment='center', size='x-small', color='black', weight='semibold')

ax3.set(
  xlabel = 'Day',
  ylabel = 'Number of interventions'
)
#
# plt.ylim([0, max(int_df.int_per_day)] + 1)
# plt.xlim([-1, max(int_df.days_in_study_from_randomisation)])
plt.show()

##############################################
# Number of randomisations per day within the study
# (starting from first randomisation day).
##############################################

groups = df.groupby(['date', 'participant_id']).size().reset_index(name='num_episodes')

rand_day_in_study = []
for index, row in groups.iterrows():
    id = row['participant_id']
    min_id_date = min(df[df['participant_id'] == id].date)
    curr_date = row['date']
    delta = curr_date - min_id_date
    days = delta.days + 1
    rand_day_in_study.append(days)

groups['rand_day_in_study'] = rand_day_in_study

# num episodes on day 1, num episodes on day 2, etc...

ax = sns.boxplot(
    x = "rand_day_in_study",
    y = "num_episodes", data=groups)

# Calculate number of obs per group & median to position labels

medians = groups.groupby(['rand_day_in_study'])['num_episodes'].median().values
nobs = groups.groupby(['rand_day_in_study'])['participant_id'].nunique().values
nobs = [str(x) for x in nobs.tolist()]
nobs = ["n: " + i for i in nobs]

# Add it to the plot
pos = range(len(nobs))
for tick,label in zip(pos,ax.get_xticklabels()):
    ax.text(pos[tick], medians[tick] + 0.03, nobs[tick],
    horizontalalignment='center', size='x-small', color='black', weight='semibold')

ax.set(
  xlabel = 'Day',
  ylabel = 'Number of randomizations'
)

# plt.show()
df.groupby(['rand_day_in_study'])['percent_class_2hr'].describe()
df = df.sort_values(by='date_time')


#use column headers as x values
x = id_df.date_time
# sum all values from DataFrame along vertical axis
y = id_df.percent_class_2hr
scatterplot(x, y, "x_label", "y_label", "title")

plt.close("all")

id_df = df[df['participant_id'] == 202]

ax = sns.scatterplot(x='date_time', y='percent_class_2hr', hue='isTriggered', data=id_df)
ax.set_xlim(id_df['date_time'].min(), id_df['date_time'].max())

plt.show()

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

data = df
ids = np.unique(data.participant_id)
fig, ax = plt.subplots(figsize=(8,6))
for id in ids:
    df_id = data[data.participant_id==id]
    ax.scatter(df_id.date_time, df_id.percent_class_2hr)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.legend()
fig.autofmt_xdate()
plt.show()



# How you begin and end a 2 hour window.
# Which of the windows begin with a intervention prompt.
# I guess some of the windows begin with no intervention but
#  within the window there is an intervention. You need to tell us when this happens.
#
# Fraction of quality readings in 2 hour windows following an intervention prompt.
# Fraction of quality readings in 2 hour windows that do not begin with an intervention prompt.
# Fraction of 2 hour windows that do not begin with an intervention prompt but a prompt occurs
#  during the two hours.
# An initial recommendation for which 2 hour windows we can actually use for
#  intervention assessment.
#

# Fraction of quality readings in 2 hour windows following an intervention prompt.



import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

data = joblib.load('df.pkl')
ids = np.unique(data.participant_id)
fig, axes = plt.subplots(nrows=9, ncols=3, figsize=(10,18))
fig.autofmt_xdate()
j=-1
for i in range(ids.shape[0]):
    if (i%3 == 0):
        j += 1
    k = i % 3
    df_id = data[data.participant_id==ids[i]]
    axes[j,k].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[j,k].scatter(df_id.date_time, df_id.percent_class_2hr)
    axes[j,k].set_title(f"id= {ids[i]}")


fig.tight_layout()

plt.show()






############
