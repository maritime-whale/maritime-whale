import pandas as pd
from datetime import *
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import scipy
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob


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

path = "../tests/2020-11-13.csv"
ch = import_report(path)[0]
sv = import_report(path)[1]

year = ch['Date/Time UTC'].iloc[0].strftime('%Y')
month = ch['Date/Time UTC'].iloc[0].strftime('%m')
day = ch['Date/Time UTC'].iloc[0].strftime('%d')
print(year, month, day)

# offshore: 41004 (ch), 41008 (sv)
# nearshore: 41029 (ch), 41033 (sv)

# Add if statement in ./run that checks whether there is available windspeeds data
# before downloading and attempting all the windspeed coersion, matching, and analysis
# the script should be able to default to how it's working now in the case the NOAA site is down...
# Some rows having missing values 'MM' which can potentially throw off the whole script if
# the dependencies arent structured correctly. not sure what MM means but removing them for now..
ch_off_wind = pd.read_csv("../tests/41004.txt", delim_whitespace=True).drop(0)
ch_near_wind = pd.read_csv("../tests/41029.txt", delim_whitespace=True).drop(0)
sv_off_wind = pd.read_csv("../tests/41008.cwind", delim_whitespace=True).drop(0)
sv_near_wind = pd.read_csv("../tests/41033.txt", delim_whitespace=True).drop(0)

wind_dat = []
for df in [ch_off_wind, ch_near_wind, sv_off_wind, sv_near_wind]:
    df = df[(df['#YY'] == year) & (df['MM'] == month) & (df['DD'] == day)]
    df['Date/Time UTC'] = pd.to_datetime(df['#YY']+df['MM']+df['DD']+df['hh']+df['mm'],
                                         infer_datetime_format=True)
    df.rename({'WDIR':'WDIR degT', 'WSPD':'WSPD m/s', 'GST':'GST m/s'}, axis=1, inplace=True)
    df = df[(df['WDIR degT'] != 'MM') &
                (df['WSPD m/s'] != 'MM') &
                (df['GST m/s'] != 'MM')]
    df['WSPD mph'] = df['WSPD m/s'].astype('float') * 2.237
    df['GST mph'] = df['GST m/s'].astype('float') * 2.237
    df['WSPD mph'] = df['WSPD mph'].round(2)
    df['GST mph'] = df['GST mph'].round(2)
    wind_dat.append(df[['Date/Time UTC', 'WDIR degT', 'WSPD mph', 'GST mph']])

ch_off_wind = wind_dat[0]
ch_near_wind = wind_dat[1]
sv_off_wind = wind_dat[2]
sv_near_wind = wind_dat[3]

# round the datetime stamp for easier matching to windspeed data
# could add this to the main import_report above to make things cleaner..
# ch_rounded_times = ch.copy()
# sv_rounded_times = sv.copy()
# ch['Date/Time UTC'] = ch["Date/Time UTC"].values.astype('<M8[m]')
# sv['Date/Time UTC'] = sv["Date/Time UTC"].values.astype('<M8[m]')

# windspeeds will be matched to these four dataframes based on location..
ch_off = ch[ch['location'] == 'offshore']
ch_near = ch[ch['location'] == 'nearshore']
sv_off = sv[sv['location'] == 'offshore']
sv_near = sv[sv['location'] == 'nearshore']


# now need to write script to match the date/time columns between the wind and ships
# if there are no exact matches, then should round and grab the closest data..?

# you can see the times are reverse chronological order in the wind data
ch_off_wind['Date/Time UTC'].plot()
ch_off['Date/Time UTC'].plot()
ch_near['Date/Time UTC'].plot()
sv_off['Date/Time UTC'].plot()
sv_near['Date/Time UTC'].plot()
