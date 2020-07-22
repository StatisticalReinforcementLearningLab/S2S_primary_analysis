
# Python script for comparing/aligning the stress episode classifications 
# at time of randomization within the 10-day MRT phase of the Sense2Stop 
# study. 

# Last modified: 30 JUN 2020.
# Last edited by: Marianne M.

# import necessary modules:

import pandas as pd
import os
import ast
import numpy as np
from datetime import datetime
from datetime import timedelta
import joblib
import pytz

# define function to get datetime from timestamp:

def date_time(intime):
    return (datetime.fromtimestamp(int(intime)/1000, tz=pytz.timezone('America/Chicago')))

# Point to relevant working directory inside Box (these are pointing to cleaned files Marianne has 
# created from the original data files): 

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

all_participant_ids = [int(i) for i in all_participant_ids]

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
        data_to_append['start_timestamp'] = data['StartTime']
        data_to_append['peak_timestamp'] = data['PeakTime']
        data_to_append['end_timestamp'] = data['EndTime']
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
        data_to_append['start_timestamp'] = data['StartTime']
        data_to_append['peak_timestamp'] = data['PeakTime']
        data_to_append['end_timestamp'] = data['EndTime']
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
        data_to_append['start_timestamp'] = data['StartTime']
        data_to_append['peak_timestamp'] = data['PeakTime']
        data_to_append['end_timestamp'] = data['EndTime']
        episodes = episodes.append(data_to_append)

episodes = episodes.drop_duplicates().reset_index(drop=True)

# Convert columns with strings of dictionaries to columns and values (this is needed for
# 'emiInfo' and 'logScheduler'):
logs = {}
for id in all_participant_ids:
    print(id)
    name = 'phone_log_' + str(id)
    df = logs_w_dicts[name]
    df['time_stamp'] = df['timestamp']
    # del df['timestamp']
    # convert string of dictionaries to dictionaries for columns 'emiInfo' and 'logScheduler':
    # NB: 'd==d' checks that values are not nan.
    if 'emiInfo' in df.columns:
        df['emiInfo'] = [ast.literal_eval(d) if d == d else np.NaN for d in df['emiInfo']]
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

# [idx for idx, element in enumerate(df['emiInfo']) if element == element]
# e.g., 881


# From discussions with Elyse and exploration in the data, we know that the following ids do not 
# have any decision points. So, remove them from consideration: 

no_dec_points = [201, 204, 206, 209, 210, 215, 217, 218, 220, 230, 232, 236,
                 237, 239, 241, 246, 247, 254, 257, 263, 270]

remaining_participant_ids = sorted(set(all_participant_ids).difference(set(no_dec_points)))

# Record which date is Quit day (Day 4) for each participant. This is Day 1 of the
# 10 day micro-randomized trial period. This is hard coded in from info provided
# by Elyse Daly (study coordinator at NW):

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

# investigate the first available decision time for id 202:

idVal = 202
key_name = 'phone_log_' + str(idVal)
mrt_id_start_day = mrt_start_day[idVal]
mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
id_episodes = episodes[episodes['participant_id'] == idVal]
day = mrt_id_start_day
id_episodes_day = id_episodes[id_episodes['date'] == day]
id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
int_triggered_condition = id_log_EMI_day['isTriggered'] == True
int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
available_decision_times = list(available_dec_ponts['date_time'])
avai_dec_time_stress_class = list(available_dec_ponts['isStress'])
avai_dec_time, avai_dec_time_class = list(zip(available_decision_times, avai_dec_time_stress_class))[0]
curr_episode = id_episodes_day[(id_episodes_day['datetime_end'] >= avai_dec_time_val) & (id_episodes_day['datetime_start'] <= avai_dec_time_val)]

episodes_202 = episodes[episodes['participant_id'] == 202]
episodes_202_ts = episodes_202[episodes_202['start_timestamp'] == curr_episode.iloc[0].start_timestamp]


# Create a data frame that allows computation of the count of all available decision times 
# that a user is classified as being in the detected-stressed vs not-detected-stressed 
# episode category as given by both the log files and episode classification files:

