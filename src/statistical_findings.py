
from import_maritime_data import *
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
    report = import_report("../tests/" + filename)
    ch_agg.append(report[0][1])
    sv_agg.append(report[1][1])

ch = pd.concat(ch_agg)
ch = ch.sort_values("Date/Time UTC").reset_index().drop(["index"], axis=1)
sv = pd.concat(sv_agg)
sv = sv.sort_values("Date/Time UTC").reset_index().drop(["index"], axis=1)

ch_compliant = ch[ch["VSPD kn"] <= 10]
sv_compliant = sv[sv["VSPD kn"] <= 10]
ch_non_compliant = ch[ch["VSPD kn"] > 10]
sv_non_compliant = sv[sv["VSPD kn"] > 10]

ch["Compliance"] = "Non Compliant"
ch["Compliance"][ch.index.isin(ch_compliant.index)] = "Compliant"
sv["Compliance"] = "Non Compliant"
sv["Compliance"][sv.index.isin(sv_compliant.index)] = "Compliant"

ch_panamax = ch[ch["Vessel Class"] == "Panamax"]
ch_post_panamax = ch[ch["Vessel Class"] == "Post-Panamax"]

sv_panamax = sv[sv["Vessel Class"] == "Panamax"]
sv_post_panamax = sv[sv["Vessel Class"] == "Post-Panamax"]


# ch_meetpass = meetpass(ch)
# ch_two_way = twoway(ch, ch_meetpass)
# ch["Transit"] = "One Way Transit"
# ch["Transit"][ch.index.isin(ch_two_way.index)] = "Two Way Transit"
#
# sv_meetpass = meetpass(sv)
# sv_two_way = twoway(sv, sv_meetpass)
# sv["transit"] = "One Way Transit"
# sv["transit"][sv.index.isin(sv_two_way.index)] = "Two Way Transit"



hover_dict = {"Date/Time UTC":True, "MMSI":False, "VSPD kn":True, "WSPD mph":True, "Course Behavior":True,
              "Yaw":True, "LOA ft":False, "Beam ft":False, "Effective Beam ft":True,
              "Location":False, "Name":False}

# fig = px.scatter(ch, "Longitude", "Latitude")
# fig.add_trace(go.Scatter(x=np.array(-79.693877), y=np.array(32.665187)))
# fig.add_trace(go.Scatter(x=np.array(-79.691502), y=np.array(32.667473)))
# px.scatter(ch[ch.Latitude >= 32.667473], "Longitude", "Latitude")
#
#
# fig = px.scatter(sv, "Longitude", "Latitude")
# fig.add_trace(go.Scatter(x=np.array(-80.81597), y=np.array(32.02732)))
# fig.add_trace(go.Scatter(x=np.array(-80.81425), y=np.array(32.02838)))
# fig.add_trace(go.Scatter(x=np.array(-80.78055), y=np.array(31.99183)))
# fig.add_trace(go.Scatter(x=np.array(-80.77943), y=np.array(31.99346)))
# fig.add_trace(go.Scatter(x=np.array(-80.78879), y=np.array(31.99772)))
# fig.add_trace(go.Scatter(x=np.array(-80.78701), y=np.array(31.9985)))
# px.scatter(sv[(sv.Latitude <= 32.02838) & (sv.Latitude >= 31.9985) | (sv.Latitude <= 31.99183)], "Longitude", "Latitude")


def effective_beam(yaw, beam, loa):
    import math
    return (math.cos(math.radians(90-yaw))*loa) + (math.cos(math.radians(yaw))*beam)

effective_beam(10, 150, 1100)
effective_beam(10, 160, 1000)
##################Stats findings graph for website###############################
fig1 = px.histogram(ch, x="VSPD kn", color="Transit", nbins=20, color_discrete_sequence=["darkslateblue", "salmon"])
fig1.update_layout(barmode="overlay",
                   xaxis_title_text = "VSPD kn",
                   yaxis_title_text = "Unique AIS Positions",
                   title = "Compliance Rate: " + str(round(sum(ch["VSPD kn"] <= 10) / ch.shape[0] * 100, 2)) + "%" "<br>"
                           "Mean VSPD: " + str(round(ch["VSPD kn"].mean(), 2)) + " kn",
                   showlegend = True, hoverlabel=dict(bgcolor="white",
                                     font_size=13),
                   legend_title_text="",
                   plot_bgcolor="#F1F1F1",
                   font=dict(size=11))
fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                line=dict(color="Red", dash="solid", width=1.5), name="test")
fig1.add_shape(type="line", x0=ch["VSPD kn"].mean(), y0=0, x1=ch["VSPD kn"].mean(), y1=1,
               xref="x", yref="paper",
               line=dict(color="black", dash="dash", width=1.5), name="test")
fig1.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                    xref="x", x=10.15, yref="paper", y=1)
fig1.add_annotation(text="Mean", showarrow=False, textangle=90, font=dict(color="black"),
                    xref="x", x=ch["VSPD kn"].mean()+0.15, yref="paper", y=1,
                    hovertext=str(ch["VSPD kn"].mean()))
# fig1.add_trace(go.Scatter(x=[10,10], y=[0, 400], mode="lines", line=dict(color="Red", dash="solid", width=1.5), hoverinfo="skip", name="Regulatory Speed Limit"))
# fig1.add_trace(go.Scatter(x=[ch["VSPD kn"].mean(), ch["VSPD kn"].mean()], y=[0, 400], mode="lines", hoverinfo="skip", line=dict(color="Black", dash="solid", width=1.5), name="Mean VSPD kn: " + str(round(ch["VSPD kn"].mean(), 2))))
fig1.data[0].marker.line.width = 0.5
fig1.data[0].marker.line.color = "black"
fig1.data[1].marker.line.width = 0.5
fig1.data[1].marker.line.color = "black"
pio.write_html(fig1, file="../tests/VSPD_hist.html", auto_open=False)
fig1

