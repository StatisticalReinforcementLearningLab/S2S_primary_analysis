
# Minute level missingness analysis

# Last modified: 23 MAR 2020

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

def minute_rounder(t):
    # Rounds to nearest minute by adding a timedelta minute if seconds >= 30
    return (t.replace(second=0, microsecond=0, minute=t.minute, hour=t.hour)
               +timedelta(minutes=t.second//30))
################################

wd = "/Users/mariannemenictas/Desktop/stress_cleaned_data4"

# use backup data stream since id = 216.

# Create a dictionary of DataFrames for the phone logs for each participant:
# To access each df: e.g., "dfs['phone_log202']".

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

# Convert columns with strings of dictionaries to columns and values (this is needed for
# 'emiInfo' and 'logScheduler'):
logs = {}
for id in all_participant_ids:
    name = 'phone_log_' + str(id)
    df = logs_w_dicts[name]
    # convert string of dictionaries to dictionaries for columns 'emiInfo' and 'logScheduler':
    # NB: 'd==d' checks that values are not nan.
    if 'emiInfo' in df.columns:
        df['emiInfo'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['emiInfo']]
        # df['emiInfo'] = [d if d == d else np.NaN for d in df['emiInfo']]
        # Add keys as columns and values as cells in columns to original data frame:
        df = pd.concat([df.drop(['emiInfo'], axis=1), df['emiInfo'].apply(pd.Series)], axis=1)
        # delete redundant '0' columns created by pd.Series:
        del df[0]
    if 'logScheduler' in df.columns:
        df['logSchedule'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['logSchedule']]
        df = pd.concat([df.drop(['logSchedule'], axis=1), df['logSchedule'].apply(pd.Series)], axis=1)
        del df[0]
    # make datetime object:
    df['date_time'] = [datetime.strptime(i, '%Y/%m/%d %H:%M:%S %p') for i in df['current_time']]
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

stress_label_backup = pd.read_csv(wd + '/' + "stress_label_backup.csv")
uq_ids_stress_label_backup = list(stress_label_backup.participant_id.unique())
stress_label_original = pd.read_csv(wd + '/' + "stress_label_phone_original.csv")
uq_ids_stress_label_original = list(stress_label_original.participant_id.unique())
stress_label_alternative = pd.read_csv(wd + '/' + "stress_label_alternative.csv")
uq_ids_stress_label_alternative = list(stress_label_alternative.participant_id.unique())

stress_activity_backup = pd.read_csv(wd + '/' + "stress_activity_phone_backup.csv")
uq_ids_stress_activity_backup = list(stress_activity_backup.participant_id.unique())
stress_activity_original = pd.read_csv(wd + '/' + "stress_activity_phone_original.csv")
uq_ids_stress_activity_original = list(stress_activity_original.participant_id.unique())
stress_activity_alternative = pd.read_csv(wd + '/' + "stress_activity_phone_alternative.csv")
uq_ids_stress_activity_alternative = list(stress_activity_alternative.participant_id.unique())

all_participant_ids = [int(i) for i in all_participant_ids]

stress_label = pd.DataFrame(columns = ['timestamp', 'event', 'offset', 'participant_id', 'datetime', 'datetime_min_rounder', 'date'])
for id in all_participant_ids:
    if id in uq_ids_stress_label_backup:
        data_to_append = stress_label_backup[stress_label_backup['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_label = stress_label.append(data_to_append)
    elif id in uq_ids_stress_label_original:
        data_to_append = stress_label_original[stress_label_original['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_label = stress_label.append(data_to_append)
    elif id in uq_ids_stress_label_alternative:
        data_to_append = stress_label_alternative[stress_label_alternative['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_label = stress_label.append(data_to_append)

stress_label = stress_label.drop_duplicates().reset_index(drop=True)
# "event" column in stress_label represents stress value cStress model:
#   no stress (0), stress(1), unsure(2).

stress_activity = pd.DataFrame(columns = ['timestamp', 'event', 'offset', 'participant_id', 'datetime', 'datetime_min_rounder', 'date'])
for id in all_participant_ids:
    if id in uq_ids_stress_activity_backup:
        data_to_append = stress_activity_backup[stress_activity_backup['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_activity = stress_activity.append(data_to_append)
    elif id in uq_ids_stress_activity_original:
        data_to_append = stress_activity_original[stress_activity_original['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_activity = stress_activity.append(data_to_append)
    elif id in uq_ids_stress_activity_alternative:
        data_to_append = stress_activity_alternative[stress_activity_alternative['participant_id'] == id]
        data_to_append['datetime'] = [date_time(i) for i in data_to_append['timestamp']]
        data_to_append['datetime_min_rounder'] = [minute_rounder(i) for i in data_to_append['datetime']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        stress_activity = stress_activity.append(data_to_append)

stress_activity = stress_activity.drop_duplicates().reset_index(drop=True)

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

# Episode data:
stress_prob_original = pd.read_csv(wd + '/' + "stress_probability_phone_original.csv")
uq_ids_stress_prob_original = list(stress_prob_original.participant_id.unique())
stress_probs_backup = pd.read_csv(wd + '/' + "stress_probability_phone_backup.csv")
uq_ids_stress_prob_backup = list(stress_probs_backup.participant_id.unique())
stress_prob_alternative = pd.read_csv(wd + '/' + "stress_probability_phone_alternative.csv")
uq_ids_stress_prob_alternative = list(stress_prob_alternative.participant_id.unique())

stress_prob = pd.DataFrame(columns = ['date', 'datetime', 'timestamp', 'offset', 'event', 'participant_id'])
for id in all_participant_ids:
    if id in uq_ids_stress_prob_backup:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime', 'timestamp', 'offset', 'event', 'participant_id'])
        data = stress_probs_backup[stress_probs_backup['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        stress_prob = stress_prob.append(data_to_append)
    elif id in uq_ids_stress_prob_original:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime', 'timestamp', 'offset', 'event', 'participant_id'])
        data = stress_prob_original[stress_prob_original['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        stress_prob = stress_prob.append(data_to_append)
    elif id in uq_ids_stress_prob_alternative:
        data_to_append = pd.DataFrame(columns = ['date', 'datetime', 'timestamp', 'offset', 'event', 'participant_id'])
        data = stress_prob_alternative[stress_prob_alternative['participant_id'] == id].reset_index(drop=True)
        data_to_append['datetime'] = [date_time(i) for i in data['timestamp']]
        data_to_append['date'] = [i.date() for i in data_to_append['datetime']]
        data_to_append['event'] = data['event']
        data_to_append['participant_id'] = data['participant_id']
        stress_prob = stress_prob.append(data_to_append)

stress_prob = stress_prob.drop_duplicates().reset_index(drop=True)


not_missing_mins = {}
not_missing_mins_frac = {}
not_missing_ep_mins = {}
not_missing_ep_mins_frac = {}
for id in participants_for_analysis:
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = stress_activity[stress_activity['participant_id'] == id]
    id_episodes = episodes[episodes['participant_id'] == id]
    id_stress_label = stress_label[stress_label['participant_id'] == id]
    id_prob = stress_prob[stress_prob['participant_id'] == id]
    day = mrt_id_start_day
    not_missing_mins[id] = {}
    not_missing_mins_frac[id] = {}
    not_missing_ep_mins[id] = {}
    not_missing_ep_mins_frac[id] = {}
    while day <=  mrt_id_tenth_day:
        # plot label and probability per day in MRT:
        id_label_day = id_stress_label[id_stress_label['date'] == day]
        id_prob_day = id_prob[id_prob['date'] == day]
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_activity_day = id_activity[id_activity['date'] == day]
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        not_missing_mins[id][day] = []
        not_missing_mins_frac[id][day] = []
        not_missing_ep_mins[id][day] = []
        not_missing_ep_mins_frac[id][day] = []
        if available_dec_ponts.shape[0] > 0:
            available_decision_times = list(available_dec_ponts['date_time'])
            for avai_dec_time in available_decision_times:
                # for each decision time, what is percent of non-missing minutes for two hours
                # following an available decision time:
                start_time = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                if start_time == 'NaT':
                    start_time_localize = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                    start_time = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                end_time = start_time + timedelta(hours = 2)
                id_episodes_day_2hour = id_episodes_day[(id_episodes_day['datetime_end'] >= start_time) & (id_episodes_day['datetime_start'] <= end_time)]
                labels_2hour = id_label_day[(id_label_day['datetime'] >= start_time) & (id_label_day['datetime'] <= end_time)]
                activity_2hour = id_activity_day[(id_activity_day['datetime'] >= start_time) & (id_activity_day['datetime'] <= end_time)]
                # count minutes stressed:
                stress_mins = labels_2hour[labels_2hour['event'] == 1.0]
                stress_min_count = stress_mins.shape[0]
                # count minutes not-stressed:
                not_stress_mins = labels_2hour[labels_2hour['event'] == 0.0]
                not_stress_min_count = not_stress_mins.shape[0]
                # count minutes that are both 'unsure' and active:
                unsure_mins = labels_2hour[labels_2hour['event'] == 2.0]
                active_mins = activity_2hour[activity_2hour['event'] == 1.0]
                unsure_active_mins_count = np.sum([int(i in active_mins.datetime_min_rounder) for i in unsure_mins.datetime_min_rounder])
                total_mins = stress_min_count + not_stress_min_count + unsure_active_mins_count
                total_mins_frac = round(total_mins/float(120), 1)
                not_missing_mins[id][day].append(total_mins)
                not_missing_mins_frac[id][day].append(total_mins_frac)
        # EPISODES:
        # count minutes stressed:
        stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 2.0]
        stress_ep_min_count = 0
        if stress_eps.shape[0] > 0:
            for index, row in stress_eps.iterrows():
                if row.datetime_start <= start_time:
                    stress_ep_min_count += ((row.datetime_end - start_time).seconds//60)%60
                elif row.datetime_end >= end_time:
                    stress_ep_min_count += ((end_time - row.datetime_start).seconds//60)%60
                else:
                    stress_ep_min_count += ((row.datetime_end - row.datetime_start).seconds//60)%60
        # count minutes not stressed:
        not_stress_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 0.0]
        not_stress_ep_min_count = 0
        if not_stress_eps.shape[0] > 0:
            for index, row in not_stress_eps.iterrows():
                if row.datetime_start <= start_time:
                    not_stress_ep_min_count += ((row.datetime_end - start_time).seconds//60)%60
                elif row.datetime_end >= end_time:
                    not_stress_ep_min_count += ((end_time - row.datetime_start).seconds//60)%60
                else:
                    not_stress_ep_min_count += ((row.datetime_end - row.datetime_start).seconds//60)%60
        # count minutes active inside unknown episodes:
        unknown_eps = id_episodes_day_2hour[id_episodes_day_2hour['event'] == 3.0]
        active_ep_mins = 0
        if unknown_eps.shape[0] > 0:
            for index, row in unknown_eps.iterrows():
                if row.datetime_start <= start_time:
                    df = activity_2hour[(activity_2hour['datetime'] >= start_time) & (activity_2hour['datetime'] <= row.datetime_end)]
                    active_ep_mins += df[df['event'] == 1.0].shape[0]
                elif row.datetime_end >= end_time:
                    df = activity_2hour[(activity_2hour['datetime'] >= row.datetime_start) & (activity_2hour['datetime'] <= end_time)]
                    active_ep_mins += df[df['event'] == 1.0].shape[0]
                else:
                    df = activity_2hour[(activity_2hour['datetime'] >= row.datetime_start) & (activity_2hour['datetime'] <= row.datetime_end)]
                    active_ep_mins += df[df['event'] == 1.0].shape[0]
        total_ep_mins = stress_ep_min_count + not_stress_ep_min_count + active_ep_mins
        total_ep_mins_frac = round(total_mins/float(120),1)
        not_missing_ep_mins[id][day].append(total_ep_mins)
        not_missing_ep_mins_frac[id][day].append(total_ep_mins_frac)
        day = day + timedelta(days=1)

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



# can we save anything by interpolating minutes close by?





















######
