
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

# this will take a long time to run...
# for some reason the dates are out of order, i suspect might contribute to long
# and inefficient run times... look into this and fix ?
# count number of post-panamax meetpass instances along with total number of instances
# calculate percentage of transits that are meeting and passing
# graph.... 
meetpass(ch)

# 15 meetpass instances from Oct6-Oct19 and Nov11-Nov18 sans a few days
# 7 out of 15 were both post-panamax ships..
ch.shape
ch[ch.isnull().any(axis=1)].shape
ch.columns

dat = ch.sort_values('Date/Time UTC').reset_index().dropna()
dat['SPEED mph'] = dat['SPEED'] * 1.151
sns.scatterplot(data = dat, y = 'SPEED', x = 'WSPD mph')

dat['Date/Time UTC'].plot()

# the x-axis here represents time from Oct4-Nov17 2020
f, axes = plt.subplots(figsize=(40,15), sharex=True)
plt.style.use('seaborn-white')
sns.set_style("whitegrid")
dat['WSPD mph'].plot(legend=True, linewidth=3, fontsize=30)
dat['SPEED mph'].plot(legend=True, linewidth=3, fontsize=30)
plt.title('Vessel Speed and Wind Speed Lineplots', fontsize=35)
plt.legend(loc=2, prop={'size': 30})
#plt.savefig('VSPD&WSDP_lineplot.png')

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
