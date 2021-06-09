import pandas as pd
import math
import sys
import os

import plotly.figure_factory as ff
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import text
# %matplotlib inline

ch = pd.read_csv("../html/riwhale.github.io/master-ch.csv")
sv = pd.read_csv("../html/riwhale.github.io/master-sv.csv")

# ch = pd.read_csv(os.path.join(os.getcwd(), "html/riwhale.github.io/master-ch.csv"))
# ch_max = pd.read_csv(os.path.join(os.getcwd(), "html/riwhale.github.io/master-ch-max.csv"))
# sv = pd.read_csv(os.path.join(os.getcwd(), "html/riwhale.github.io/master-sv.csv"))
# sv_max = pd.read_csv(os.path.join(os.getcwd(), "html/riwhale.github.io/master-sv-max.csv"))
sv = sv.drop("Unnamed: 0", axis=1)
ch = ch.drop("Unnamed: 0", axis=1)

# for df in [ch, ch_max, sv, sv_max]:
#     df.loc[:, "Date/Time UTC"] = pd.to_datetime(df.loc[:, "Date/Time UTC"])
print("\n2020-2021 Compliance Report Seasonal Stats\n")

print("Wind outages at Charleston occurred %.2f%% of the time through the SMA season" % (100*len(ch[ch.isnull().any(axis=1)])/len(ch)))
print("Wind outages at Savannah occurred %.2f%% of the time through the SMA season" % (100*len(sv[sv.isnull().any(axis=1)])/len(sv)))
print("The following stats are computed using the remainder of the data without wind outages\n")
ch = ch.dropna()
sv = sv.dropna()

print("The correlation value between wind speed and vessel speed at Charleston was %.2f" % (ch[["VSPD kn", "WSPD mph"]].corr().iloc[1][0]))
print("The correlation value between wind speed and vessel speed at Savannah was %.2f\n" % (sv[["VSPD kn", "WSPD mph"]].corr().iloc[1][0]))

print("The 2020-2021 SMA season at Charleston consisted of %d AIS positions" % (len(ch)))
print("The 2020-2021 SMA season at Savannah consisted of %d AIS positions\n" % (len(sv)))
# print("Charleston sans outages shape: ", ch.dropna().shape)



print("There were %d unique vessels at Charleston throughout the 2020-2021 SMA season" % (len(ch.MMSI.unique())))
print("There were %d unique vessels at Savannah throughout the 2020-2021 SMA season\n" % (len(sv.MMSI.unique())))


# null_data = ch[ch.isnull().any(axis=1)]
# null_data.shape
# len(null_data)/len(ch)*100
#
# null_data = sv[sv.isnull().any(axis=1)]
# null_data.shape
# len(null_data)/len(sv)*100

print("Charleston one way transits: %.2f%%" % (100*ch["Transit"].value_counts()[0]/len(ch)))
print("Charleston two way transits: %.2f%%" % (100*ch["Transit"].value_counts()[1]/len(ch)))
print("Savannah one way transits: %.2f%%" % (100*sv["Transit"].value_counts()[0]/len(sv)))
print("Savannah two way transits: %.2f%%\n" % (100*sv["Transit"].value_counts()[1]/len(sv)))