# TITLE:
# Vessel Speed Histogram
fig1 = px.histogram(sv, x="VSPD kn", color="Transit", nbins=20, color_discrete_sequence=["plum", "rebeccapurple"]) #width=800, height=600)#, color_discrete_sequence=["teal"])
fig1.update_layout(barmode="overlay",
                   xaxis_title_text = "VSPD kn",
                   yaxis_title_text = "Unique AIS Positions",
                   title = "Compliance Rate: " + str(round(sum(sv["VSPD kn"] <= 10) / sv.shape[0] * 100, 2)) + "%" "<br>"
                           "Mean VSPD: " + str(round(sv["VSPD kn"].mean(), 2)) + " kn",
                   showlegend = True, hoverlabel=dict(bgcolor="white", font_size=13),
                   legend_title_text="",
                   plot_bgcolor="#F1F1F1",
                   font=dict(size=11))
fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                line=dict(color="Red", dash="solid", width=1.5), name="test", templateitemname="test", visible=True)
fig1.add_shape(type="line", x0=sv["VSPD kn"].mean(), y0=0, x1=sv["VSPD kn"].mean(), y1=1,
               xref="x", yref="paper",
               line=dict(color="black", dash="dash", width=1.5), name="test")
fig1.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                    xref="x", x=10.15, yref="paper", y=1)
fig1.add_annotation(text="Mean", showarrow=False, textangle=90, font=dict(color="black"),
                    xref="x", x=sv["VSPD kn"].mean()+0.15, yref="paper", y=1)
fig1.data[0].marker.line.width = 0.5
fig1.data[0].marker.line.color = "black"
fig1.data[1].marker.line.width = 0.5
fig1.data[1].marker.line.color = "black"
fig1
########################################################################
# "One-Minute Time Resolution Vessel Speed Plot"
fig2 = px.strip(ch, x="Name", y="VSPD kn",
                color="Transit", hover_data=hover_dict, hover_name="Name", stripmode="overlay",
                color_discrete_sequence=["darkslateblue", "salmon"], width=900, height=600,
                title= "One Way Transits: " + str(round((ch[ch.Transit == "One Way Transit"].shape[0] / ch.shape[0]) * 100, 2)) + "%" "<br>"
                       "Two Way Transits: " + str(round((ch[ch.Transit == "Two Way Transit"].shape[0] / ch.shape[0]) * 100, 2)) + "%")
fig2.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                line=dict(color="Red", dash="solid", width=1.5), name="test")
fig2.update_layout(xaxis_title_text = "",
                  hoverlabel=dict(bgcolor="white",
                                    font_size=13),
                  legend_title_text="",
                  font=dict(size=12),
                  plot_bgcolor="#F1F1F1")
fig2.update_traces(marker_size=5.5)
pio.write_html(fig2, file="../tests/VSPD_array.html", auto_open=False)


# px.strip(ch, x="Name", y="Longitude", hover_data=hover_dict, width=950, height=550, color="compliance", stripmode="overlay")

fig2 = px.strip(sv, x="Name", y="VSPD kn",
                color="Transit", hover_data=hover_dict, hover_name="Name", stripmode="overlay",
                color_discrete_sequence=["plum", "rebeccapurple"], width=900, height=600,
                title="One Way Transits: " + str(round((sv[sv.Transit == "One Way Transit"].shape[0] / sv.shape[0]) * 100, 2)) + "%" "<br>"
                       "Two Way Transits: " + str(round((sv[sv.Transit == "Two Way Transit"].shape[0] / sv.shape[0]) * 100, 2)) + "%") #array of vessel speed copy from last year..
fig2.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                line=dict(color="Red", dash="solid", width=1.5), name="test")
fig2.update_layout(xaxis_title_text = "",
                  hoverlabel=dict(bgcolor="white",
                                    font_size=13),
                  legend_title_text="",
                  plot_bgcolor="#F1F1F1",
                  font=dict(size=11))
fig2.update_traces(marker_size=5.5)

########################################################################
# TITLE:
# Windspeed Histogram
fig3 = px.histogram(ch.dropna()["WSPD mph"], color_discrete_sequence=["lightsteelblue"], nbins=15)
fig3.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                        x0=30, y0=0, x1=30, y1=1, line={"dash": "solid", "width":1.5}, name="test"))
fig3.update_layout(title="Adverse Wind Conditions: " + str(round((ch[ch["WSPD mph"] >= 30].shape[0] / ch.shape[0]) * 100, 2)) + "% ",
                  xaxis_title_text="WSPD mph", yaxis_title_text="Unique AIS Positions",
                  showlegend = False, hoverlabel=dict(bgcolor="white",
                                    font_size=13),
                                    plot_bgcolor="#F1F1F1",
                                    font=dict(size=11))
fig3.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=90, font=dict(color="black"),
                    xref="x", x=30.4, yref="paper", y=1)
fig3.data[0].marker.line.width = 0.5
fig3.data[0].marker.line.color = "black"
pio.write_html(fig3, file="../tests/WSPD_hist.html", auto_open=False)

fig3

fig3 = px.histogram(sv.dropna()["WSPD mph"], color_discrete_sequence=["darkseagreen"], nbins=15)
fig3.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                        x0=30, y0=0, x1=30, y1=1, line={"dash": "solid", "width":1.5}, name="test"))
fig3.update_layout(title="Adverse Wind Conditions: " + str(round((sv[sv["WSPD mph"] >= 30].shape[0] / sv.shape[0]) * 100, 2)) + "% ",
                  xaxis_title_text="WSPD mph", yaxis_title_text="Unique AIS Positions",
                  showlegend = False, hoverlabel=dict(bgcolor="white",
                                    font_size=13),
                                    plot_bgcolor="#F1F1F1")
fig3.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=90, font=dict(color="black"),
                    xref="x", x=30.4, yref="paper", y=1)
# fig3.add_vline(x=30, annotation_text="Adverse Condition Threshold", annotation_font_size=13, annotation_font_color="black")
fig3.data[0].marker.line.width = 0.5
fig3.data[0].marker.line.color = "black"
# fig3.update_xaxes(range=[sv["WSPD mph"].min(), sv["WSPD mph"].max()+2])
fig3
########################################################################
# TITLE:
# WSPD and VSPD Density Plot
fig4 = px.density_contour(ch.dropna(), x="VSPD kn", y="WSPD mph")
fig4.update_traces(contours_coloring = "fill", colorscale = "blues")
fig4.update_layout(xaxis_title_text = "VSPD kn", title="WSPD-VSPD Correlation: " + str(round(ch.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1] * 100, 2)) + "%",
                   hoverlabel=dict(bgcolor="white", font_size=13),
                   font=dict(size=11))
