
from import_vessel_data import *
from datetime import timedelta
from meetpass import *
from util import *

import plotly.figure_factory as ff
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import pandas as pd
import numpy as np
import glob
import os

# running multiple days of data at once
path = "../tests/*.csv"
ch_agg = []
sv_agg = []
for filename in glob.glob(path):
    report = import_report("../tests/" + filename, STATS)
    ch_agg.append(report[0])
    sv_agg.append(report[1])

ch = pd.concat(ch_agg)
sv = pd.concat(sv_agg)

# line plot for every ship in the channel... speed vs time
for ship in ch.MMSI.unique():
    trace = go.Scatter()
    plt = px.line(ch[ch.MMSI == ship], x='Date/Time UTC', y='SPEED', color="course behavior", hover_name="Name")
    plt.show()

fig = plt.figure()
g = sns.swarmplot(x='MMSI', y='SPEED', data=ch, size=3, color='m')
g.set(xticklabels=[])
g.set_xlabel('Vessels')
g.set_ylabel('VSPD kn')
plt.figure(figsize=(30,15))
sns.set(font_scale=2.5)
sns.set_style("whitegrid")
plt.title("Array of Vessel Speeds")

# for some reason the dates are out of order, i suspect might contribute to long
# and inefficient run times... look into this and fix ?
# count number of post-panamax meetpass instances along with total number of instances
# calculate percentage of transits that are meeting and passing
# graph....
ch_meetpass = meetpass(ch)
ch_meetpass

for item in ch_meetpass.items():
    print(item)

mp = ch[(ch['MMSI'] == 255805942) | (ch['MMSI'] == 440176000) &
   (ch['Date/Time UTC'] >= '2020-11-18 14:40:00') &
   (ch['Date/Time UTC'] <= '2020-11-18 15:30:00')]
mp['WDIR degT'] = mp['WDIR degT'].astype(int)
mp.shape
mp.columns

hover_dict = {'Date/Time UTC':True, 'SPEED':True, 'course behavior':False,
                'WDIR degT':True, 'WSPD mph':True, 'GST mph':True,'Yaw':True,
                'Beam m':True, 'effective beam m':True}
round(mp.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)
round(mp.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2)
round(mp.dropna()[['SPEED', 'WDIR degT']].corr().iloc[0][1], 2)
round(mp.dropna()[['SPEED', 'Yaw']].corr().iloc[0][1], 2)


mp_plot = px.line(mp, x='Date/Time UTC', y='SPEED', color='course behavior', hover_data=hover_dict)
mp_plot.update_layout(hoverlabel=dict(bgcolor="White", font_size=13, font_family="sans-serif"))

px.line(mp, x='Date/Time UTC', y='Yaw', color="course behavior", hover_name="Name")
px.line(mp, x='Date/Time UTC', y='GST mph', color="course behavior", hover_name="Name")
px.line(mp, x='Date/Time UTC', y='WSPD mph', color="course behavior", hover_name="Name")



ch.shape
ch[ch.isnull().any(axis=1)].shape
ch.columns

dat = ch.sort_values('Date/Time UTC').reset_index().dropna()
dat['SPEED mph'] = dat['SPEED'] * 1.151
dat['WDIR degT'] = dat['WDIR degT'].astype(int)
sns.scatterplot(data = dat, y = 'SPEED', x = 'WSPD mph')
sns.scatterplot(data = dat, y = 'SPEED', x = 'GST mph')
sns.scatterplot(data = dat, y = 'SPEED', x = 'WDIR degT')

dat['Date/Time UTC'].plot()
########################################################################
trace1 = go.Scatter(x=dat.index, y=dat['WSPD mph'], mode='lines', name='WSPD mph')
trace2 = go.Scatter(x=dat.index, y=dat['SPEED mph'], mode='lines', name='VSPD mph')
trace3 = go.Scatter(x=dat.index, y=dat['GST mph'], mode='lines', name='GST mph')
data = [trace1, trace2, trace3]
fig = go.Figure(data=data)#, layout=layout)
fig.show()
#######################################################


