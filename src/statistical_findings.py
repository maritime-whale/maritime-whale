import pandas as pd
from datetime import timedelta
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import scipy
import seaborn as sns
import matplotlib.pyplot as plt

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

    df = df[(df.COURSE >= 115) &
                          (df.COURSE <= 125) |
                          (df.COURSE >= 295) &
                          (df.COURSE <= 305)]
    df.COURSE = round(df.COURSE).astype("int")
    df['course behavior'] = df.COURSE
    courses = {}
    for i in range (115, 126):
        courses[i] = "Outbound"
    for i in range (295, 306):
        courses[i] = "Inbound"
    df['course behavior'] = df['course behavior'].replace(courses).astype("str")
    new_blacklisters = []
    for i in range(df.shape[0]):
        if df.iloc[i]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36,
                                             37, 51, 52, 53, 55, 57, 58, 59]:
            new_blacklisters.append(df.iloc[i].MMSI)


    df = df[~df.MMSI.isin(new_blacklisters)]
    df = df[["Name", "MMSI", "Date/Time UTC", "SPEED",
                           "LOA m", "LOA ft", "Latitude", "Longitude", "COURSE", "course behavior",
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
    #sv = df[df.Latitude < 32.033]
    # Missing near and offshore in Savannah because Jon only wants charleston for now...
    ch_nearshore_index = ch[ch['Longitude'] <= -79.74169].index
    ch_offshore_index = ch[ch['Longitude'] > -79.74169].index
    ch_nearshore = pd.Series(['nearshore' for i in range(len(ch_nearshore_index))],
                        index = ch_nearshore_index)
    ch_offshore = pd.Series(['offshore' for i in range(len(ch_offshore_index))],
                        index = ch_offshore_index)
    ch_location = pd.concat([ch_offshore, ch_nearshore]).sort_index(axis=0).to_frame().rename(
                                                                                    {0:'location'}, axis=1)
    ch['location'] = ch_location

    return ch


panamax = ch[ch['vessel class'] == 'Panamax']
post_panamax = ch[ch['vessel class'] == 'Post Panamax']

# COMPLIANCE RATES
print('Panamax Transit Compliance: ' + str(round(sum(panamax['SPEED'] <= 10) / panamax.shape[0] * 100, 2)) + '%')
print('Post Panamax Transit Compliance: ' + str(round(sum(post_panamax['SPEED'] <= 10) / post_panamax.shape[0] * 100, 2)) + '%')
print('Total Transit Compliance: ' + str(round(sum(ch['SPEED'] <= 10) / ch.shape[0] * 100, 2)) + '%')