print("Charleston WSPD less than 20mph was recorded %.2f%% of the 2020-2021 SMA season" % (len(ch[ch["WSPD mph"] < 20])/len(ch)*100))
print("Charleston WSPD 20mph or higher was recorded %.2f%% of the 2020-2021 SMA season" % (len(ch[ch["WSPD mph"] >= 20])/len(ch)*100))
print("Charleston WSPD 25mph or higher was recorded %.2f%% of the 2020-2021 SMA season" % (len(ch[ch["WSPD mph"] >= 25])/len(ch)*100))
print("Charleston WSPD 30mph or higher was recorded %.2f%% of the 2020-2021 SMA season" % (len(ch[ch["WSPD mph"] >= 30])/len(ch)*100))
print("Savannah WSPD less than 20mph was recorded %.2f%% of the 2020-2021 SMA season" % (len(sv[sv["WSPD mph"] < 20])/len(sv)*100))
print("Savannah WSPD 20mph or higher was recorded %.2f%% of the 2020-2021 SMA season" % (len(sv[sv["WSPD mph"] >= 20])/len(sv)*100))
print("Savannah WSPD 25mph or higher was recorded %.2f%% of the 2020-2021 SMA season" % (len(sv[sv["WSPD mph"] >= 25])/len(sv)*100))
print("Savannah WSPD 30mph or higher was recorded %.2f%% of the 2020-2021 SMA season\n" % (len(sv[sv["WSPD mph"] >= 30])/len(sv)*100))

print("Average Yaw for compliant ships at Charleston was %.2f degrees" % (ch[ch["VSPD kn"] <= 10]["Yaw deg"].mean()))
print("Average Yaw for non-compliant ships at Charleston was %.2f degrees" % (ch[ch["VSPD kn"] > 10]["Yaw deg"].mean()))
print("The difference in yaw between compliant and non-compliant ships at Charleston was %.2f degrees" % (abs(ch[ch["VSPD kn"] <= 10]["Yaw deg"].mean() - ch[ch["VSPD kn"] > 10]["Yaw deg"].mean())))
print("Charleston transits through the SMA season exhibited a %.2f correlation between VSPD and Yaw" % (ch[["VSPD kn", "Yaw deg"]].corr().iloc[1][0]))
print("Average Yaw for compliant ships at Savannah was %.2f degrees" % (sv[sv["VSPD kn"] <= 10]["Yaw deg"].mean()))
print("Average Yaw for non-compliant ships at Savannah was %.2f degrees" % (sv[sv["VSPD kn"] > 10]["Yaw deg"].mean()))
print("The difference in yaw between compliant and non-compliant ships at Savannah was %.2f degrees" % (abs(sv[sv["VSPD kn"] <= 10]["Yaw deg"].mean() - sv[sv["VSPD kn"] > 10]["Yaw deg"].mean())))
print("Savannah transits through the SMA season exhibited a %.2f correlation between VSPD and Yaw\n" % (sv[["VSPD kn", "Yaw deg"]].corr().iloc[1][0]))

print("%.2f%% of positions at Charleston exhibited Yaw greater than or equal to 10 degrees. That's %d out of %d positions." % (100*len(ch[ch["Yaw deg"] >= 10])/len(ch) , len(ch[ch["Yaw deg"] >= 10]), len(ch)))
print("%.2f%% of positions at Savannah exhibited Yaw greater than or equal to 10 degrees. That's %d out of %d positions.\n" % (100*len(sv[sv["Yaw deg"] >= 10])/len(sv) , len(sv[sv["Yaw deg"] >= 10]), len(sv)))

len(ch[(ch["Transit"] == "Two-way Transit") & (ch["WSPD mph"] >= 30)])
len(sv[(sv["Transit"] == "Two-way Transit") & (sv["WSPD mph"] >= 30)])

print("%.2f%% of positions at Charleston were Two-way with winds greater than or equal to 30mph. That's %d out of %d positions." % (100*len(ch[(ch["Transit"] == "Two-way Transit") & (ch["WSPD mph"] >= 30)])/len(ch) , len(ch[(ch["Transit"] == "Two-way Transit") & (ch["WSPD mph"] >= 30)]), len(ch)))
print("%d%% of positions at Savannah were Two-way with winds greater than or equal to 30mph.\n" % (100*len(sv[(sv["Transit"] == "Two-way Transit") & (sv["WSPD mph"] >= 30)])/len(sv)))

