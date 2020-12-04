
from import_vessel_data import *
from datetime import timedelta
from meetpass import *
from util import *

import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
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
ch = ch[ch.Longitude < -79.692].reset_index()
sv = pd.concat(sv_agg)
sv = sv.reset_index()
# sv = sv[sv.Longitude < -80.76].reset_index()

ch['rounded date'] = [ch['Date/Time UTC'].iloc[i].floor('Min') for i in range(len(ch['Date/Time UTC']))]
sv['rounded date'] = [sv['Date/Time UTC'].iloc[i].floor('Min') for i in range(len(sv['Date/Time UTC']))]

def effective_beam(yaw, beam, loa):
    import math
    return (math.cos(math.radians(90-yaw))*loa) + (math.cos(math.radians(yaw))*beam)

effective_beam(10, 160, 1000)
effective_beam(10, 160, 1201)

ch_compliant = ch[ch.SPEED <= 10]
sv_compliant = sv[sv.SPEED <= 10]
ch_non_compliant = ch[ch.SPEED > 10]
sv_non_compliant = sv[sv.SPEED > 10]

ch_panamax = ch[ch['vessel class'] == 'Panamax']
ch_post_panamax = ch[ch['vessel class'] == 'Post Panamax']
sv_panamax = sv[sv['vessel class'] == 'Panamax']
sv_post_panamax = sv[sv['vessel class'] == 'Post Panamax']

hover_dict = {'Date/Time UTC':True, 'MMSI':True, 'SPEED':True, 'course behavior':True,
                'WDIR degT':True, 'WSPD mph':True, 'GST mph':True,'Yaw':True, 'LOA ft':True,
                'Beam ft':True, 'effective beam ft':True}
##################Stats findings graph for website###############################
ch['VSPD kn'] = ch.SPEED.copy()
fig1 = px.histogram(ch, x='VSPD kn', nbins=20, color_discrete_sequence=['teal'])
fig1.update_layout(xaxis_title_text = 'Vessel speed',
                   yaxis_title_text = 'Unique AIS Positions',
                   title = 'Vessel Speed Histogram' '<br>'
                           "Compliance Rate: " + str(round(sum(ch['SPEED'] <= 10) / ch.shape[0] * 100, 2)) + "%",
                   showlegend = True)
fig1.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=10, y0=0, x1=10, y1=1, line={'dash': 'solid', 'color':'Red', 'width':2}))
fig1.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=ch.SPEED.mean(), y0=0, x1=ch.SPEED.mean(), y1=1, line={'dash': 'dash', 'color':'Black', 'width':2.5}))
sv['VSPD kn'] = sv.SPEED.copy()
fig1 = px.histogram(sv, x='VSPD kn', nbins=20, color_discrete_sequence=['teal'])
fig1.update_layout(xaxis_title_text = 'Vessel speed',
                   yaxis_title_text = 'Unique AIS Positions',
                   title = 'Vessel Speed Histogram' '<br>'
                           "Compliance Rate: " + str(round(sum(sv['SPEED'] <= 10) / sv.shape[0] * 100, 2)) + "%",
                   showlegend = True)
fig1.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=10, y0=0, x1=10, y1=1, line={'dash': 'solid', 'color':'Red', 'width':2}))
fig1.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=sv.SPEED.mean(), y0=0, x1=sv.SPEED.mean(), y1=1, line={'dash': 'dash', 'color':'Black', 'width':2.5}))

fig2 = px.histogram(ch['WSPD mph'], nbins=15, color_discrete_sequence=['darkseagreen'])
fig2.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=30, y0=0, x1=30, y1=1, line={'dash': 'solid'}, name='test'))
fig2.update_layout(title="Windspeed Histogram" '<br>'
                        "Adverse Conditions: " + str(round((ch[ch['WSPD mph'] >= 30].shape[0] / ch.shape[0]) * 100, 2)) + '% ',
                  xaxis_title_text='Windspeed', yaxis_title_text="Unique AIS Positions",
                  showlegend = True)
fig2 = px.histogram(sv['WSPD mph'], nbins=15, color_discrete_sequence=['darkseagreen'])
fig2.add_shape(go.layout.Shape(type='line', xref='x', yref='paper',
                        x0=30, y0=0, x1=30, y1=1, line={'dash': 'solid'}, name='test'))