pio.write_html(fig4, file="../tests/density_plot.html", auto_open=False)


fig4 = px.density_contour(sv.dropna(), x="VSPD kn", y="WSPD mph")
fig4.update_traces(contours_coloring = "fill", colorscale = "blues")
fig4.update_layout(xaxis_title_text = "VSPD kn", title="WSPD-VSPD Correlation: " + str(round(sv.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1] * 100, 2)) + "%",
                   hoverlabel=dict(bgcolor="white", font_size=13),
                   font=dict(size=11))
########################################################################
t1 = go.Scatter(x=ch.index, y=ch["VSPD kn"], mode="lines", name="VSPD kn", line=dict(width=1.5, color="#1f77b4"), hoverinfo="skip")
t2 = go.Scatter(x=ch.index, y=ch["Yaw"], mode="lines", name="Yaw deg", line=dict(width=1.5, color="#9467bd"), hoverinfo="skip")
data = [t1, t2]
fig5 = go.Figure(data=data)#, layout=layout)
fig5.update_layout(title="VSPD-Yaw Correlation: " + str(round(ch.dropna()[["VSPD kn", "Yaw"]].corr().iloc[0][1], 2)) + "<br>"
                         "Compliant Yaw (Mean): " + str(round(ch[ch["VSPD kn"] <= 10].Yaw.mean(), 2)) + " deg" + "<br>"
                         "Non Compliant Yaw (Mean):  " + str(round(ch[ch["VSPD kn"] > 10].Yaw.mean(), 2)) + " deg",
                  xaxis_title_text="Unique AIS Positions",
                  width=900,
                  height=500,
                  plot_bgcolor="#F1F1F1",
                  font=dict(size=11))
pio.write_html(fig5, file="../tests/line_plot.html", auto_open=False)



t1 = go.Scatter(x=sv.index, y=sv["VSPD kn"], mode="lines", name="VSPD kn", line=dict(width=1.5), hoverinfo="skip")
t2 = go.Scatter(x=sv.index, y=sv["Yaw"], mode="lines", name="Yaw deg", line=dict(width=1.5), hoverinfo="skip")
data = [t1, t2]
fig5 = go.Figure(data=data)#, layout=layout)
fig5.update_layout(title="VSPD-Yaw Correlation: " + str(round(sv.dropna()[["VSPD kn", "Yaw"]].corr().iloc[0][1], 2)) + "<br>"
                         "Compliant Yaw (Mean): " + str(round(sv[sv["VSPD kn"] <= 10].Yaw.mean(), 2)) + " deg" + "<br>"
                         "Non Compliant Yaw (Mean):  " + str(round(sv[sv["VSPD kn"] > 10].Yaw.mean(), 2)) + " deg",
                   xaxis_title_text="Unique AIS Positions",
                   width=900,
                   plot_bgcolor="#F1F1F1",
                   font=dict(size=11))
########################################################################

# fig6 - another yaw visualization. try breaking apart the compliant vs non-compliant yaw values into a graph_
# effective beam visualization ? would need to use the width of channel for this to be effective..
# maybe add that into twoway transit visualization to show that the pilots actually have a lot of space... maybe

ch_transit_speeders = []
for mmsi in ch.MMSI.unique():
    ship = ch[ch.MMSI == mmsi]
    compl = len(ship[ship["VSPD kn"] <= 10])
    ch_transit_speeders.append(round(compl / len(ship), 2))

np.array(ch_transit_speeders).mean()

sv_transit_speeders = []
for mmsi in sv.MMSI.unique():
    ship = sv[sv.MMSI == mmsi]
    compl = len(ship[ship["VSPD kn"] <= 10])
    sv_transit_speeders.append(round(compl / len(ship), 2))

np.array(sv_transit_speeders).mean()
########################################################################

for row in range(len(ch)):
    if (ch.loc[row, 'Vessel Class'] == 'Post-Panamax') & (ch.loc[row, 'Transit'] == 'One Way Transit'):
        ch.loc[row, '% Channel Occupied'] = round((ch.loc[row, 'Effective Beam ft'] / 800) * 100, 2)
    elif (ch.loc[row, 'Vessel Class'] == 'Post-Panamax') & (ch.loc[row, 'Transit'] == 'Two Way Transit'):
        ch.loc[row, '% Channel Occupied'] = round((ch.loc[row, 'Effective Beam ft'] / 400) * 100, 2)
    elif (ch.loc[row, 'Vessel Class'] == 'Panamax') & (ch.loc[row, 'Transit'] == 'One Way Transit'):
        ch.loc[row, '% Channel Occupied'] = round((ch.loc[row, 'Effective Beam ft'] / 1000) * 100, 2)
    elif (ch.loc[row, 'Vessel Class'] == 'Panamax') & (ch.loc[row, 'Transit'] == 'Two Way Transit'):
        ch.loc[row, '% Channel Occupied'] = round((ch.loc[row, 'Effective Beam ft'] / 500) * 100, 2)

for row in range(len(sv)):
    if (sv.loc[row, 'Vessel Class'] == 'Post-Panamax') & (sv.loc[row, 'Transit'] == 'One Way Transit'):
        sv.loc[row, '% Channel Occupied'] = round((sv.loc[row, 'Effective Beam ft'] / 600) * 100, 2)
    elif (sv.loc[row, 'Vessel Class'] == 'Post-Panamax') & (sv.loc[row, 'Transit'] == 'Two Way Transit'):
        sv.loc[row, '% Channel Occupied'] = round((sv.loc[row, 'Effective Beam ft'] / 300) * 100, 2)
    elif (sv.loc[row, 'Vessel Class'] == 'Panamax') & (sv.loc[row, 'Transit'] == 'One Way Transit'):
        sv.loc[row, '% Channel Occupied'] = round((sv.loc[row, 'Effective Beam ft'] / 600) * 100, 2)
    elif (sv.loc[row, 'Vessel Class'] == 'Panamax') & (sv.loc[row, 'Transit'] == 'Two Way Transit'):
        sv.loc[row, '% Channel Occupied'] = round((sv.loc[row, 'Effective Beam ft'] / 300) * 100, 2)


