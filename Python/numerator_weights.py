
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

day_start = pd.read_pickle(pickle_jar + "day_start_df.pkl")
day_end = pd.read_pickle(pickle_jar + "day_end_df.pkl")

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
        available_dec_ponts = id_log_EMI_day[(
            int_triggered_condition) | (int_not_triggered_condition)]
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
            hours_in_day_val = round(time_diff.seconds/3600, 0)
            if hours_in_day_val > 12: 
                print(hours_in_day_val, "hours from ", start_time_val, " to ", end_time_val)
            hours_in_day[idVal].append(hours_in_day_val)
        else:
            hours_in_day[idVal].append(np.nan)
        day = day + timedelta(days=1)

# find max hours in each user/day:

hours_in_day_per_id = []
for idVal in participants_for_analysis:
    hours_in_day_per_id.append(np.nanmax(hours_in_day[idVal]))

# numerator weights: 
num_weight_stress_num = {}
num_weight_stress_denom = {}
num_weight_no_stress_num = {}
num_weight_no_stress_denom = {}
for id in participants_for_analysis:
    print("id: ", id)
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    day = mrt_id_start_day
    num_weight_stress_num[id] = 0
    num_weight_stress_denom[id] = 0
    num_weight_no_stress_num[id] = 0
    num_weight_no_stress_denom[id] = 0
    while day <= mrt_id_tenth_day:
        print("day: ", day)
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day] 
        available_condition = id_log_EMI_day['message'] == 'true: all conditions okay'
        unavailable_condition = id_log_EMI_day['message'] == 'false: some conditions are failed'
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_points = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        stress_avai_dec_points = available_dec_points[available_dec_points['isStress'] == True]
        no_stress_avai_dec_points = available_dec_points[available_dec_points['isStress'] == False]
        if stress_avai_dec_points.shape[0] > 0:
            num_weight_stress_num[id] += round(np.sum(list(stress_avai_dec_points.probability)),2)
            num_weight_stress_denom[id] += stress_avai_dec_points.shape[0]
        if no_stress_avai_dec_points.shape[0] > 0:
            num_weight_no_stress_num[id] += round(np.sum(list(no_stress_avai_dec_points.probability)),2)
            num_weight_no_stress_denom[id] += no_stress_avai_dec_points.shape[0]
        day = day + timedelta(days=1)

# find numerator weights: 
numerator_stress_weight = round(np.nanmean(list(num_weight_stress_num.values()))/np.nanmean(list(num_weight_stress_denom.values())),2)
numerator_not_stress_weight = round(np.nanmean(list(num_weight_no_stress_num.values()))/np.nanmean(list(num_weight_no_stress_denom.values())),2)