print("Post-Panamax ships at Charleston made %d out of %d transits, making up %.2f%% of large cargo ship traffic in the 2020-2021 season." % (len(ch[ch["Class"] == "Post-Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1)),
len(ch.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2)), 100*len(ch[ch["Class"] == "Post-Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1))/len(ch.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2))))
print("Panamax ships at Charleston made %d out of %d transits, making up %.2f%% of large cargo ship traffic in the 2020-2021 season.\n" % (len(ch[ch["Class"] == "Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1)),
len(ch.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2)), 100*len(ch[ch["Class"] == "Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1))/len(ch.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2))))
print("Post-Panamax ships at Savannah made %d out of %d transits, making up %.2f%% of large cargo ship traffic in the 2020-2021 season." % (len(sv[sv["Class"] == "Post-Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1)),
len(sv.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2)), 100*len(sv[sv["Class"] == "Post-Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1))/len(sv.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2))))
print("Panamax ships at Savannah made %d out of %d transits, making up %.2f%% of large cargo ship traffic in the 2020-2021 season.\n" % (len(sv[sv["Class"] == "Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1)),
len(sv.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2)), 100*len(sv[sv["Class"] == "Panamax"].groupby(["MMSI", "Course Behavior"]).mean().index.get_level_values(1))/len(sv.groupby(["MMSI", "Class", "Course Behavior"]).mean().index.get_level_values(2))))

one = ch.describe().drop(["MMSI", "AIS Type", "Course", "Heading", "Buoy Source", "Longitude", "Latitude", "Effective Beam ft"], axis=1)
two = sv.describe().drop(["MMSI", "AIS Type", "Course", "Heading", "Buoy Source", "Longitude", "Latitude", "Effective Beam ft"], axis=1)
print(pd.concat([one, two], keys=["ch", "sv"], axis=0).round(2))
pd.concat([one, two], keys=["ch", "sv"], axis=0).round(2).to_csv("stats.csv")


ch_one_way = ch[ch.loc[:, "Transit"] == "One-way Transit"][["VSPD kn"]].describe().rename({"VSPD kn":"One-way VSPD kn"}, axis=1).round(2)
ch_two_way = ch[ch.loc[:, "Transit"] == "Two-way Transit"][["VSPD kn"]].describe().rename({"VSPD kn":"Two-way VSPD kn"}, axis=1).round(2)
ch_one_way.reset_index().merge(ch_two_way.reset_index(), "left").rename({"index":"Stat"}, axis=1).to_csv("ch_transit_vspd.csv")

sv_one_way = sv[sv.loc[:, "Transit"] == "One-way Transit"][["VSPD kn"]].describe().rename({"VSPD kn":"One-way VSPD kn"}, axis=1).round(2)
sv_two_way = sv[sv.loc[:, "Transit"] == "Two-way Transit"][["VSPD kn"]].describe().rename({"VSPD kn":"Two-way VSPD kn"}, axis=1).round(2)
sv_one_way.reset_index().merge(sv_two_way.reset_index(), "left").rename({"index":"Stat"}, axis=1).to_csv("sv_transit_vspd.csv")

def dashboard(df):
    """Generate DataFrame containing relevant port entrance statistics."""
    panamax = (df.loc[:, "Class"] == "Panamax")
    post_panamax = (df.loc[:, "Class"] == "Post-Panamax")
    nearshore = (df.loc[:, "Location"] == "Nearshore")
    offshore = (df.loc[:, "Location"] == "Offshore")
    inbound = (df.loc[:, "Course Behavior"] == "Inbound")
    outbound = (df.loc[:, "Course Behavior"] == "Outbound")
    dat = {"Proportion<br>of Transits":[
           str(round(sum(panamax) / len(df) * 100, 2)) + "%",
           str(round(sum(post_panamax) / len(df) * 100, 2)) + "%", "100%"
           ],
           "Compliance<br>Rate":[
           str(round(sum(panamax & (df.loc[:, "VSPD kn"] <= 10)) /
                     sum(panamax) * 100, 2)) + "%",
           str(round(sum(post_panamax & (df.loc[:, "VSPD kn"] <= 10)) /
                     sum(post_panamax) * 100, 2)) + "%",
           str(round(sum(df.loc[:, "VSPD kn"] <= 10) / len(df) * 100, 2)) + "%"
           ],
           "Mean<br>VSPD":[
           str(round(df[panamax].loc[:, "VSPD kn"].mean(), 2)) + " kn",
           str(round(df[post_panamax].loc[:, "VSPD kn"].mean(), 2)) + " kn",
           str(round(df.loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "Nearshore<br>Mean VSPD":[
           str(round(df[nearshore & panamax].loc[:, "VSPD kn"].mean(), 2)) +
           " kn",
           str(round(df[nearshore & post_panamax].loc[:,
           ("VSPD kn")].mean(), 2)) + " kn",
           str(round(df[nearshore].loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "Offshore<br>Mean VSPD":[
           str(round(df[offshore & panamax].loc[:, "VSPD kn"].mean(), 2)) +
           " kn",
           str(round(df[offshore & post_panamax].loc[:,
           ("VSPD kn")].mean(), 2)) + " kn",
           str(round(df[offshore].loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "Inbound<br>Mean VSPD":[
           str(round(df[inbound & panamax].loc[:, "VSPD kn"].mean(), 2)) +
           " kn",
           str(round(df[inbound & post_panamax].loc[:,
           ("VSPD kn")].mean(), 2)) + " kn",
           str(round(df[inbound].loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "Outbound<br>Mean VSPD":[
           str(round(df[outbound & panamax].loc[:, "VSPD kn"].mean(), 2)) +
           " kn",
           str(round(df[outbound & post_panamax].loc[:,
           ("VSPD kn")].mean(), 2)) + " kn",
           str(round(df[outbound].loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "VSPD-WSPD<br>Correlation":[
           str(round(df[panamax].dropna().loc[:, ("VSPD kn", "WSPD mph")].corr()
           .iloc[0][1], 2)),
           str(round(df[post_panamax].dropna().loc[:,
           ("VSPD kn", "WSPD mph")].corr().iloc[0][1], 2)),
           str(round(df.dropna().loc[:,
           ("VSPD kn", "WSPD mph")].corr().iloc[0][1], 2))
           ]
          }
    index = ["Panamax", "Post-Panamax", "Combined"]
    return pd.DataFrame(dat, index)

dash = pd.concat([dashboard(ch.dropna()), dashboard(sv.dropna())],
                  keys=["Charleston", "Savannah"],
                  axis=0).reset_index(level=1).rename(
                  {"level_1": "Class"}, axis=1)
dash.to_csv("dashboard.csv", mode="w", index=True)

plt.figure(figsize=(10,6))
fig = sns.kdeplot(data=ch, x="VSPD kn", y="WSPD mph", fill=True, cmap="mako_r")
plt.axvline(10,0,1, c="red")
text(10, 30, "Speed Limit", rotation=270, color="Red")
plt.savefig("../EOS_2020-2021/plots/vspd_vs_wspd_ch.pdf")

plt.figure(figsize=(10,6))
fig = sns.kdeplot(data=sv, x="VSPD kn", y="WSPD mph", fill=True, cmap="mako_r")
plt.axvline(10,0,1, c="red")
text(10, 30, "Speed Limit", rotation=270, color="Red")
plt.savefig("../EOS_2020-2021/plots/vspd_vs_wspd_sv.pdf")

plt.figure(figsize=(10,6))
fig = sns.histplot(data=ch, x="VSPD kn", bins=22, color="#19336A")
plt.axvline(10,0,1, c="red")
fig.set(ylabel='Unique AIS Positions')
text(10, 4800, "Speed Limit", rotation=270, color="Red")
plt.savefig("../EOS_2020-2021/plots/vspd_hist_ch.pdf")

plt.figure(figsize=(10,6))
fig = sns.histplot(data=sv, x="VSPD kn", bins=22, color="#19336A")
plt.axvline(10,0,1, c="red")
fig.set(ylabel='Unique AIS Positions')
text(10, 4000, "Speed Limit", rotation=270, color="Red")
plt.savefig("../EOS_2020-2021/plots/vspd_hist_sv.pdf")

plt.figure(figsize=(10,6))
fig = sns.stripplot(data=ch, x="Name", y="VSPD kn", size=4, hue="Transit", palette=["#19336A", "green"], edgecolor="white", linewidth=0.25)
plt.xticks([])
plt.axhline(10,0,1, c="red")
fig.set(xlabel='Vessels')
fig.legend(fontsize = 10,
           # loc = "upper left",
           # bbox_to_anchor= (1, 1),
           title="Transit",
           title_fontsize = 11,
           shadow = False,
           facecolor = 'white')
plt.savefig("../EOS_2020-2021/plots/vspd_strip4_ch.pdf")

plt.figure(figsize=(10,6))
fig = sns.stripplot(data=sv, x="Name", y="VSPD kn", size=4, hue="Transit", palette=["#19336A", "green"], edgecolor="white", linewidth=0.25)
plt.xticks([])
plt.axhline(10,0,1, c="red")
fig.set(xlabel='Vessels')
fig.legend(fontsize = 10,
           # bbox_to_anchor= (1.03, 1),
           title="Transit",
           title_fontsize = 11,
           shadow = True,
           facecolor = 'white')
plt.savefig("../../EOS_2020-2021/plots/vspd_strip_sv.pdf")

plt.figure(figsize=(10,6))
fig = sns.histplot(data=ch, x="WSPD mph", bins=22, color="steelblue")
plt.axvline(30,0,1, c="Black")
fig.set(ylabel='Unique AIS Positions')
text(30, 1000, "Adverse WSPD Threshold", rotation=270, color="Black")
plt.savefig("../EOS_2020-2021/plots/wspd_hist_ch.pdf")

plt.figure(figsize=(10,6))
fig = sns.histplot(data=sv, x="WSPD mph", bins=22, color="steelblue")
plt.axvline(30,0,1, c="Black")
fig.set(ylabel='Unique AIS Positions')
text(30, 1000, "Adverse WSPD Threshold", rotation=270, color="Black")
plt.savefig("../EOS_2020-2021/plots/wspd_hist_sv.pdf")


plt.figure(figsize=(10,6))
fig = ch.reset_index().loc[:, "Yaw deg"].plot(color="green", lw=1)
fig = ch.sort_values("VSPD kn").reset_index()["VSPD kn"].plot(color="#19336A", lw=1)
plt.xticks([])
fig.set(xlabel="AIS Positions", ylabel="Degrees and Knots")
plt.axhline(10,0,1, c="red")
fig.legend(fontsize = 10,
           # bbox_to_anchor= (1.03, 1),
           shadow = False,
           facecolor = 'white')
plt.savefig("../EOS_2020-2021/plots/yaw_lineplot_ch.pdf")

plt.figure(figsize=(10,6))
fig = sv.reset_index().loc[:, "Yaw deg"].plot(color="green", lw=1)
fig = sv.sort_values("VSPD kn").reset_index()["VSPD kn"].plot(color="#19336A", lw=1)
plt.xticks([])
fig.set(xlabel="AIS Positions", ylabel="Degrees and Knots")
plt.axhline(10,0,1, c="red")
fig.legend(fontsize = 10,
           # bbox_to_anchor= (1.03, 1),
           shadow = False,
           facecolor = 'white');
plt.savefig("../EOS_2020-2021/plots/yaw_lineplot_sv.pdf")

plt.figure(figsize=(10,6))
fig = sns.scatterplot(data=ch, x="VSPD kn", y="% Channel Occupied", hue="Transit", palette=["#19336A", "green"])
plt.axvline(10,0,1, c="red")
# fig.set(ylabel='Unique AIS Positions')
text(10.1, 74, "Speed Limit", color="Red")
fig.legend(fontsize = 10,
           loc = "upper left",
           # bbox_to_anchor= (1, 1),
           title="Transit",
           title_fontsize = 11,
           shadow = False,
           facecolor = 'white');
plt.savefig("../EOS_2020-2021/plots/channel_occupancy_ch.pdf")

plt.figure(figsize=(10,6))
fig = sns.scatterplot(data=sv, x="VSPD kn", y="% Channel Occupied", hue="Transit", palette=["#19336A", "green"])
plt.axvline(10,0,1, c="red")
# fig.set(ylabel='Unique AIS Positions')
text(10.1, 97, "Speed Limit", color="Red")
fig.legend(fontsize = 10,
            # loc = "upper left",
           bbox_to_anchor= (1, 1),
           title="Transit",
           title_fontsize = 11,
           shadow = False,
           facecolor = 'white')
plt.savefig("../EOS_2020-2021/plots/channel_occupancy_sv.pdf")


x = ['≤10', '(10-12]', '(12-14]', '(14-16]', '>16']
y = [ch[ch['VSPD kn'] <= 10].shape[0],
     ch[(ch['VSPD kn'] > 10) & (ch['VSPD kn'] <= 12)].shape[0],
     ch[(ch['VSPD kn'] > 12) & (ch['VSPD kn'] <= 14)].shape[0],
     ch[(ch['VSPD kn'] > 14) & (ch['VSPD kn'] <= 16)].shape[0],
     ch[(ch['VSPD kn'] > 16)].shape[0]]
fig1, ax1 = plt.subplots(figsize=(7,7))

ax1.pie(y, autopct='%1.1f%%', counterclock=False, pctdistance=1.128, startangle=180,
        colors=sns.color_palette("mako_r", as_cmap=False))
        # colors=["dodgerblue", "silver", "darkgrey", "grey", "dimgray", "black"])
        # colors=['dodgerblue', 'cornflowerblue', 'royalblue', 'blue', 'mediumblue', 'darkblue'])
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# plt.title('Proportion of Speed Increments \n Transits \n February 2017')
ax1.legend(x,
          title="Speed Increments (kn)",
          loc="upper right")
          # bbox_to_anchor=(1, 0, 0.5, 1))
plt.savefig("../../EOS_2020-2021/plots/vspd_piechart_ch.pdf")


x = ['≤10', '(10-12]', '(12-14]', '(14-16]', '>16']
y = [sv[sv['VSPD kn'] <= 10].shape[0],
     sv[(sv['VSPD kn'] > 10) & (sv['VSPD kn'] <= 12)].shape[0],
     sv[(sv['VSPD kn'] > 12) & (sv['VSPD kn'] <= 14)].shape[0],
     sv[(sv['VSPD kn'] > 14) & (sv['VSPD kn'] <= 16)].shape[0],
     sv[(sv['VSPD kn'] > 16)].shape[0]]
fig1, ax1 = plt.subplots(figsize=(7,7))
ax1.pie(y, autopct='%1.1f%%', counterclock=False, pctdistance=1.128, startangle=180,
        colors = sns.color_palette("mako_r", as_cmap=False))
        # colors=["dodgerblue", "silver", "darkgrey", "grey", "dimgray", "black"])
        # colors=['dodgerblue', 'cornflowerblue', 'royalblue', 'blue', 'mediumblue', 'darkblue'])
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# plt.title('Proportion of Speed Increments \n Transits \n February 2017')
ax1.legend(x,
          title="Speed Increments (kn)",
          loc="upper right")
          # bbox_to_ansvor=(1, 0, 0.5, 1))
plt.savefig("../../EOS_2020-2021/plots/vspd_piechart_sv.pdf")