fig2.update_layout(title="Windspeed Histogram" '<br>'
                        "Adverse Conditions: " + str(round((sv[sv['WSPD mph'] >= 30].shape[0] / sv.shape[0]) * 100, 2)) + '% ',
                  xaxis_title_text='Windspeed', yaxis_title_text="Unique AIS Positions",
                  showlegend = True)

fig3 = px.scatter(ch, x = 'SPEED', y = 'WSPD mph', hover_data = hover_dict, color_discrete_sequence = ['forestgreen'])
fig3.update_layout(xaxis_title_text = "VSPD kn",
                 title = "WSPD vs. VSPD" '<br>'
                        "Correlation: " + str(round(ch.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1] * 100, 2)) + "%")
fig3 = px.scatter(sv, x = 'SPEED', y = 'WSPD mph', hover_data = hover_dict, color_discrete_sequence = ['forestgreen'])
fig3.update_layout(xaxis_title_text = "VSPD kn",
                 title = "WSPD vs. VSPD" '<br>'
                        "Correlation: " + str(round(sv.dropna()[['SPEED', 'WSPD mph']].corr().iloc[0][1] * 100, 2)) + "%")

t1 = go.Scatter(x=ch.index, y=ch['SPEED'], mode='lines', name='VSPD kn')
t2 = go.Scatter(x=ch.index, y=ch['Yaw'], mode='lines', name='Yaw deg')
data = [t1, t2]
fig4 = go.Figure(data=data)#, layout=layout)
fig4.update_layout(title="VSPD-Yaw Correlation: " + str(round(ch.dropna()[['SPEED', 'Yaw']].corr().iloc[0][1], 2)) + '<br>'
                         "Compliant Mean Yaw: " + str(round(ch[ch.SPEED <= 10].Yaw.mean(), 2)) + ' deg' + '<br>'
                         "Non Compliant Mean Yaw:  " + str(round(ch[ch.SPEED > 10].Yaw.mean(), 2)) + ' deg')

t1 = go.Scatter(x=sv.index, y=sv['SPEED'], mode='lines', name='VSPD kn')
t2 = go.Scatter(x=sv.index, y=sv['Yaw'], mode='lines', name='Yaw deg')
data = [t1, t2]
fig4 = go.Figure(data=data)#, layout=layout)
fig4.update_layout(title="VSPD-Yaw Correlation: " + str(round(sv.dropna()[['SPEED', 'Yaw']].corr().iloc[0][1], 2)) + '<br>'
                         "Compliant Mean Yaw: " + str(round(sv[sv.SPEED <= 10].Yaw.mean(), 2)) + ' deg' + '<br>'
                         "Non Compliant Mean Yaw:  " + str(round(sv[sv.SPEED > 10].Yaw.mean(), 2)) + ' deg')

# fig5 - another yaw visualization. try breaking apart the compliant vs non-compliant yaw values into a graph_
# fig6 - oneway vs twoway transit visualization. probably bar chart ?
# effective beam visualization ? would need to use the width of channel for this to be effective..
# maybe add that into twoway transit visualization to show that the pilots actually have a lot of space... maybe

px.violin(non_compliant.Yaw)
px.violin(compliant.Yaw)
px.histogram(ch, x='effective beam ft', color='vessel class')

# ch_ec = [1000, 800, 400]
# sv_ec = [600, 300]
# for i in len(ch):
#     if ch.loc[i, 'vessel class'] == "Post Panamax":
#         ch.loc[i, 'channel space'] = ch.loc[i, 'effective beam ft'] / ch_ec[1]
#     elif


ch_post_panamax['channel space'] = round(ch_post_panamax['effective beam ft'] / 800, 2)
px.histogram(ch_post_panamax['channel space'])


px.violin(ch[['WSPD mph', 'GST mph']])


px.strip(ch, x='Name', y='SPEED', hover_data=hover_dict) #array of vessel speed copy from last year..
# line plot for every ship in the channel... speed vs time
for ship in ch.MMSI.unique():
    trace = go.Scatter()
    plt = px.line(ch[ch.MMSI == ship], x='Date/Time UTC', y='SPEED', color="course behavior", hover_name="Name", hover_data=hover_dict)
    plt.show()


