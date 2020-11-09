import pandas as pd
from datetime import timedelta
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

# dir = "../temp/"
# files = os.listdir(dir)
# for file in files:
#     path = dir + file
#     print(path)
path = "../temp/*.csv"
ch_agg = []
sv_agg = []
for filename in glob.glob(path):
    report = import_report("../temp/" + filename)
    ch_agg.append(report[0])
    sv_agg.append(report[1])

print(pd.concat(ch_agg).shape), print(pd.concat(sv_agg).shape)

# plt.scatter(x=pd.concat(sv_agg).Longitude,
#             y=pd.concat(sv_agg).Latitude)
#
# plt.show()
#file = "2020-11-05.csv"
# path = dir + file
# ch = import_report(path)[0]
# sv = import_report(path)[1]
#
# ch_panamax = ch[ch['vessel class'] == 'Panamax']
# ch_post_panamax = ch[ch['vessel class'] == 'Post Panamax']
#
# sv_panamax = sv[sv['vessel class'] == 'Panamax']
# sv_post_panamax = sv[sv['vessel class'] == 'Post Panamax']
#
# # CHARLESTON COMPLIANCE RATES
# print('Panamax Transit Compliance: ' + str(round(sum(ch_panamax['SPEED'] <= 10) / ch_panamax.shape[0] * 100, 2)) + '%')
# print('Post Panamax Transit Compliance: ' + str(round(sum(ch_post_panamax['SPEED'] <= 10) / ch_post_panamax.shape[0] * 100, 2)) + '%')
# print('Total Transit Compliance: ' + str(round(sum(ch['SPEED'] <= 10) / ch.shape[0] * 100, 2)) + '%')
#
# # Savannah COMPLIANCE RATES
# print('Panamax Transit Compliance: ' + str(round(sum(sv_panamax['SPEED'] <= 10) / sv_panamax.shape[0] * 100, 2)) + '%')
# print('Post Panamax Transit Compliance: ' + str(round(sum(sv_post_panamax['SPEED'] <= 10) / sv_post_panamax.shape[0] * 100, 2)) + '%')
# print('Total Transit Compliance: ' + str(round(sum(sv['SPEED'] <= 10) / sv.shape[0] * 100, 2)) + '%')
