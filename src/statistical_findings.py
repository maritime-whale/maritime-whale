
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
ch = ch[ch.Longitude <= -79.7].reset_index()
sv = pd.concat(sv_agg)

ch['rounded date'] = [ch['Date/Time UTC'].iloc[i].floor('Min') for i in range(len(ch['Date/Time UTC']))]


def effective_beam(yaw, beam, loa):
    import math
    return (math.cos(math.radians(90-yaw))*loa) + (math.cos(math.radians(yaw))*beam)

effective_beam(10, 160, 1000)
effective_beam(10, 160, 1201)

compliant = ch[ch.SPEED <= 10]
non_compliant = ch[ch.SPEED > 10]

hover_dict = {'Date/Time UTC':True, 'MMSI':True, 'SPEED':True, 'course behavior':False,
                'WDIR degT':True, 'WSPD mph':True, 'GST mph':True,'Yaw':True, 'LOA ft':True,
                'Beam ft':True, 'effective beam ft':True}
##################FOCUS ON CHARELSTON ONLY FOR NOW###############################
ch_panamax = ch[ch['vessel class'] == 'Panamax']
ch_post_panamax = ch[ch['vessel class'] == 'Post Panamax']

# Note: Nearshore/offshore speed deltas is more important than Inbound/outbound speed deltas (not important).
# Note: no need to split stats up into Panamax and Post-Panamax (not really important).
# Note: high ship speed and low/moderate wind speed is important, and should be emphasized.
px.strip(ch, x='Name', y='SPEED', hover_data=hover_dict)
# line plot for every ship in the channel... speed vs time
for ship in ch.MMSI.unique():
    trace = go.Scatter()
    plt = px.line(ch[ch.MMSI == ship], x='Date/Time UTC', y='SPEED', color="course behavior", hover_name="Name", hover_data=hover_dict)
    plt.show()


# COMPLIANT
px.scatter(compliant, x='SPEED', y='GST mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)
# px.scatter(compliant, y='effective beam ft', x='GST mph', size='Yaw', color='SPEED', hover_data=hover_dict)
comp_corr_mat = compliant.dropna()[['SPEED', 'WSPD mph', 'GST mph', 'Yaw', 'effective beam ft']]
comp_correlation = comp_corr_mat.corr()
px.imshow(comp_correlation)

# NON_COMPLIANT
px.scatter(non_compliant, x='SPEED', y='GST mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)
# px.scatter(non_compliant, y='effective beam ft', x='GST mph', size='Yaw', color='SPEED', hover_data=hover_dict)
non_comp_corr_mat = non_compliant.dropna()[['SPEED', 'WSPD mph', 'GST mph', 'Yaw', 'effective beam ft']]
non_comp_correlation = non_comp_corr_mat.corr()
px.imshow(non_comp_correlation)




ch.shape
ch[ch.isnull().any(axis=1)].shape
ch.columns

dat = ch.sort_values('Date/Time UTC').reset_index().dropna()
dat['SPEED mph'] = dat['SPEED'] * 1.151
dat['WDIR degT'] = dat['WDIR degT'].astype(int)
dat['Date/Time UTC'].plot()
########################################################################
trace1 = go.Scatter(x=dat.index, y=dat['WSPD mph'], mode='lines', name='WSPD mph')
trace2 = go.Scatter(x=dat.index, y=dat['SPEED mph'], mode='lines', name='VSPD mph')
trace3 = go.Scatter(x=dat.index, y=dat['GST mph'], mode='lines', name='GST mph')
trace4 = go.Scatter(x=dat.index, y=dat['Yaw'], mode='lines', name='Yaw')
data = [trace1, trace2, trace3, trace4]
fig = go.Figure(data=data)#, layout=layout)
fig.show()
#######################################################

###### YAW ANALAYSIS
# ch.groupby(['Name', 'MMSI', 'vessel class', 'effective beam m'])[['SPEED', 'Yaw', 'WSPD mph', 'GST mph']].count()

# ch.groupby(['Name', 'MMSI', 'vessel class', 'Beam m'])[['Yaw', 'effective beam m']].max()

ch.shape
compliant.shape
non_compliant.shape
ch[ch.SPEED <= 10][['Yaw', 'SPEED', 'GST mph']].reset_index().drop('index', axis=1).plot(figsize=(15,6))
ch[ch.SPEED > 10][['Yaw', 'SPEED', 'GST mph']].reset_index().drop('index', axis=1).plot(figsize=(15,6))
ch[ch.Yaw >= 10].sort_values('Date/Time UTC').drop(64).drop(['LOA ft', 'Beam ft', 'effective beam ft'], axis=1)
high_yaw = ch[ch.MMSI.isin(ch[ch.Yaw >= 10].MMSI.unique())]
ch[ch.Yaw >= 9]
for ship in ch[ch.Yaw >= 10].MMSI.unique():
    t1 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['SPEED'], mode='markers', name='VSPD kn')
    t2 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['Yaw'], mode='markers', name='Yaw')
    t3 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['GST mph'], mode='markers', name='Gust mph')
    t4 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['WSPD mph'], mode='markers', name='WSPD mph')
    fig = go.Figure(data=[t1, t2, t3, t4])#, layout=layout)
    fig.show()
    # plt = px.line(ch[ch.MMSI == ship], x='Date/Time UTC', y='SPEED', color="course behavior", hover_name="Name", hover_data=hover_dict)
    # plt.show()