weight_vals = {}
weight_trunc_vals = {}
dec_points_count = {}
trig_post_rand = {}
rands_within_119_mins = {}
rands_within_119_mins_no_ints = {}
rands_within_119_mins_no_ints_stressed = {}
count_a = 0
for id in participants_for_analysis:
    print("id: ", id)
    key_name = 'phone_log_' + str(id)
    mrt_id_start_day = mrt_start_day[id]
    mrt_id_tenth_day = mrt_id_start_day + timedelta(days=9)
    id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
    day = mrt_id_start_day
    weight_vals[id] = []
    weight_trunc_vals[id] = []
    dec_points_count[id] = []
    trig_post_rand[id] = []
    rands_within_119_mins[id] = []
    rands_within_119_mins_no_ints[id] = []
    rands_within_119_mins_no_ints_stressed[id] = []
    while day <= mrt_id_tenth_day:
        print("day: ", day)
        id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day] 
        int_triggered_condition = id_log_EMI_day['isTriggered'] == True
        int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
        available_dec_points = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
        dec_points_count[id].append(available_dec_points.shape[0])
        for id1, row1 in available_dec_points.iterrows(): 
            At_val = int(row1.isTriggered)
            if row1.isStress: 
                first_term = (numerator_stress_weight/row1.probability)**At_val
                second_term = ((1-numerator_stress_weight)/((1-row1.probability)))**(1-At_val)
                fourth_term = 1/(numerator_stress_weight*(1 - numerator_stress_weight))
            else:
                first_term = (numerator_not_stress_weight/row1.probability)**At_val
                second_term = ((1-numerator_not_stress_weight)/((1-row1.probability)))**(1-At_val)
                fourth_term = 1/(numerator_not_stress_weight*(1 - numerator_not_stress_weight))
            # check if there are any randomizations within the following 119 minutes 
            # after the randomization minute: 
            rand_plus_119_mins = row1.date_time + timedelta(minutes = 119)
            rands_in_2_hours = available_dec_points[(available_dec_points['date_time']<=rand_plus_119_mins)&(available_dec_points['date_time']>row1.date_time)]
            third_term = 1
            trig_post_rand_count = 0
            rand_post_rand_count = rands_in_2_hours.shape[0]
            rands_within_119_mins_no_ints_val = 0
            rands_within_119_mins_no_ints_stressed_val = 0
            if rands_in_2_hours.shape[0] > 0: 
                if (np.sum(rands_in_2_hours.isTriggered) == 0):
                    rands_within_119_mins_no_ints_val = rands_in_2_hours.shape[0]
                    rands_within_119_mins_no_ints_stressed_val = np.sum(rands_in_2_hours.isStress)
                for id2, row2 in rands_in_2_hours.iterrows(): 
                    if row2.isTriggered: 
                        trig_post_rand_count += 1
                    third_term = third_term * ((1 - int(row2.isTriggered))/(1 - row2.probability))
            rands_within_119_mins_no_ints[id].append(rands_within_119_mins_no_ints_val)
            rands_within_119_mins_no_ints_stressed[id].append(rands_within_119_mins_no_ints_stressed_val)
            trig_post_rand[id].append(trig_post_rand_count)
            if trig_post_rand_count == 2: 
                print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("      decision time: ", row1.date_time)
                print("      decision time triggered?", row1.isTriggered)
                print("      times of other rands in following 2 hours: ", list(rands_in_2_hours.date_time))
                print("      isTriggered of other rands in following 2 hours: ", list(rands_in_2_hours.isTriggered))
                print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                if not row1.isTriggered: 
                    count_a += 1
            weight_val = first_term * second_term * third_term * fourth_term
            weight_trunc_val = first_term * second_term * third_term 
            weight_vals[id].append(round(weight_val,2))
            weight_trunc_vals[id].append(round(weight_trunc_val,2))
            if weight_val > 200: 
                print("id: ", id, ", day: ", day, "avai_dec_time: ", row1.date_time)
            # Track number of randomizations within the following 119 minutes: 
            rands_within_119_mins[id].append(rands_in_2_hours.shape[0])
        day = day + timedelta(days=1)

# weights above 200: 
id:  223 , day:  2018-01-10 avai_dec_time:  2018-01-10 12:55:02.656000-06:00
id:  269 , day:  2019-07-08 avai_dec_time:  2019-07-08 13:15:02.106000-05:00

id = 269
key_name = 'phone_log_' + str(id)
mrt_id_start_day = mrt_start_day[id]
id_log_EMI = logs[key_name][logs[key_name]['id'] == 'EMI']
day = mrt_id_start_day
day = day + timedelta(days=7)
id_log_EMI_day = id_log_EMI[id_log_EMI['date'] == day] 
int_triggered_condition = id_log_EMI_day['isTriggered'] == True
int_not_triggered_condition = id_log_EMI_day['isTriggered'] == False
available_dec_points = id_log_EMI_day[(int_triggered_condition) | (int_not_triggered_condition)]
row1 = available_dec_points.iloc[4]
At_val = int(row1.isTriggered)
first_term = (numerator_not_stress_weight/row1.probability)**At_val
second_term = ((1-numerator_not_stress_weight)/((1-row1.probability)))**(1-At_val)
fourth_term = 1/(numerator_not_stress_weight*(1 - numerator_not_stress_weight))
# check if there are any randomizations for this individual within the following 119 minutes 
# after the randomization minute: 
rand_plus_119_mins = row1.date_time + timedelta(minutes = 119)
rands_in_2_hours = available_dec_points[(available_dec_points['date_time']<=rand_plus_119_mins)&(available_dec_points['date_time']>row1.date_time)]
third_term = 1 
trig_post_rand_count = 0 
for id2, row2 in rands_in_2_hours.iterrows(): 
    if row2.isTriggered: 
        trig_post_rand_count += 1
    print("A_t: ", int(row2.isTriggered))
    print("p_t(H_t): ", row2.probability)
    third_term = third_term * ((1 - int(row2.isTriggered))/(1 - row2.probability))
    print("third_term: ", third_term)