# COMPLIANT
px.scatter(ch_compliant, x='SPEED', y='WSPD mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)
px.scatter(ch_compliant, x='SPEED', y='GST mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)
# px.scatter(compliant, y='effective beam ft', x='GST mph', size='Yaw', color='SPEED', hover_data=hover_dict)
comp_corr_mat = ch_compliant.dropna()[['SPEED', 'WSPD mph', 'GST mph', 'Yaw', 'effective beam ft']]
comp_correlation = comp_corr_mat.corr()
px.imshow(comp_correlation)

# NON_COMPLIANT
px.scatter(ch_non_compliant, x='SPEED', y='GST mph', size='Yaw', color='effective beam ft', hover_data=hover_dict)
# px.scatter(non_compliant, y='effective beam ft', x='GST mph', size='Yaw', color='SPEED', hover_data=hover_dict)
non_comp_corr_mat = ch_non_compliant.dropna()[['SPEED', 'WSPD mph', 'GST mph', 'Yaw', 'effective beam ft']]
non_comp_correlation = non_comp_corr_mat.corr()
px.imshow(non_comp_correlation)



########################################################################
dat = ch.sort_values('Date/Time UTC').reset_index().dropna()
dat['SPEED mph'] = dat['SPEED'] * 1.151
dat['WDIR degT'] = dat['WDIR degT'].astype(int)
dat['Date/Time UTC'].plot()
trace1 = go.Scatter(x=dat.index, y=dat['WSPD mph'], mode='lines', name='WSPD mph')
trace2 = go.Scatter(x=dat.index, y=dat['SPEED'], mode='lines', name='VSPD kn')
trace3 = go.Scatter(x=dat.index, y=dat['GST mph'], mode='lines', name='GST mph')
trace4 = go.Scatter(x=dat.index, y=dat['Yaw'], mode='lines', name='Yaw')
data = [trace1, trace2, trace3, trace4]
fig = go.Figure(data=data)#, layout=layout)
fig.show()
#######################################################

###### YAW ANALAYSIS
high_yaw = ch[ch.MMSI.isin(ch[ch.Yaw >= 10].MMSI.unique())]
ch[ch.Yaw >= 9]
for ship in ch[ch.Yaw >= 8].MMSI.unique():
    t1 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['SPEED'], mode='markers', name='VSPD kn')
    t2 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['Yaw'], mode='markers', name='Yaw')
    t3 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['GST mph'], mode='markers', name='Gust mph')
    t4 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()['Date/Time UTC'], y=high_yaw[high_yaw.MMSI == ship]['WSPD mph'], mode='markers', name='WSPD mph')
    fig = go.Figure(data=[t1, t2, t3, t4])#, layout=layout)
    fig.show()
    # plt = px.line(ch[ch.MMSI == ship], x='Date/Time UTC', y='SPEED', color="course behavior", hover_name="Name", hover_data=hover_dict)
    # plt.show()
px.scatter(ch[(ch.MMSI == 338241000) & (ch['course behavior'] == 'Inbound')], x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)
px.scatter(ch[(ch.MMSI == 338241000) & (ch['course behavior'] == 'Outbound')], x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)


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



t1 = go.Scatter(x=compliant.sort_values('Date/Time UTC').reset_index().index, y=compliant.sort_values('Date/Time UTC').reset_index()['SPEED'], mode='lines', name='VSPD kn')
t2 = go.Scatter(x=compliant.sort_values('Date/Time UTC').reset_index().index, y=compliant.sort_values('Date/Time UTC').reset_index()['Yaw'], mode='lines', name='Yaw deg')
data = [t1, t2]
fig = go.Figure(data=data)#, layout=layout)
fig.update_layout(title="Compliant VSPD-Yaw Correlation: " + str(round(compliant.dropna()[['SPEED', 'Yaw']].corr().iloc[0][1], 2)))
fig.show()




ch_compliant[['SPEED', 'Yaw']].corr()
non_compliant[['SPEED', 'Yaw']].corr()

sv_compliant[['SPEED', 'Yaw']].corr()
sv_non_compliant[['SPEED', 'Yaw']].corr()


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
           ch[(ch.MMSI == mmsi[5]) & (ch['rounded date'] == times[2])],
           ch[(ch.MMSI == mmsi[6]) & (ch['rounded date'] == times[3])],
           ch[(ch.MMSI == mmsi[7]) & (ch['rounded date'] == times[3])],
           ch[(ch.MMSI == mmsi[8]) & (ch['rounded date'] == times[4])],
           ch[(ch.MMSI == mmsi[9]) & (ch['rounded date'] == times[4])]])#,
           # ch[(ch.MMSI == mmsi[10]) & (ch['rounded date'] == times[5])],
           # ch[(ch.MMSI == mmsi[11]) & (ch['rounded date'] == times[5])]
           ])

ch.shape
two_way.shape
print(str(round((two_way.shape[0] / ch.shape[0])*100, 2)) + '%')
len(ch.MMSI.unique())

