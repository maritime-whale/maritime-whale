from import_vessel_data import *
from datetime import timedelta
from util import *

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import scipy
#import seaborn as sns
#import matplotlib.pyplot as plt

# # use '2020-10-06.csv' path for testing
# path = "../tests/2020-10-06.csv"
# out = import_report(path, STATS)
# ch = out[0]
# sv = out[1]
#
# print(meetpass(ch))

def meetpass_helper(df, time_tolerance):
    """    df: cleaned VMR from import_report
    This function takes in a cleaned up entry channel dataframe plus desired time_tolerance (int),
       and returns potential meeting/passing positions from the entry channel"""
    #sorts the time stamp such that entry channel data is in chronological order
    times = df.sort_values("Date/Time UTC")

    mmsi = list(times.MMSI)
    timestamp = list(times["Date/Time UTC"])
    course = list(times["course behavior"])

    potential_times = []

    for i in range(len(mmsi) - 1):
            if mmsi[i] != mmsi[i + 1]:
                if (timestamp[i + 1] - timestamp[i]) <= timedelta(minutes=time_tolerance):
                    if course[i] != course[i + 1]:
                        potential_times.append(timestamp[i])
                        potential_times.append(timestamp[i + 1])
                        sorted(potential_times)

    res = times[times["Date/Time UTC"].isin(potential_times)]
    return res

def calc_naut_dist(lat1, long1, lat2, long2):
    return ((lat1 - lat2)**2 + (long1 - long2)**2)**0.5

def meetpass(df):
    """
    df: cleaned VMR from import_report
    """
    rounded_df = df.copy()
    rounded_df['Date/Time UTC'] = df["Date/Time UTC"].values.astype('<M8[m]')
    flagged = meetpass_helper(df, MEET_PASS_TIME_TOL).groupby(
            ['MMSI', 'course behavior', pd.Grouper(
                key='Date/Time UTC', freq='min')])[['Date/Time UTC']].size()

    # sub should contain all the flagged times
    sub = {}
    for level in flagged.index.unique(0):
        sub[level] = flagged.xs(level, level=0).index
    sub.items()

    true_encs = {}
    min_dist = 0.1
    # FUTURE OPTIMIZATION: minimize comparison operations between timestamps
    while len(sub):
        item = sub.popitem()
        cur_key = item[0]
        cur_val = item[1]
        i = 0
        while not cur_val.empty:
            this_course = cur_val.get_level_values(0)[0]
            this_time = cur_val.get_level_values(1)[0]
            this_lat = rounded_df[(rounded_df.MMSI == cur_key) & (rounded_df['Date/Time UTC'] == this_time)].Latitude.values[0].round(5)
            this_long = rounded_df[(rounded_df.MMSI == cur_key) & (rounded_df['Date/Time UTC'] == this_time)].Longitude.values[0].round(5)
            for inner_key, inner_val in sub.items():
                for j, that in enumerate(inner_val):
                    that_course = that[0]
                    that_time = that[1]
                    that_lat = rounded_df[(rounded_df.MMSI == inner_key) & (rounded_df['Date/Time UTC'] == that_time)].Latitude.values[0].round(5)
                    that_long = rounded_df[(rounded_df.MMSI == inner_key) & (rounded_df['Date/Time UTC'] == that_time)].Longitude.values[0].round(5)
                    if (this_time == that_time) and (this_course != that_course):
                        dist = calc_naut_dist(this_lat, this_long, that_lat, that_long)
                        # check if true encounter (within minimum distance)
                        if min_dist >= dist:
                            key = tuple(sorted([cur_key, inner_key]))
                            if key not in true_encs:
                                # create new entry
                                true_encs[key] = (this_time, dist)
                            else:
                                # minimize distance (update)
                                if true_encs[key][1] > dist:
                                    true_encs[key] = (this_time, dist)
            multiindex = cur_val.delete(0)
            cur_val = multiindex
            i += 1
    return true_encs

# use '2020-10-06.csv' path for testing
path = "../tests/2020-10-06.csv"
out = import_report(path, STATS)
ch = out[0]
sv = out[1]

print(meetpass(ch))
print(len(meetpass(ch)))


ch[ch.isnull().any(axis=1)]