indexVal = 0
avai_dec_time_stress_classes = pd.DataFrame()
rand_minus_peak = {}
for idVal in participants_for_analysis:
    rand_minus_peak[idVal] = {}
    print("  id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_episodes = episodes[episodes['participant_id'] == idVal]
    day = mrt_id_start_day
    while day <=  mrt_id_tenth_day:
        rand_minus_peak[idVal][day] = []
        print("  day: ", day)
        id_episodes_day = id_episodes[id_episodes['date'] == day]
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        if available_dec_ponts.shape[0] > 0:
            available_decision_times = list(available_dec_ponts['date_time'])
            avai_dec_time_stress_class = list(available_dec_ponts['isStress'])
            time_stamps = list(available_dec_ponts['time_stamp'])
            for avai_dec_time, avai_dec_time_class, time_stamp_val in zip(available_decision_times, avai_dec_time_stress_class, time_stamps):
                # find current stress classification from cStress episode classification data file to make 
                # sure that this matches what the log files indicate: 
                avai_dec_time_val = avai_dec_time
                # avai_dec_time_val = pd.to_datetime(avai_dec_time).tz_localize('America/Chicago', ambiguous = 'NaT')
                # if avai_dec_time_val == 'NaT':
                #     avai_dec_time_val = pd.to_datetime(avai_dec_time).tz_localize('Europe/London') # this localizes the timestamp.
                #     avai_dec_time_val = pd.to_datetime(start_time_localize).tz_convert('America/Chicago') # this now converts the localized version to chicago timestamp.
                curr_episode = id_episodes_day[(id_episodes_day['datetime_end'] >= avai_dec_time_val) & (id_episodes_day['datetime_start'] <= avai_dec_time_val)]
                if curr_episode.shape[0] == 0: 
                    print("WARNING: id ", idVal, " for available decision time ", avai_dec_time, "has no classification for this current episode!!!!!!")
                    ep_class = 'does_not_exist'
                    rand_minus_peak[idVal][day].append(np.nan)
                elif curr_episode.shape[0] > 0:
                    val = round((abs(avai_dec_time - curr_episode.iloc[0].datetime_peak)).seconds/60, 2)
                    if val > 1000: 
                        print("----WARNING: val: ", val, "id: ", idVal, " rand ts: ", 
                              time_stamp_val, "rand time:", avai_dec_time_val, "peak time: ", curr_episode.iloc[0].datetime_peak, "----")
                    rand_minus_peak[idVal][day].append(val)
                    if curr_episode.iloc[0].event == 3.0: 
                        ep_class = "unknown"
                        print("WARNING: id ", idVal, " for time stamp ", time_stamp_val, "is also classified UNKOWN for this current episode!!!!!!")
                    elif curr_episode.iloc[0].event == 2.0: 
                        ep_class = "stress"
                    elif curr_episode.iloc[0].event == 0.0:
                        ep_class = "no_stress"
                # Now check if we can find classified episodes that is within the window of time from the available 
                # decition time and this time plus 5 mins (as suggested by Monowar and Soujanya to try to understand this 
                # discrepancy more.): 
                # avai_dec_time_val_plus_5 = avai_dec_time_val + timedelta(minutes=5)
                # curr_episode_plus_5 = id_episodes_day[(id_episodes_day['datetime_end'] >= avai_dec_time_val) & (id_episodes_day['datetime_start'] <= avai_dec_time_val_plus_5)]
                # if curr_episode_plus_5.shape[0] == 0: 
                #     print("WARNING: id ", idVal, " for available decision time PLUS 5 MIN", avai_dec_time, "has no classification for this current episode!!!!!!")
                #     ep_class_plus_5 = 'does_not_exist'
                # elif curr_episode_plus_5.shape[0] > 0:
                #     if curr_episode_plus_5.iloc[0].event == 3.0: 
                #         ep_class_plus_5 = "unknown"
                #     elif curr_episode_plus_5.iloc[0].event == 2.0: 
                #         ep_class_plus_5 = "stress"
                #     elif curr_episode_plus_5.iloc[0].event == 0.0:
                #         ep_class_plus_5 = "no_stress"
                # # Now check if we can find classified episodes that is within the window of time from the available 
                # # decition time and this time plus 10 mins (as suggested by Monowar and Soujanya to try to understand this 
                # # discrepancy more.): 
                # avai_dec_time_val_plus_10 = avai_dec_time_val + timedelta(minutes=10)
                # curr_episode_plus_10 = id_episodes_day[(id_episodes_day['datetime_end'] >= avai_dec_time_val) & (id_episodes_day['datetime_start'] <= avai_dec_time_val_plus_10)]
                # if curr_episode_plus_10.shape[0] == 0: 
                #     print("WARNING: id ", idVal, " for available decision time PLUS 10 MIN", avai_dec_time, "has no classification for this current episode!!!!!!")
                #     ep_class_plus_10 = 'does_not_exist'
                # elif curr_episode_plus_10.shape[0] > 0:
                #     if curr_episode_plus_10.iloc[0].event == 3.0: 
                #         ep_class_plus_10 = "unknown"
                #     elif curr_episode_plus_10.iloc[0].event == 2.0: 
                #         ep_class_plus_10 = "stress"
                #     elif curr_episode_plus_10.iloc[0].event == 0.0:
                #         ep_class_plus_10 = "no_stress"
                rows_to_append = pd.DataFrame({
                                'id': idVal,
                                'day': day,
                                'available_decision_point': avai_dec_time,
                                'rand_alg_is_stress': avai_dec_time_class, 
                                'episode_class': ep_class}, index=[indexVal])
                                # 'episode_class_plus_5': ep_class_plus_5,
                                # 'episode_class_plus_10': ep_class_plus_10}, index=[indexVal])
                indexVal = indexVal + 1
                avai_dec_time_stress_classes = avai_dec_time_stress_classes.append(rows_to_append)
        day = day + timedelta(days=1)

# average time after peak that the intervention is sent: 

rand_minus_peak_means = {}
for idVal in participants_for_analysis:
    days = list(rand_minus_peak[idVal].keys())
    rand_minus_peak_means[idVal] = []
    for day in days:
        rand_minus_peak_means[idVal].append(round(np.nanmean(rand_minus_peak[idVal][day]),2))

rand_minus_peak_means_across_days = []
for idVal in participants_for_analysis: 
    rand_minus_peak_means_across_days.append(round(np.nanmean(rand_minus_peak_means[idVal]), 2))

#########################################################################################
####### TO MONOWAR: 
#######
#######   - Please run all of the above code after replacing your working directory 
#######     on line 28 to one pointing to the Box directory's the appropriate folder. 
#######     (i.e., "~/Box/MD2K Northwestern/Processed Data/primary_analysis/data/stress_cleaned_data")
#######     This is a folder that I've created with cleaned data files.
#######
#######   - Then, the following line shows a data frame with the episode classifications given by the 
#######     two files for participant 202. 

data_202 = avai_dec_time_stress_classes[avai_dec_time_stress_classes['id'] == 202]

# Descriptions of columns in data_202: 
#
# - The column "rand_alg_is_stress" shows whethere the randomization algorithm at the available 
#     decision time detected that the individual was within a detected stressed episode or a not 
#     detected stressed episode. 
# - The column "episode_class" is the stress episode classification provided by the stress episode 
#     classification file. 
# - The column "episode_class_plus_5" is the stress episode classification provided by the stress episode
#     classification file whilst also allowing for an additional 5 minutes following the available 
#     decision time. 
# - The column "episode_class_plus 10" is the stress episode classification provided by the stress episode
#     classification file whilst also allowing for an additional 10 minutes following the available
#     decision time. 




# The below code creates the tables I ave sent you in email exchanges: 

# Create row counts in table provided in email to Tim, Soujanya, Shahin and Susan: 

isStressTrue = list(avai_dec_time_stress_classes['rand_alg_is_stress'] == True)
isStressFalse = list(avai_dec_time_stress_classes['rand_alg_is_stress'] == False)

EpClassStress = list(avai_dec_time_stress_classes['episode_class'] == 'stress')
EpClassNoStress = list(avai_dec_time_stress_classes['episode_class'] == 'no_stress')
EpClassUnknown = list(avai_dec_time_stress_classes['episode_class'] == 'unknown')
NoEpClass = list(avai_dec_time_stress_classes['episode_class'] == 'does_not_exist')

# using the timestamp from the phone log files: 

np.sum([i & j for (i,j) in zip(isStressTrue, EpClassStress)])
np.sum([i & j for (i,j) in zip(isStressTrue, EpClassNoStress)])
np.sum([i & j for (i,j) in zip(isStressTrue, EpClassUnknown)])
np.sum([i & j for (i,j) in zip(isStressTrue, NoEpClass)])

np.sum([i & j for (i,j) in zip(isStressFalse, EpClassStress)])
np.sum([i & j for (i,j) in zip(isStressFalse, EpClassNoStress)])
np.sum([i & j for (i,j) in zip(isStressFalse, EpClassUnknown)])
np.sum([i & j for (i,j) in zip(isStressFalse, NoEpClass)])

# # using the time window from the timestamp from the phone log files + 5 mins: 

# EpClassPlus5Stress = list(avai_dec_time_stress_classes['episode_class_plus_5'] == 'stress')
# EpClassPlus5NoStress = list(avai_dec_time_stress_classes['episode_class_plus_5'] == 'no_stress')
# EpClassPlus5Unknown = list(avai_dec_time_stress_classes['episode_class_plus_5'] == 'unknown')
# NoEpClassPlus5 = list(avai_dec_time_stress_classes['episode_class_plus_5'] == 'does_not_exist')

# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus5Stress)])
# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus5NoStress)])
# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus5Unknown)])
# np.sum([i & j for (i,j) in zip(isStressTrue, NoEpClassPlus5)])

# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus5Stress)])
# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus5NoStress)])
# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus5Unknown)])
# np.sum([i & j for (i,j) in zip(isStressFalse, NoEpClassPlus5)])

# # using the time window from the timestamp from the phone log files + 10 mins: 

# EpClassPlus10Stress = list(avai_dec_time_stress_classes['episode_class_plus_10'] == 'stress')
# EpClassPlus10NoStress = list(avai_dec_time_stress_classes['episode_class_plus_10'] == 'no_stress')
# EpClassPlus10Unknown = list(avai_dec_time_stress_classes['episode_class_plus_10'] == 'unknown')
# NoEpClassPlus10 = list(avai_dec_time_stress_classes['episode_class_plus_10'] == 'does_not_exist')

# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus10Stress)])
# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus10NoStress)])
# np.sum([i & j for (i,j) in zip(isStressTrue, EpClassPlus10Unknown)])
# np.sum([i & j for (i,j) in zip(isStressTrue, NoEpClassPlus10)])

# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus10Stress)])
# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus10NoStress)])
# np.sum([i & j for (i,j) in zip(isStressFalse, EpClassPlus10Unknown)])
# np.sum([i & j for (i,j) in zip(isStressFalse, NoEpClassPlus10)])



