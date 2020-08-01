
# Show the extent of missing data in the primary outcome 
# for the Sense2Stop MRT. Also, create a data set in order 
# to predict missing episodes.

# Last changed: 30 JUL 2020

# import modules:

import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

from user_defined_modules import date_time
from user_defined_modules import minute_rounder

wd_cleaned_data = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/stress_cleaned_data"

file_marker = 'phone_log_backup'
participant_ids_backup = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd_cleaned_data) if file_marker in filename]
participant_ids_backup.sort()

file_marker = 'phone_log_original'
participant_ids_original = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd_cleaned_data) if file_marker in filename]
participant_ids_original.sort()

file_marker = 'phone_log_alternative'
participant_ids_alternative = [filename[len(file_marker):len(file_marker)+3] for filename in os.listdir(wd_cleaned_data) if file_marker in filename]
participant_ids_alternative.sort()

all_participant_ids = set(participant_ids_original) | set(participant_ids_backup) | set(participant_ids_alternative)
all_participant_ids = sorted(all_participant_ids)

all_participant_ids = [int(i) for i in all_participant_ids]

# Check if all expected ids are represented in the raw data:

all_expected_inds = set(range(201, 271))
all_received_inds = set([int(i) for i in all_participant_ids])
missing_inds = all_expected_inds.difference(all_received_inds) # no missing inds

# Import pickles from pickle jar:

pickle_jar = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/"

with open(pickle_jar + 'log_dict.pkl', 'rb') as handle:
    logs = pickle.load(handle)

activity = pd.read_pickle(pickle_jar + "activity_df.pkl")
quality_ecg = pd.read_pickle(pickle_jar + "quality_ecg_df.pkl")
quality_rep = pd.read_pickle(pickle_jar + "quality_rep_df.pkl")
stress_episode_classifications = pd.read_pickle(pickle_jar + "stress_episode_classification_df.pkl")
day_start = pd.read_pickle(pickle_jar + "day_start_df.pkl")
day_end = pd.read_pickle(pickle_jar + "day_end_df.pkl")

# print unique dates in log files:

for id in all_participant_ids:
    print(id)
    value_name = 'phone_log_' + str(id)
    uq_dates = sorted(set([date_time(i).date() for i in logs[value_name]['time_stamp']]))
    print(uq_dates)

no_dec_points = [201, 204, 206, 209, 210, 215, 217, 218, 220, 230, 232, 236,
                 237, 239, 241, 246, 247, 254, 257, 263, 270]
remaining_participant_ids = sorted(set(all_participant_ids).difference(set(no_dec_points)))

# store participant micro-radomization start days for the 47 participants
# we are keeping for analysis. This is hard coded in from info provided
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

# Show proportions of missing data: 

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
    print("id: ", id)
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == id]
    id_episodes = stress_episode_classifications[stress_episode_classifications['participant_id'] == id]
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
        print("day: ", day)
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
                        # first check to see if the entire episode (wherever it occurs within the 120 minutes) is unknown due to 
                        # physical activity. This would mean that the number of physical activity minutes from start to peak is 
                        # greater than the number of minutes from start to peak / 2: 
                        time_start_to_peak = (minute_rounder(row.datetime_peak) - minute_rounder(row.datetime_start)).seconds//60
                        df_active_class_start_to_peak = id_activity_day_2hour[(id_activity_day_2hour['datetime'] >= row.datetime_start) & (id_activity_day_2hour['datetime'] <= row.datetime_peak)]
                        df_active_start_to_peak = df_active_class_start_to_peak[df_active_class_start_to_peak['event'] == 1.0]
                        num_mins_active_start_to_peak = df_active_start_to_peak.shape[0]
                        if num_mins_active_start_to_peak >= time_start_to_peak/2: 
                            # This unknown episode is due to physical activity. Now count the number of 
                            # minutes in this entire episode based on where this episode lies in the 120 mins:
                            if row.datetime_start <= start_time:
                                # WARNING: this should technically never happen since the randomization time should not be within an 
                                # unknown episode. However, we know that the data is such that this occurs a few times (due to a bug?)
                                # In this case, we plan to remove such randomization times in the primary analysis. So, continue and don't 
                                # count this:
                                continue
                            elif row.datetime_end >= end_time:
                                unknown_due_to_activity_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_activity_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
                        else: 
                            # this episode is unknown due to bad quality data: 
                            if row.datetime_start <= start_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(start_time)).seconds//60
                            elif row.datetime_end >= end_time:
                                unknown_due_to_bad_data_mins += (minute_rounder(end_time) - minute_rounder(row.datetime_start)).seconds//60
                            else:
                                unknown_due_to_bad_data_mins += (minute_rounder(row.datetime_end) - minute_rounder(row.datetime_start)).seconds//60
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

average_per_id_not_missing_mins_frac = []
for id in average_not_missing_mins_frac.keys(): 
    average_per_id_not_missing_mins_frac.append(round(np.nanmean(average_not_missing_mins_frac[id]), 2))

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
    id_episodes = stress_episode_classifications[stress_episode_classifications['participant_id'] == idVal]
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