one_way = ch[~ch.index.isin(two_way.index)]
one_way.shape
px.scatter(one_way, x='SPEED', y='WSPD mph', size='Yaw', hover_data=hover_dict, color='vessel class')

px.scatter(one_way, x='WSPD mph', y='Yaw', hover_data=hover_dict, color='SPEED')

px.scatter(one_way, x='SPEED', y='WSPD mph', color='Yaw', hover_data=hover_dict)

px.scatter(two_way, x='SPEED', y='WSPD mph', color='vessel class', hover_data=hover_dict)




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


####### Yaw algorithm...
px.violin(ch[ch.COURSE > 200][['COURSE', 'HEADING']])
px.violin(ch[ch.COURSE < 200][['COURSE', 'HEADING']])

px.histogram(sv[sv.COURSE > 200][['COURSE', 'HEADING']])
px.histogram(sv[sv.COURSE < 200][['COURSE', 'HEADING']])

for ship in sv[(sv.COURSE > 200) & (sv.Yaw >= 9)].MMSI.unique():
    t1 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.HEADING > 200)].reset_index()['Date/Time UTC'],
                    y=sv[(sv.MMSI == ship) & (sv.HEADING > 200)].HEADING, mode='lines+markers', name='Heading')
    t2 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.COURSE > 200)].reset_index()['Date/Time UTC'],
                    y=sv[(sv.MMSI == ship) & (sv.COURSE > 200)].COURSE, mode='lines+markers', name='COURSE')
    data = [t1, t2]
    fig = go.Figure(data=data)#, layout=layout)
    fig.update_layout(title='Savannah ' + str(ship) + ' Inbound Course and Heading')
    fig.show()

for ship in sv[(sv.COURSE < 200) & (sv.Yaw >= 8)].MMSI.unique():
    t1 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.HEADING < 200)].reset_index()['Date/Time UTC'],
                    y=sv[(sv.MMSI == ship) & (sv.HEADING < 200)].HEADING, mode='lines+markers', name='Heading')
    t2 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.COURSE < 200)].reset_index()['Date/Time UTC'],
                    y=sv[(sv.MMSI == ship) & (sv.COURSE < 200)].COURSE, mode='lines+markers', name='COURSE')
    data = [t1, t2]
    fig = go.Figure(data=data)#, layout=layout)
    fig.update_layout(title='Savannah ' + str(ship) + ' Outbound Course and Heading')
    fig.show()


# charleston outbound high yaw ships in pilot staging area
df1 = ch[(ch.MMSI.isin(ch[(ch.COURSE < 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique())) &
    (ch.COURSE < 200) &
    (ch.Longitude >= -79.692)]
# charleston inbound high yaw ships in pilot staging area
df2 = ch[(ch.MMSI.isin(ch[(ch.COURSE > 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique())) &
    (ch.COURSE > 200) &
    (ch.Longitude >= -79.692)]

for ship in ch[(ch.COURSE > 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique():
    t1 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.HEADING > 200)].reset_index()['Date/Time UTC'],
                    y=ch[(ch.MMSI == ship) & (ch.HEADING > 200)].HEADING, mode='lines+markers', name='Heading')
    t2 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE > 200)].reset_index()['Date/Time UTC'],
                    y=ch[(ch.MMSI == ship) & (ch.COURSE > 200)].COURSE, mode='lines+markers', name='COURSE')
    data = [t1, t2]
    fig = go.Figure(data=data)#, layout=layout)
    fig.update_layout(title='Charleston ' + str(ship) + ' Inbound Course and Heading')
    fig.show()

for ship in ch[(ch.COURSE < 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique():
    t1 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].reset_index()['Date/Time UTC'],
                    y=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].HEADING, mode='lines+markers', name='Heading')
    t2 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].reset_index()['Date/Time UTC'],
                    y=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].COURSE, mode='lines+markers', name='COURSE')
    data = [t1, t2]
    fig = go.Figure(data=data)#, layout=layout)
    fig.update_layout(title='Charleston ' + str(ship) + ': Outbound Course and Heading')
    fig.show()

px.scatter(ch, x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)
px.scatter(ch[ch.Yaw >= 8], x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)
px.scatter(ch[ch.Longitude >= -79.692], x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)


px.scatter(sv, x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)
px.scatter(sv[sv.Yaw >= 6], x='Longitude', y='Latitude', color='Yaw', hover_data=hover_dict)