px.scatter(ch[ch.MMSI == 338241000], x='Longitude', y='Latitude', size='Yaw', color='course behavior', hover_data=hover_dict)



inbound = ch[ch['course behavior'] == 'Inbound']
outbound = ch[ch['course behavior'] == 'Outbound']
for ship in inbound.MMSI.unique():
    plt = px.scatter(inbound[inbound.MMSI == ship],
                x = 'Longitude',
                y = 'Latitude',
                hover_data=hover_dict,
                size='Yaw',
                range_color=[inbound.Yaw.min(),inbound.Yaw.max()])
    plt.show()

for ship in outbound.MMSI.unique():
    plt = px.scatter(outbound[outbound.MMSI == ship],
                x = 'Longitude',
                y = 'Latitude',
                hover_data=hover_dict,
                size='Yaw',
                range_color=[outbound.Yaw.min(),outbound.Yaw.max()])
    plt.show()


ch_compliant = ch[ch.SPEED <= 10]
ch_compliant['Yaw'] = abs(ch_compliant.COURSE - ch_compliant.HEADING)
ch_compliant.sort_values('Yaw').reset_index().Yaw.plot()
ch_compliant.Yaw.value_counts().plot(kind='barh')



ch_compliant[['Yaw', 'SPEED']].reset_index().drop('index', axis=1).plot(figsize=(15,6))

ch_compliant[['SPEED', 'Yaw']].corr()



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


###### meeting/passing
ch_meetpass = meetpass(ch)
for item in ch_meetpass.items():
    print(item)

mmsi = []
times = []
for i in range(len(ch_meetpass)):
    mmsi.append(list(ch_meetpass)[i][0])
    mmsi.append(list(ch_meetpass)[i][1])
    times.append(list(ch_meetpass.values())[i][0])
#
# for i in range(len(ch_meetpass)):
#     mp = pc.concat([ch[(ch.MMSI == mmsi[i]) & (ch['rounded date'] == times[0])]])

two_way = pd.concat([ch[(ch.MMSI == mmsi[0]) & (ch['rounded date'] == times[0])],
           ch[(ch.MMSI == mmsi[1]) & (ch['rounded date'] == times[0])],
           ch[(ch.MMSI == mmsi[2]) & (ch['rounded date'] == times[1])],
           ch[(ch.MMSI == mmsi[3]) & (ch['rounded date'] == times[1])],
           ch[(ch.MMSI == mmsi[4]) & (ch['rounded date'] == times[2])],
           ch[(ch.MMSI == mmsi[5]) & (ch['rounded date'] == times[2])]#,
           # ch[(ch.MMSI == mmsi[6]) & (ch['rounded date'] == times[3])],
           # ch[(ch.MMSI == mmsi[7]) & (ch['rounded date'] == times[3])],
           # ch[(ch.MMSI == mmsi[8]) & (ch['rounded date'] == times[4])],
           # ch[(ch.MMSI == mmsi[9]) & (ch['rounded date'] == times[4])],
           # ch[(ch.MMSI == mmsi[10]) & (ch['rounded date'] == times[5])],
           # ch[(ch.MMSI == mmsi[11]) & (ch['rounded date'] == times[5])]
           ])

ch.shape
two_way.shape
print(str(round((two_way.shape[0] / ch.shape[0])*100, 2)) + '%')
len(ch.MMSI.unique())

one_way = ch[~ch.index.isin(two_way.index)]
one_way.shape

px.scatter(one_way, x='SPEED', y='GST mph', size='Yaw', hover_data=hover_dict)
px.scatter(one_way, x='SPEED', y='WSPD mph', size='Yaw', hover_data=hover_dict)
px.scatter(ch[ch.MMSI == 255805914], x='Longitude', y='Latitude', size='Yaw', color='course behavior', hover_data=hover_dict)
ch[(ch.MMSI == 255805914) & (ch['Date/Time UTC'] == '2020-11-14 06:55:39')]


one_way[one_way.Yaw == 11]



px.scatter(two_way, x='SPEED', y='GST mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)




# for some reason the dates are out of order, i suspect might contribute to long
# and inefficient run times... look into this and fix ?
# count number of post-panamax meetpass instances along with total number of instances
# calculate percentage of transits that are meeting and passing
# graph....

mp = ch[(ch['MMSI'] == 255805942) | (ch['MMSI'] == 440176000) &
   (ch['Date/Time UTC'] >= '2020-11-18 14:40:00') &
   (ch['Date/Time UTC'] <= '2020-11-18 15:30:00')]
# mp_plot = px.line(mp, x='Date/Time UTC', y='SPEED', color='course behavior', hover_data=hover_dict)
# mp_plot.update_layout(hoverlabel=dict(bgcolor="White", font_size=13, font_family="sans-serif"))
# px.line(mp, x='Date/Time UTC', y='Yaw', color="course behavior", hover_name="Name")
# px.line(mp, x='Date/Time UTC', y='GST mph', color="course behavior", hover_name="Name")