# Create row counts:

isStressTrue = list(avai_dec_time_stress_classes['rand_alg_is_stress'] == True)
isStressFalse = list(avai_dec_time_stress_classes['rand_alg_is_stress'] == False)

EpClassStress = list(avai_dec_time_stress_classes['episode_class'] == 'stress')
EpClassNoStress = list(avai_dec_time_stress_classes['episode_class'] == 'no_stress')
EpClassUnknown = list(avai_dec_time_stress_classes['episode_class'] == 'unknown')
NoEpClass = list(avai_dec_time_stress_classes['episode_class'] == 'does_not_exist')

# using the timestamp from the phone log files:

np.sum([i & j for (i, j) in zip(isStressTrue, EpClassStress)])
np.sum([i & j for (i, j) in zip(isStressTrue, EpClassNoStress)])
np.sum([i & j for (i, j) in zip(isStressTrue, EpClassUnknown)])
np.sum([i & j for (i, j) in zip(isStressTrue, NoEpClass)])

np.sum([i & j for (i, j) in zip(isStressFalse, EpClassStress)])
np.sum([i & j for (i, j) in zip(isStressFalse, EpClassNoStress)])
np.sum([i & j for (i, j) in zip(isStressFalse, EpClassUnknown)])
np.sum([i & j for (i, j) in zip(isStressFalse, NoEpClass)])

# How many hours in a user's day (according to their available decision times?)
# Here, we also make use of the start and end time data:

hours_in_day = {}
for idVal in participants_for_analysis:
    print("  id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_start_times = day_start[day_start['participant_id'] == idVal]
    id_end_times = day_end[day_end['participant_id'] == idVal]
    day = mrt_id_start_day
    hours_in_day[idVal] = []
    while day <= mrt_id_tenth_day:
        print("  day: ", day)
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day]
        id_start_times_day = id_start_times[id_start_times['date'] == day]
        id_end_times_day = id_end_times[id_end_times['date'] == day]
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_ponts = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        if available_dec_ponts.shape[0] > 0:
            if id_start_times_day.shape[0] == 1: 
                start_time_val = id_start_times_day.datetime.iloc[0]
            else: 
                start_time_val = np.min(available_dec_ponts.date_time)
            if id_end_times_day.shape[0] == 1: 
                end_time_val = id_end_times_day.datetime.iloc[0]
            else: 
                end_time_val = np.max(available_dec_ponts.date_time)
            time_diff = minute_rounder(end_time_val) - minute_rounder(start_time_val)
            hours_in_day[idVal].append(round(time_diff.seconds/3600, 0))
        else: 
            hours_in_day[idVal].append(np.nan)
        day = day + timedelta(days=1)

# find max hours in each user/day: 

hours_in_day_per_id = []
for idVal in participants_for_analysis:
    hours_in_day_per_id.append(np.nanmax(hours_in_day[idVal]))


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

# Create dataset for predicting missing minutes:

# predict_missing_columns = ['id', 'day', 'available_decision_time', 'episode_type',
#     'previous_episode_type', 'length_of_episode', 'length_of_previous_episode',
#     'prop_good_data', 'prop_good_data_previous_episode']
# predict_missing_df = pd.DataFrame(columns = predict_missing_columns)

# Columns to consider as additions:
# add has lapsed?
# add number of prompts so far (perhaps burdened by prompts?)
# add missing EMA? 

predict_missing_df = pd.DataFrame()
indexVal = 0
for idVal in participants_for_analysis:
    print("id: ", idVal)
    key_name = 'phone_log_' + str(idVal)
    mrt_id_start_day = mrt_start_day[idVal]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    id_activity = activity[activity['participant_id'] == idVal]
    id_episodes = stress_episode_classifications[stress_episode_classifications['participant_id'] == idVal]
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
                                    df = id_activity_day[(id_activity_day['datetime'] >= prev_ep.datetime_start) & (id_activity_day['datetime'] <= prev_ep.datetime_peak)]
                                    active_mins = df[df['event'] == 1.0].shape[0]
                                    if active_mins >= ((minute_rounder(prev_ep.datetime_peak) - minute_rounder(prev_ep.datetime_start)).seconds//60)/2:
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

# now add column that notes whether current row is an available decision point or not (isRand): 

isRand = []
prev_avai_dec_time = 0
for el in missing_df['available_decision_point']: 
    if prev_avai_dec_time == el: 
        isRand.append(0)
        prev_avai_dec_time = el
    else: 
        isRand.append(1)
        prev_avai_dec_time = el

missing_df['isRand'] = isRand

# export dataset:

wd_to_save = "/Users/mariannemenictas/Box/MD2K Northwestern/Processed Data/primary_analysis/data/pickle_jar/missing_df.pkl"
missing_df.to_pickle(wd_to_save)