fig = px.density_contour(ch[(ch['Transit'] == 'One Way Transit') & (ch['WSPD mph'] < 30)], y='VSPD kn', x='% Channel Occupied',
                         color_discrete_sequence=["darkslateblue", "salmon"], width=800, height=500,
                         title="Non Adverse Conditions: " + str(round(len(ch[(ch['Transit'] == 'One Way Transit') & (ch['WSPD mph'] < 30)]) / len(ch) * 100, 2)) + '%')
fig.update_traces(contours_coloring = "fill", colorscale = "greens")
fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=1, xref="x", yref="paper",
                line=dict(color="Red", dash="solid", width=1.5), name="test", templateitemname="test", visible=True)


fig = px.density_contour(sv[(sv['Transit'] == 'One Way Transit') & (sv['WSPD mph'] < 30)], y='VSPD kn', x='% Channel Occupied',
                            color_discrete_sequence=["darkslateblue", "salmon"], width=800, height=500,
                            title="Non Adverse Conditions: " + str(round(len(sv[(sv['Transit'] == 'One Way Transit') & (sv['WSPD mph'] < 30)]) / len(sv) * 100, 2)) + '%')
fig.update_traces(contours_coloring = "fill", colorscale = "greens")
fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=1, xref="x", yref="paper",
                line=dict(color="Red", dash="solid", width=1.5), name="test", templateitemname="test", visible=True)