corr_mat = dat[['SPEED mph', 'WSPD mph', 'GST mph', 'WDIR degT', 'COURSE', 'LOA m']]
corr_mat['WDIR degT'] = corr_mat['WDIR degT'].astype(int)
correlation = corr_mat.corr()
sns.heatmap(correlation, center=0.6)
plt.title('Correlation Heatmap')


round(ch.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)


# running one day of data at a time
# use '2020-10-06.csv' path for testing
# path = "../tests/2020-10-06.csv"
# out = import_report(path, STATS)
# ch = out[0]
# sv = out[1]


ch_panamax = ch[ch['vessel class'] == 'Panamax']
ch_post_panamax = ch[ch['vessel class'] == 'Post Panamax']

sv_panamax = sv[sv['vessel class'] == 'Panamax']
sv_post_panamax = sv[sv['vessel class'] == 'Post Panamax']

# Note: Nearshore/offshore speed deltas is more important than Inbound/outbound speed deltas (not important).
# Note: no need to split stats up into Panamax and Post-Panamax (not really important).
# Note: high ship speed and low/moderate wind speed is important, and should be emphasized.

###### YAW ANALAYSIS
ch[ch.SPEED < 15][['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))
ch[ch.SPEED >= 15][['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))




def effective_beam(yaw, beam, loa):
    import math
    return (math.cos(math.radians(90-yaw))*loa) + (math.cos(math.radians(yaw))*beam)

effective_beam(10, 40, 318)
effective_beam(10, 160, 1000)

ch_compliant = ch[ch.SPEED <= 10]
ch_compliant['Yaw'] = abs(ch_compliant.COURSE - ch_compliant.HEADING)
ch_compliant.sort_values('Yaw').reset_index().Yaw.plot()
ch_compliant.Yaw.value_counts().plot(kind='barh')


ch_compliant[['COURSE', 'HEADING', 'Yaw']].sort_values('COURSE').reset_index().drop('index', axis=1).plot(figsize=(15,6))

ch_compliant[ch_compliant.Yaw > 5][['COURSE', 'HEADING', 'Yaw']].sort_values('COURSE').reset_index().drop('index', axis=1).plot(figsize=(15,6))
ch_compliant[['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))

ch_compliant[ch_compliant.Yaw > 5][['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))
ch_compliant[['SPEED', 'Yaw']].corr()





sv_compliant = sv[sv.SPEED <= 10]
sv_compliant['Yaw'] = abs(sv_compliant.COURSE - sv_compliant.HEADING)
sv_compliant.Yaw.value_counts().plot(kind='barh')
sv_compliant[['COURSE', 'HEADING', 'Yaw']].sort_values('COURSE').reset_index().drop('index', axis=1).plot(figsize=(15,6))
sv_compliant[['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))
sv_compliant[['SPEED', 'Yaw']].corr()

# CHARLESTON
ch_dat = {'Proportion of Transits':[str(round(ch_panamax.shape[0]/ch.shape[0]*100, 2)) + '%',
                                    str(round(ch_post_panamax.shape[0]/ch.shape[0]*100, 2)) + '%',
                                    "100%"],

          'Compliance Rate':[str(round(sum(ch_panamax['SPEED'] <= 10) / ch_panamax.shape[0] * 100, 2)) + '%',
                             str(round(sum(ch_post_panamax['SPEED'] <= 10) / ch_post_panamax.shape[0] * 100, 2)) + '%',
                             str(round(sum(ch['SPEED'] <= 10) / ch.shape[0] * 100, 2)) + '%'],

          'Nearshore Median Speed':[str(round(ch_panamax[ch_panamax['location'] == 'nearshore']['SPEED'].median(),2)),
                                    str(round(ch_post_panamax[ch_post_panamax['location'] == 'nearshore']['SPEED'].median(),2)),
                                    str(round(ch[ch['location'] == 'nearshore']['SPEED'].median(),2))],

          'Offshore Median Speed':[str(round(ch_panamax[ch_panamax['location'] == 'offshore']['SPEED'].median(),2)),
                                   str(round(ch_post_panamax[ch_post_panamax['location'] == 'offshore']['SPEED'].median(),2)),
                                   str(round(ch[ch['location'] == 'offshore']['SPEED'].median(),2))],

          'Inbound Median Speed':[str(round(ch_panamax[ch_panamax['course behavior'] == 'Inbound']['SPEED'].median(),2)),
                                  str(round(ch_post_panamax[ch_post_panamax['course behavior'] == 'Inbound']['SPEED'].median(),2)),
                                  str(round(ch[ch['course behavior'] == 'Inbound']['SPEED'].median(),2))],

          'Outbound Median Speed':[str(round(ch_panamax[ch_panamax['course behavior'] == 'Outbound']['SPEED'].median(),2)),
                                   str(round(ch_post_panamax[ch_post_panamax['course behavior'] == 'Outbound']['SPEED'].median(),2)),
                                   str(round(ch[ch['course behavior'] == 'Outbound']['SPEED'].median(),2))],

          'VSPD-WSPD correlation':[str(round(ch_panamax.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)),
                                   str(round(ch_post_panamax.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)),
                                   str(round(ch.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2))],

          'VSPD-GST correlation':[str(round(ch_panamax.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2)),
                                   str(round(ch_post_panamax.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2)),
                                   str(round(ch.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2))]
         }

ch_index = ['Panamax', 'Post Panamax', 'Combined']

# SAVANNAH
sv_dat = {'Proportion of Transits':[str(round(sv_panamax.shape[0]/sv.shape[0]*100, 2)) + '%',
                                str(round(sv_post_panamax.shape[0]/sv.shape[0]*100, 2)) + '%',
                                "100%"],

          'Compliance Rate':[str(round(sum(sv_panamax['SPEED'] <= 10) / sv_panamax.shape[0] * 100, 2)) + '%',
                        str(round(sum(sv_post_panamax['SPEED'] <= 10) / sv_post_panamax.shape[0] * 100, 2)) + '%',
                        str(round(sum(sv['SPEED'] <= 10) / sv.shape[0] * 100, 2)) + '%'],

          'Nearshore Median Speed':[str(round(sv_panamax[sv_panamax['location'] == 'nearshore']['SPEED'].median(),2)),
                                    str(round(sv_post_panamax[sv_post_panamax['location'] == 'nearshore']['SPEED'].median(),2)),
                                    str(round(sv[sv['location'] == 'nearshore']['SPEED'].median(),2))],

          'Offshore Median Speed':[str(round(sv_panamax[sv_panamax['location'] == 'offshore']['SPEED'].median(),2)),
                                  str(round(sv_post_panamax[sv_post_panamax['location'] == 'offshore']['SPEED'].median(),2)),
                                  str(round(sv[sv['location'] == 'offshore']['SPEED'].median(),2))],

          'Inbound Median Speed':[str(round(sv_panamax[sv_panamax['course behavior'] == 'Inbound']['SPEED'].median(),2)),
                                    str(round(sv_post_panamax[sv_post_panamax['course behavior'] == 'Inbound']['SPEED'].median(),2)),
                                    str(round(sv[sv['course behavior'] == 'Inbound']['SPEED'].median(),2))],

          'Outbound Median Speed':[str(round(sv_panamax[sv_panamax['course behavior'] == 'Outbound']['SPEED'].median(),2)),
                        str(round(sv_post_panamax[sv_post_panamax['course behavior'] == 'Outbound']['SPEED'].median(),2)),
                        str(round(sv[sv['course behavior'] == 'Outbound']['SPEED'].median(),2))],

          'VSPD-WSPD correlation':[str(round(sv_panamax.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)),
                                 str(round(sv_post_panamax.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2)),
                                 str(round(sv.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1], 2))],

          'VSPD-GST correlation':[str(round(sv_panamax.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2)),
                                  str(round(sv_post_panamax.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2)),
                                  str(round(sv.dropna()[['SPEED', 'GST mph']].corr().iloc[0][1], 2))]
                                 }

sv_index = ['Panamax', 'Post Panamax', 'Combined']


pd.DataFrame(ch_dat, ch_index)
# pd.DataFrame(ch_dat, ch_index)

pd.DataFrame(sv_dat, sv_index)
# pd.DataFrame(sv_dat, sv_index)
