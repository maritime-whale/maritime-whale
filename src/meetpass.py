import pandas as pd
from datetime import timedelta
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import scipy
#import seaborn as sns
#import matplotlib.pyplot as plt

def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    df = pd.read_csv(path)
    df.rename({"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
               "LATITUDE": "Latitude", "LONGITUDE": "Longitude"}, axis=1,
               inplace=True)
    df["LOA m"] = df["A"] + df["B"]
    df["LOA ft"] = df["LOA m"] * 3.28
    df["LOA ft"] = df["LOA ft"].round(0)
    df["Latitude"] = df["Latitude"].round(5)
    df["Longitude"] = df["Longitude"].round(5)
    df = df[df["LOA m"] >= 200]
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    new_blacklisters = []
    for i in range(df.shape[0]):
        if df.iloc[i]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36,
                                             37, 51, 52, 53, 55, 57, 58, 59]:
            new_blacklisters.append(df.iloc[i].MMSI)


    df = df[~df.MMSI.isin(new_blacklisters)]
    df = df[["Name", "MMSI", "Date/Time UTC", "SPEED",
                           "LOA m", "LOA ft", "Latitude", "Longitude", "COURSE",
             "AIS TYPE", 'HEADING']]

    panamax_index = df[df['LOA ft'] <= 965].index
    post_panamax_index = df[df['LOA ft'] > 965].index
    panamax = pd.Series(['Panamax' for i in range(len(panamax_index))],
                        index = panamax_index)
    post_panamax = pd.Series(['Post Panamax' for i in range(len(post_panamax_index))],
                        index = post_panamax_index)
    vessel_class = pd.concat([panamax, post_panamax]).sort_index(axis=0).to_frame().rename(
                                                                                    {0:'vessel class'}, axis=1)
    df['vessel class'] = vessel_class

    ch = df[df.Latitude >= 32.033]
    ch_nearshore_index = ch[ch['Longitude'] <= -79.74169].index
    ch_offshore_index = ch[ch['Longitude'] > -79.74169].index
    ch_nearshore = pd.Series(['nearshore' for i in range(len(ch_nearshore_index))],
                        index = ch_nearshore_index)
    ch_offshore = pd.Series(['offshore' for i in range(len(ch_offshore_index))],
                        index = ch_offshore_index)
    ch_location = pd.concat([ch_offshore, ch_nearshore]).sort_index(axis=0).to_frame().rename(
                                                                                    {0:'location'}, axis=1)
    ch['location'] = ch_location

    ch = ch[(ch.COURSE >= 100) &
              (ch.COURSE <= 140) |
              (ch.COURSE >= 280) &
              (ch.COURSE <= 320)]
    ch.COURSE = round(ch.COURSE).astype("int")
    ch['course behavior'] = ch.COURSE
    courses = {}
    for i in range (100, 141):
        courses[i] = "Outbound"
    for i in range (280, 321):
        courses[i] = "Inbound"
    ch['course behavior'] = ch['course behavior'].replace(courses).astype("str")

    sv = df[df.Latitude < 32.033]
    sv_nearshore_index = sv[sv['Longitude'] <= -80.78522].index
    sv_offshore_index = sv[sv['Longitude'] > -80.78522].index
    sv_nearshore = pd.Series(['nearshore' for i in range(len(sv_nearshore_index))],
                        index = sv_nearshore_index)
    sv_offshore = pd.Series(['offshore' for i in range(len(sv_offshore_index))],
                        index = sv_offshore_index)
    sv_location = pd.concat([sv_offshore, sv_nearshore]).sort_index(axis=0).to_frame().rename(
                                                                                    {0:'location'}, axis=1)
    sv['location'] = sv_location

    sv = sv[(sv.COURSE >= 100) &
              (sv.COURSE <= 160) |
              (sv.COURSE >= 280) &
              (sv.COURSE <= 340)]
    sv.COURSE = round(sv.COURSE).astype("int")
    sv['course behavior'] = sv.COURSE
    courses = {}
    for i in range (100, 161):
        courses[i] = "Outbound"
    for i in range (280, 341):
        courses[i] = "Inbound"
    sv['course behavior'] = sv['course behavior'].replace(courses).astype("str")


    return ch, sv


def meetpass_helper(EC, time_interval):
    """This function takes in a cleaned up entry channel dataframe plus desired time_interval (int),
       and returns potential meeting/passing positions from the entry channel"""
    #sorts the time stamp such that entry channel data is in chronological order
    times = EC.sort_values("Date/Time UTC")

    mmsi = list(times.MMSI)
    timestamp = list(times["Date/Time UTC"])
    course = list(times["course behavior"])

    potential_times = []

    for i in range(len(mmsi) - 1):
            if mmsi[i] != mmsi[i + 1]:
                if (timestamp[i + 1] - timestamp[i]) <= timedelta(minutes=time_interval):
                    if course[i] != course[i + 1]:
                        potential_times.append(timestamp[i])
                        potential_times.append(timestamp[i + 1])
                        sorted(potential_times)

    df2 = times[times["Date/Time UTC"].isin(potential_times)]
    return df2

    def calc_dist(lat1, long1, lat2, long2):
        return ((lat1 - lat2)**2 + (long1 - long2)**2)**0.5

# use '2020-10-06.csv' path for testing
df = import_report("../tests/2020-10-06.csv")
rounded_df = df[0].copy()
rounded_df['Date/Time UTC'] = df[0]["Date/Time UTC"].values.astype('<M8[m]')
flagged = meetpass_helper(df[0], 1).groupby(
        ['MMSI', 'course behavior', pd.Grouper(
            key='Date/Time UTC', freq='min')])[['Date/Time UTC']].size()

# sub should contain all the flagged times
sub = {}
for level in flagged.index.unique(0):
    sub[level] = flagged.xs(level, level=0).index
sub.items()

pot_encs = []
# {key:(MMSI_i, MMSI_j) val:([timestamp_i, timestamp_j], distance)}
# WHERE MMSI_i < MMSI_j and where [Timestamps] is a list of between 1 or 2 (no more no less) Timestamps; MMSI_i -> Timestamp_i
true_encs = {}
tolerance = 2
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
                if (abs(that_time - this_time) <=
                    timedelta(minutes=tolerance)) and (that_course != this_course):
                    pot_enc = ((cur_key,cur_val.get_level_values(1)[0]),
                              (inner_key,inner_val.get_level_values(1)[j]))
                    # pot_encs.append(pot_enc)
                    # find distance (some func)
                    print(calc_dist(this_lat, this_long, that_lat, that_long))
                    #calc_dist(this_lat, this_long, that_lat, that_long)
                    #exit(0)

                    # CHECK if true encounter
                    # this means that the vessels must be within a certain minimum distance of one another
                    # if distance < 1:
                    # if it is a NEW true encounter, then add it to true_encs
                    # otherwise, encounter doesn't exist in our dictionary of encounter (true_encs)
                    # therefore we should see if we have just found a smaller distance than the current time/distance stored for that MMSI combo key/val pair
                    #
                    # data =
                    #true_encs.append(data)

        multiindex = cur_val.delete(0)
        cur_val = multiindex
        i += 1


# loop thru ALL potential encounters
# for each potential_encounter

#rounded_df
#flagged

#meetpass_helper(df[0], 1)
#pot_encs