weight_val = first_term * second_term * third_term * fourth_term

# create a list of all these weights: 
weights = []
for id in participants_for_analysis: 
    for value in weight_vals[id]:
        weights.append(value)

rands_within_119_mins_no_ints_list = []
for id in participants_for_analysis: 
    for value in rands_within_119_mins_no_ints[id]:
        rands_within_119_mins_no_ints_list.append(value)

rands_within_119_mins_no_ints_str_list = []
for id in participants_for_analysis: 
    for value in rands_within_119_mins_no_ints_stressed[id]:
        rands_within_119_mins_no_ints_str_list.append(value)

weights_trunc = []
for id in participants_for_analysis: 
    for value in weight_trunc_vals[id]:
        weights_trunc.append(value)

np.min(weights) # 0 
np.quantile(weights, 0.25) # 0
np.median(weights) # 11.74
np.quantile(weights, 0.75) # 16
np.max(weights) # 373.71

np.min(weights_trunc) # 0 
np.quantile(weights_trunc, 0.25) # 0
np.median(weights_trunc) # 0.98
np.quantile(weights_trunc, 0.75) # 1.33
np.max(weights_trunc) # 30.61

# create histogram of weights: 
import matplotlib.pyplot as plt

plt.figure()
plt.hist(weights, bins=20)
plt.savefig(save_dir + 'weights.png')

plt.figure()
plt.hist(weights_trunc, bins=20)
plt.savefig(save_dir + 'weights_trunc.png')

# create two histograms: 
# One  histogram  for  weights  above  3rd  quartile  
# and  the  second  his-togram for weights below 3rd quartile.

third_quartile = np.quantile(weights, 0.75)
g_third_quartile = [x for x in weights if x > third_quartile]
leq_third_quartile = [x for x in weights if x <= third_quartile]

save_dir = "/Users/mariannemenictas/Dropbox/Postdoc_Harvard/S2S_primary_analysis/github_repository/S2S_primary_analysis/img/"

plt.figure()
plt.hist(g_third_quartile, bins=20)
plt.savefig(save_dir + 'hist_g_third_quart.png')

plt.figure()
plt.hist(leq_third_quartile, bins=20)
plt.savefig(save_dir + 'hist_leq_third_quart.png')

plt.figure()
leq_third_quartile_ne_zero = [x for x in leq_third_quartile if x != 0]
plt.hist(leq_third_quartile_ne_zero, bins=20)
plt.savefig(save_dir + 'hist_leq_third_quart_neq_zero.png')

from collections import Counter, OrderedDict

weight_counts = Counter(weights)
most_common_weights_sorted = OrderedDict(weight_counts.most_common())
list(weight_counts.keys())


# Summary of triggered post randomization: 
# count the 0's, 1's and 2's that exist per individual: 
total_dec_points = {}
count_trig_post_rand_0 = {}
count_trig_post_rand_1 = {}
count_trig_post_rand_2 = {}
for id in participants_for_analysis: 
    total_dec_points[id] = len(trig_post_rand[id])
    count_trig_post_rand_0[id] = trig_post_rand[id].count(0)
    count_trig_post_rand_1[id] = trig_post_rand[id].count(1)
    count_trig_post_rand_2[id] = trig_post_rand[id].count(2)

trig_post_rand_list = []
for id in participants_for_analysis: 
    for value in trig_post_rand[id]:
        trig_post_rand_list.append(value)