########################################################################
# px.violin(non_compliant.Yaw)
# px.violin(compliant.Yaw)
# px.histogram(ch, x="effective beam ft", color="vessel class")
#
# # ch_ec = [1000, 800, 400]
# # sv_ec = [600, 300]
# # for i in len(ch):
# #     if ch.loc[i, "vessel class"] == "Post Panamax":
# #         ch.loc[i, "channel space"] = ch.loc[i, "effective beam ft"] / ch_ec[1]
# #     elif
#
#
# ch_post_panamax["channel space"] = round(ch_post_panamax["effective beam ft"] / 800, 2)
# px.histogram(ch_post_panamax["channel space"])
#
#
# px.violin(ch[["WSPD mph", "GST mph"]])
#
# len(ch[ch["Date/Time UTC"] < "2020-11-19"].Name.unique())
#
# fig = px.strip(ch[ch["Date/Time UTC"] < "2020-11-19"], x="Name", y="SPEED",
#                 color="adverse wind", hover_data=hover_dict, stripmode="overlay", color_discrete_sequence=["darkseagreen", "seagreen"]) #array of vessel speed copy from last year..
# fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig.update_layout(xaxis_title_text = "",
#                    yaxis_title_text = "VSPD kn")
# fig = px.strip(ch[ch["Date/Time UTC"] < "2020-11-19"], x="Name", y="SPEED",
#                 color="transit", hover_data=hover_dict, stripmode="overlay",
#                 color_discrete_sequence=["darkslateblue", "salmon"], width=800) #array of vessel speed copy from last year..
# fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig.update_layout(xaxis_title_text = "",
#                   yaxis_title_text = "VSPD kn")
#
# # fig.add_hline(y=10, annotation_text="Regulatory Speed", annotation_font_size=10, annotation_font_color="red")
#
#                    # title = "Vessel Speed Histogram" "<br>"
#                    #         "Compliance Rate: " + str(round(sum(ch["SPEED"] <= 10) / ch.shape[0] * 100, 2)) + "%",
#                    # showlegend = True)
#
# # line plot for every ship in the channel... speed vs time
# for ship in ch.MMSI.unique():
#     trace = go.Scatter()
#     plt = px.line(ch[ch.MMSI == ship], x="Date/Time UTC", y="SPEED", color="course behavior", hover_name="Name", hover_data=hover_dict)
#     plt.show()
#
#
# # COMPLIANT
# px.scatter(ch_compliant, x="SPEED", y="WSPD mph", size="Yaw", color="effective beam ft", hover_data=hover_dict)
# px.scatter(ch_compliant, x="SPEED", y="GST mph", size="Yaw", color="effective beam ft", hover_data=hover_dict)
# # px.scatter(compliant, y="effective beam ft", x="GST mph", size="Yaw", color="SPEED", hover_data=hover_dict)
# comp_corr_mat = ch_compliant.dropna()[["SPEED", "WSPD mph", "GST mph", "Yaw", "effective beam ft"]]
# comp_correlation = comp_corr_mat.corr()
# px.imshow(comp_correlation)
#
# # NON_COMPLIANT
# px.scatter(ch_non_compliant, x="SPEED", y="GST mph", size="Yaw", color="effective beam ft", hover_data=hover_dict)
# # px.scatter(non_compliant, y="effective beam ft", x="GST mph", size="Yaw", color="SPEED", hover_data=hover_dict)
# non_comp_corr_mat = ch_non_compliant.dropna()[["SPEED", "WSPD mph", "GST mph", "Yaw", "effective beam ft"]]
# non_comp_correlation = non_comp_corr_mat.corr()
# px.imshow(non_comp_correlation)
#
#
#
# ########################################################################
# dat = ch.sort_values("Date/Time UTC").reset_index().dropna()
# dat["SPEED mph"] = dat["SPEED"] * 1.151
# dat["WDIR degT"] = dat["WDIR degT"].astype(int)
# dat["Date/Time UTC"].plot()
# trace1 = go.Scatter(x=dat.index, y=dat["WSPD mph"], mode="lines", name="WSPD mph")
# trace2 = go.Scatter(x=dat.index, y=dat["SPEED"], mode="lines", name="VSPD kn")
# trace3 = go.Scatter(x=dat.index, y=dat["GST mph"], mode="lines", name="GST mph")
# trace4 = go.Scatter(x=dat.index, y=dat["Yaw"], mode="lines", name="Yaw")
# data = [trace1, trace2, trace3, trace4]
# fig = go.Figure(data=data)#, layout=layout)
# fig.show()
# #######################################################
#
# ###### YAW ANALAYSIS
# high_yaw = ch[ch.MMSI.isin(ch[ch.Yaw >= 10].MMSI.unique())]
# ch[ch.Yaw >= 9]
# for ship in ch[ch.Yaw >= 8].MMSI.unique():
#     t1 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()["Date/Time UTC"], y=high_yaw[high_yaw.MMSI == ship]["SPEED"], mode="markers", name="VSPD kn")
#     t2 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()["Date/Time UTC"], y=high_yaw[high_yaw.MMSI == ship]["Yaw"], mode="markers", name="Yaw")
#     t3 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()["Date/Time UTC"], y=high_yaw[high_yaw.MMSI == ship]["GST mph"], mode="markers", name="Gust mph")
#     t4 = go.Scatter(x=high_yaw[high_yaw.MMSI == ship].reset_index()["Date/Time UTC"], y=high_yaw[high_yaw.MMSI == ship]["WSPD mph"], mode="markers", name="WSPD mph")
#     fig = go.Figure(data=[t1, t2, t3, t4])#, layout=layout)
#     fig.show()
#     # plt = px.line(ch[ch.MMSI == ship], x="Date/Time UTC", y="SPEED", color="course behavior", hover_name="Name", hover_data=hover_dict)
#     # plt.show()
# px.scatter(ch[(ch.MMSI == 338241000) & (ch["course behavior"] == "Inbound")], x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
# px.scatter(ch[(ch.MMSI == 338241000) & (ch["course behavior"] == "Outbound")], x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
#
#
# inbound = ch[ch["course behavior"] == "Inbound"]
# outbound = ch[ch["course behavior"] == "Outbound"]
# for ship in inbound.MMSI.unique():
#     plt = px.scatter(inbound[inbound.MMSI == ship],
#                 x = "Longitude",
#                 y = "Latitude",
#                 hover_data=hover_dict,
#                 size="Yaw",
#                 range_color=[inbound.Yaw.min(),inbound.Yaw.max()])
#     plt.show()
#
# for ship in outbound.MMSI.unique():
#     plt = px.scatter(outbound[outbound.MMSI == ship],
#                 x = "Longitude",
#                 y = "Latitude",
#                 hover_data=hover_dict,
#                 size="Yaw",
#                 range_color=[outbound.Yaw.min(),outbound.Yaw.max()])
#     plt.show()
#
#
#
# t1 = go.Scatter(x=compliant.sort_values("Date/Time UTC").reset_index().index, y=compliant.sort_values("Date/Time UTC").reset_index()["SPEED"], mode="lines", name="VSPD kn")
# t2 = go.Scatter(x=compliant.sort_values("Date/Time UTC").reset_index().index, y=compliant.sort_values("Date/Time UTC").reset_index()["Yaw"], mode="lines", name="Yaw deg")
# data = [t1, t2]
# fig = go.Figure(data=data)#, layout=layout)
# fig.update_layout(title="Compliant VSPD-Yaw Correlation: " + str(round(compliant.dropna()[["SPEED", "Yaw"]].corr().iloc[0][1], 2)))
# fig.show()
#
#
#
#
# ch_compliant[["SPEED", "Yaw"]].corr()
# non_compliant[["SPEED", "Yaw"]].corr()
#
# sv_compliant[["SPEED", "Yaw"]].corr()
# sv_non_compliant[["SPEED", "Yaw"]].corr()
#
#
# CHARLESTON
ch_dat = {"Proportion of Transits":[str(round(ch_panamax.shape[0]/ch.shape[0]*100, 2)) + "%",
                                    str(round(ch_post_panamax.shape[0]/ch.shape[0]*100, 2)) + "%",
                                    "100%"],

          "Compliance Rate":[str(round(sum(ch_panamax["VSPD kn"] <= 10) / ch_panamax.shape[0] * 100, 2)) + "%",
                             str(round(sum(ch_post_panamax["VSPD kn"] <= 10) / ch_post_panamax.shape[0] * 100, 2)) + "%",
                             str(round(sum(ch["VSPD kn"] <= 10) / ch.shape[0] * 100, 2)) + "%"],

          "Nearshore Median Speed":[str(round(ch_panamax[ch_panamax["Location"] == "nearshore"]["VSPD kn"].median(),2)),
                                    str(round(ch_post_panamax[ch_post_panamax["Location"] == "nearshore"]["VSPD kn"].median(),2)),
                                    str(round(ch[ch["Location"] == "nearshore"]["VSPD kn"].median(),2))],

          "Offshore Median Speed":[str(round(ch_panamax[ch_panamax["Location"] == "offshore"]["VSPD kn"].median(),2)),
                                   str(round(ch_post_panamax[ch_post_panamax["Location"] == "offshore"]["VSPD kn"].median(),2)),
                                   str(round(ch[ch["Location"] == "offshore"]["VSPD kn"].median(),2))],

          "Inbound Median Speed":[str(round(ch_panamax[ch_panamax["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2)),
                                  str(round(ch_post_panamax[ch_post_panamax["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2)),
                                  str(round(ch[ch["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2))],

          "Outbound Median Speed":[str(round(ch_panamax[ch_panamax["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2)),
                                   str(round(ch_post_panamax[ch_post_panamax["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2)),
                                   str(round(ch[ch["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2))],

          "VSPD-WSPD correlation":[str(round(ch_panamax.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                   str(round(ch_post_panamax.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                   str(round(ch.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2))],

          "VSPD-GST correlation":[str(round(ch_panamax.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2)),
                                   str(round(ch_post_panamax.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2)),
                                   str(round(ch.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2))]
         }

ch_index = ["Panamax", "Post Panamax", "Combined"]

# SAVANNAH
sv_dat = {"Proportion of Transits":[str(round(sv_panamax.shape[0]/sv.shape[0]*100, 2)) + "%",
                                str(round(sv_post_panamax.shape[0]/sv.shape[0]*100, 2)) + "%",
                                "100%"],

          "Compliance Rate":[str(round(sum(sv_panamax["VSPD kn"] <= 10) / sv_panamax.shape[0] * 100, 2)) + "%",
                        str(round(sum(sv_post_panamax["VSPD kn"] <= 10) / sv_post_panamax.shape[0] * 100, 2)) + "%",
                        str(round(sum(sv["VSPD kn"] <= 10) / sv.shape[0] * 100, 2)) + "%"],

          "Nearshore Median Speed":[str(round(sv_panamax[sv_panamax["Location"] == "nearshore"]["VSPD kn"].median(),2)),
                                    str(round(sv_post_panamax[sv_post_panamax["Location"] == "nearshore"]["VSPD kn"].median(),2)),
                                    str(round(sv[sv["Location"] == "nearshore"]["VSPD kn"].median(),2))],

          "Offshore Median Speed":[str(round(sv_panamax[sv_panamax["Location"] == "offshore"]["VSPD kn"].median(),2)),
                                  str(round(sv_post_panamax[sv_post_panamax["Location"] == "offshore"]["VSPD kn"].median(),2)),
                                  str(round(sv[sv["Location"] == "offshore"]["VSPD kn"].median(),2))],

          "Inbound Median Speed":[str(round(sv_panamax[sv_panamax["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2)),
                                    str(round(sv_post_panamax[sv_post_panamax["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2)),
                                    str(round(sv[sv["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2))],

          "Outbound Median Speed":[str(round(sv_panamax[sv_panamax["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2)),
                        str(round(sv_post_panamax[sv_post_panamax["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2)),
                        str(round(sv[sv["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2))],

          "VSPD-WSPD correlation":[str(round(sv_panamax.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                 str(round(sv_post_panamax.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                 str(round(sv.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2))],

          "VSPD-GST correlation":[str(round(sv_panamax.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2)),
                                  str(round(sv_post_panamax.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2)),
                                  str(round(sv.dropna()[["VSPD kn", "GST mph"]].corr().iloc[0][1], 2))]
                                 }

sv_index = ["Panamax", "Post Panamax", "Combined"]


pd.DataFrame(ch_dat, ch_index)
# pd.DataFrame(ch_dat, ch_index)

pd.DataFrame(sv_dat, sv_index)
# pd.DataFrame(sv_dat, sv_index)
#
#
# ###### meeting/passing
ch_meetpass = meetpass(ch)
# sv_meetpass = meetpass(sv)
# for item in ch_meetpass.items():
#     print(item)
# for item in sv_meetpass.items():
#     print(item)
#
# for key in ch_meetpass:
#     this_mmsi = key[0]
#     that_mmsi = key[1]
#     this_class = key[2]
#     that_class = key[3]
#     mp_time = ch_meetpass[key][0]
#     print(this_mmsi)
#     print(this_class)
#     print(that_mmsi)
#     print(that_class)
#     print(mp_time)
#
#
# ch["rounded date"] = [ch["Date/Time UTC"].iloc[i].floor("Min") for i in range(len(ch["Date/Time UTC"]))]
# sv["rounded date"] = [sv["Date/Time UTC"].iloc[i].floor("Min") for i in range(len(sv["Date/Time UTC"]))]
#
# dat = []
# for key in ch_meetpass:
#     this_mmsi = key[0]
#     that_mmsi = key[1]
#     this_class = key[2]
#     that_class = key[3]
#     this_course = key[4]
#     that_course = key[5]
#     enc_time = ch_meetpass[key][0]
#     dat.append(pd.DataFrame({"mmsi":[this_mmsi, that_mmsi],
#                             "vessel class":[this_class, that_class],
#                             "course":[this_course, that_course]}))
# df = pd.concat(dat).reset_index().drop("index", axis=1)
# ################################################################################
# mmsi = []
# times = []
# courses = []
# vessel_class = []
# dist = []
# for i in range(len(ch_meetpass)):
#     mmsi.append(list(ch_meetpass)[i][0])
#     mmsi.append(list(ch_meetpass)[i][1])
#     vessel_class.append(list(ch_meetpass)[i][2])
#     vessel_class.append(list(ch_meetpass)[i][3])
#     courses.append(list(ch_meetpass)[i][4])
#     courses.append(list(ch_meetpass)[i][5])
#     times.append(list(ch_meetpass.values())[i][0])
#     dist.append(list(ch_meetpass.values())[i][1])
#
# timess = []
# dists = []
# for time in times:
#     timess.append(time)
#     timess.append(time)
# for d in dist:
#     dists.append(d)
#     dists.append(d)
#
# arrays = [timess, dists, mmsi, vessel_class, courses ]
# tuples = list(zip(*arrays))
# index = pd.MultiIndex.from_tuples(tuples, names=["rounded_mp_time", "min_deg_dist", "mmsi", "vessel class", "course behavior"])
# df = pd.DataFrame(np.random.randn(len(index)), index=index).drop(0, axis=1)
# df
# df.index.get_level_values(2)
#
# ch[(ch.MMSI == mmsi[0]) & (ch["rounded date"] <= times[0]) & (ch["course behavior"] == courses[0])]
#
# # add this into MAIN for STATS mode
# ch_meetpass = meetpass(ch)
# ch_two_way = twoway(ch, ch_meetpass)
# ch["transit"] = "one way transit"
# ch["transit"][ch.index.isin(ch_two_way.index)] = "two way transit"
#
#
# sv_two_way = twoway(sv, sv_meetpass)
# sv["transit"] = "one way transit"
# sv["transit"][sv.index.isin(sv_two_way.index)] = "two way transit"
#
#
#
# ch_two_way[(ch_two_way.MMSI == df.index.get_level_values(2)[8]) | (ch_two_way.MMSI == df.index.get_level_values(2)[9])]
#
# for i in range(len(df)):
#     if i%2 == 0:
#         t = ch_two_way[(ch_two_way.MMSI == df.index.get_level_values(2)[i]) | (ch_two_way.MMSI == df.index.get_level_values(2)[i+1])]
#         plt = px.scatter(t, x="Longitude", y="Latitude", color="Name", hover_data=hover_dict)
#         plt.show()
#
# ch[ch.transit == "two way transit"].shape
# ch[ch.transit == "one way transit"].shape
#
# print(str(round((ch[ch.transit == "two way transit"].shape[0] / ch.shape[0]) * 100, 2)) + "%")
#
#
# fig1 = px.histogram(ch, x="SPEED", color="transit", nbins=20, color_discrete_sequence=["darkslateblue", "salmon"])#, color_discrete_sequence=["teal"])
# fig1.update_layout(barmode="overlay",
#                    xaxis_title_text = "VSPD kn",
#                    yaxis_title_text = "Unique AIS Positions",
#                    title = "Vessel Speed Histogram" "<br>"
#                            "Compliance Rate: " + str(round(sum(ch["SPEED"] <= 10) / ch.shape[0] * 100, 2)) + "%",
#                    showlegend = True)
# fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig1.add_shape(type="line", x0=ch.SPEED.mean(), y0=0, x1=ch.SPEED.mean(), y1=1,
#                xref="x", yref="paper",
#                line=dict(color="black", dash="solid", width=1.5), name="test")
# fig1.data[0].marker.line.width = 0.75
# fig1.data[0].marker.line.color = "black"
# fig1
# # fig1.add_vline(x=10, annotation_text="Regulatory Speed", annotation_font_size=10, annotation_font_color="red")
# # fig1.add_vline(x=ch["SPEED"].mean(), annotation_text="Mean Vessel Speed", annotation_font_size=10, annotation_font_color="blue")
#
# fig1 = px.histogram(sv, x="SPEED", color="transit", nbins=20, color_discrete_sequence=["darkslateblue", "salmon"])#, color_discrete_sequence=["teal"])
# fig1.update_layout(barmode="overlay",
#                    xaxis_title_text = "VSPD kn",
#                    yaxis_title_text = "Unique AIS Positions",
#                    title = "Vessel Speed Histogram" "<br>"
#                            "Compliance Rate: " + str(round(sum(sv["SPEED"] <= 10) / sv.shape[0] * 100, 2)) + "%",
#                    showlegend = True)
# fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig1.add_shape(type="line", x0=sv.SPEED.mean(), y0=0, x1=sv.SPEED.mean(), y1=1,
#                xref="x", yref="paper",
#                line=dict(color="black", dash="solid", width=1.5), name="test")
# fig1.data[0].marker.line.width = 0.75
# fig1.data[0].marker.line.color = "black"
# fig1
# # fig1.add_vline(x=10, annotation_text="Regulatory Speed", annotation_font_size=10, annotation_font_color="red")
# # fig1.add_vline(x=sv["SPEED"].mean(), annotation_text="Mean Vessel Speed", annotation_font_size=10, annotation_font_color="blue")
#
#
#
#
# # fig = px.histogram(ch, x="SPEED", color="transit")
# # fig.update_layout(barmode="overlay")
# px.pie(ch, "transit")
# px.scatter(ch, x="SPEED", y="WSPD mph", color="transit", hover_data=hover_dict )
# fig = px.histogram(ch, x="SPEED", color="adverse wind")
# fig.update_layout(barmode="overlay")
# px.pie(ch, "adverse wind")
#
# one_way = ch[~ch.index.isin(ch_two_way.index)]
# one_way.shape
#
# px.scatter(ch[ch.transit == "one way transit"], x="SPEED", y="WSPD mph", size="Yaw", hover_data=hover_dict, color="vessel class")
#
# px.scatter(ch[ch.transit == "one way transit"], x="WSPD mph", y="Yaw", hover_data=hover_dict, color="SPEED")
# px.scatter(ch[ch.transit == "two way transit"], x="WSPD mph", y="Yaw", hover_data=hover_dict, color="SPEED")
#
# px.scatter(ch[ch.transit == "one way transit"], x="SPEED", y="WSPD mph", color="Yaw", hover_data=hover_dict)
# fig = px.density_contour(ch[ch.transit == "one way transit"][ch[ch.transit == "one way transit"]["WSPD mph"] < 30], x="SPEED", y="WSPD mph")
# fig.update_traces(contours_coloring = "fill", colorscale = "blues")
#
#
# fig1 = px.histogram(ch[ch.transit == "one way transit"], x="SPEED", nbins=20)#, color_discrete_sequence=["teal"])
# fig1.update_layout(xaxis_title_text = "VSPD kn",
#                    yaxis_title_text = "Unique AIS Positions",
#                    title = "One Way Transits Vessel Speed Histogram" "<br>"
#                            "Compliance Rate: " +
#                            str(round(sum(ch[ch.transit == "one way transit"]["SPEED"] <= 10) / ch[ch.transit == "one way transit"].shape[0] * 100, 2)) + "%")
# fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig1.add_shape(type="line", x0=ch[ch.transit == "one way transit"].SPEED.mean(), y0=0, x1=ch[ch.transit == "one way transit"].SPEED.mean(), y1=1,
#                xref="x", yref="paper",
#                line=dict(color="black", dash="solid", width=1.5), name="test")
# fig1.data[0].marker.line.width = 0.75
# fig1.data[0].marker.line.color = "black"
# fig1.add_vline(x=10, annotation_text="Regulatory Speed", annotation_font_size=10, annotation_font_color="red")
# fig1.add_vline(x=ch[ch.transit == "one way transit"]["SPEED"].mean(), annotation_text="Mean Vessel Speed", annotation_font_size=10, annotation_font_color="black")
#
# px.scatter(ch[ch.transit == "two way transit"], x="SPEED", y="WSPD mph", hover_data=hover_dict)
# fig = px.density_contour(ch[ch.transit == "two way transit"], x="SPEED", y="WSPD mph")
# fig.update_traces(contours_coloring = "fill", colorscale = "blues")
#
# fig1 = px.histogram(ch_two_way, x="SPEED", nbins=20)#, color_discrete_sequence=["teal"])
# fig1.update_layout(xaxis_title_text = "VSPD kn",
#                    yaxis_title_text = "Unique AIS Positions",
#                    title = "Two Way Transits Vessel Speed Histogram" "<br>"
#                            "Compliance Rate: " +
#                            str(round(sum(ch_two_way["SPEED"] <= 10) / ch_two_way.shape[0] * 100, 2)) + "%")
# fig1.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
#                 line=dict(color="Red", dash="solid", width=1.5), name="test")
# fig1.add_shape(type="line", x0=ch_two_way.SPEED.mean(), y0=0, x1=ch_two_way.SPEED.mean(), y1=1,
#                xref="x", yref="paper",
#                line=dict(color="black", dash="solid", width=1.5), name="test")
# fig1.data[0].marker.line.width = 0.75
# fig1.data[0].marker.line.color = "black"
# fig1.add_vline(x=10, annotation_text="Regulatory Speed", annotation_font_size=10, annotation_font_color="red")
# fig1.add_vline(x=ch_two_way["SPEED"].mean(), annotation_text="Mean Vessel Speed", annotation_font_size=10, annotation_font_color="black")
#
#
# # for some reason the dates are out of order, i suspect might contribute to long
# # and inefficient run times... look into this and fix ?
# # count number of post-panamax meetpass instances along with total number of instances
# # calculate percentage of transits that are meeting and passing
# # graph....
#
# mp = ch[(ch["MMSI"] == 255805942) | (ch["MMSI"] == 440176000) &
#    (ch["Date/Time UTC"] >= "2020-11-18 14:40:00") &
#    (ch["Date/Time UTC"] <= "2020-11-18 15:30:00")]
# # mp_plot = px.line(mp, x="Date/Time UTC", y="SPEED", color="course behavior", hover_data=hover_dict)
# # mp_plot.update_layout(hoverlabel=dict(bgcolor="White", font_size=13, font_family="sans-serif"))
# # px.line(mp, x="Date/Time UTC", y="Yaw", color="course behavior", hover_name="Name")
# # px.line(mp, x="Date/Time UTC", y="GST mph", color="course behavior", hover_name="Name")
#
#
# ####### Yaw algorithm...
# px.violin(ch[ch.COURSE > 200][["COURSE", "HEADING"]])
# px.violin(ch[ch.COURSE < 200][["COURSE", "HEADING"]])
#
# px.histogram(sv[sv.COURSE > 200][["COURSE", "HEADING"]])
# px.histogram(sv[sv.COURSE < 200][["COURSE", "HEADING"]])
#
# for ship in sv[(sv.COURSE > 200) & (sv.Yaw >= 9)].MMSI.unique():
#     t1 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.HEADING > 200)].reset_index()["Date/Time UTC"],
#                     y=sv[(sv.MMSI == ship) & (sv.HEADING > 200)].HEADING, mode="lines+markers", name="Heading")
#     t2 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.COURSE > 200)].reset_index()["Date/Time UTC"],
#                     y=sv[(sv.MMSI == ship) & (sv.COURSE > 200)].COURSE, mode="lines+markers", name="COURSE")
#     data = [t1, t2]
#     fig = go.Figure(data=data)#, layout=layout)
#     fig.update_layout(title="Savannah " + str(ship) + " Inbound Course and Heading")
#     fig.show()
#
# for ship in sv[(sv.COURSE < 200) & (sv.Yaw >= 8)].MMSI.unique():
#     t1 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.HEADING < 200)].reset_index()["Date/Time UTC"],
#                     y=sv[(sv.MMSI == ship) & (sv.HEADING < 200)].HEADING, mode="lines+markers", name="Heading")
#     t2 = go.Scatter(x=sv[(sv.MMSI == ship) & (sv.COURSE < 200)].reset_index()["Date/Time UTC"],
#                     y=sv[(sv.MMSI == ship) & (sv.COURSE < 200)].COURSE, mode="lines+markers", name="COURSE")
#     data = [t1, t2]
#     fig = go.Figure(data=data)#, layout=layout)
#     fig.update_layout(title="Savannah " + str(ship) + " Outbound Course and Heading")
#     fig.show()
#
#
# # charleston outbound high yaw ships in pilot staging area
# df1 = ch[(ch.MMSI.isin(ch[(ch.COURSE < 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique())) &
#     (ch.COURSE < 200) &
#     (ch.Longitude >= -79.692)]
# # charleston inbound high yaw ships in pilot staging area
# df2 = ch[(ch.MMSI.isin(ch[(ch.COURSE > 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique())) &
#     (ch.COURSE > 200) &
#     (ch.Longitude >= -79.692)]
#
# for ship in ch[(ch.COURSE > 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique():
#     t1 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.HEADING > 200)].reset_index()["Date/Time UTC"],
#                     y=ch[(ch.MMSI == ship) & (ch.HEADING > 200)].HEADING, mode="lines+markers", name="Heading")
#     t2 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE > 200)].reset_index()["Date/Time UTC"],
#                     y=ch[(ch.MMSI == ship) & (ch.COURSE > 200)].COURSE, mode="lines+markers", name="COURSE")
#     data = [t1, t2]
#     fig = go.Figure(data=data)#, layout=layout)
#     fig.update_layout(title="Charleston " + str(ship) + " Inbound Course and Heading")
#     fig.show()
#
# for ship in ch[(ch.COURSE < 200) & (ch.Longitude >= -79.692) & (ch.Yaw >= 6)].MMSI.unique():
#     t1 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].reset_index()["Date/Time UTC"],
#                     y=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].HEADING, mode="lines+markers", name="Heading")
#     t2 = go.Scatter(x=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].reset_index()["Date/Time UTC"],
#                     y=ch[(ch.MMSI == ship) & (ch.COURSE < 200)].COURSE, mode="lines+markers", name="COURSE")
#     data = [t1, t2]
#     fig = go.Figure(data=data)#, layout=layout)
#     fig.update_layout(title="Charleston " + str(ship) + ": Outbound Course and Heading")
#     fig.show()
#
# px.scatter(ch, x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
# px.scatter(ch[ch.Yaw >= 8], x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
# px.scatter(ch[ch.Longitude >= -79.692], x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
#
#
# px.scatter(sv, x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
# px.scatter(sv[sv.Yaw >= 6], x="Longitude", y="Latitude", color="Yaw", hover_data=hover_dict)
