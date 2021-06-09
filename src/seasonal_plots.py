# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Generate seasonal plots and figures for the 2020-2021 SMA.

import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

ch = pd.read_csv("../html/riwhale.github.io/master-ch.csv")
ch_max = pd.read_csv("../html/riwhale.github.io/master-ch-max.csv")
sv = pd.read_csv("../html/riwhale.github.io/master-sv.csv")
sv_max = pd.read_csv("../html/riwhale.github.io/master-sv-max.csv")

def _write_html(fig, filename):
    return pio.write_html(fig, file=filename, auto_open=False)

def _write_image(fig, filename, format, scale):
    return pio.write_image(fig, file=filename, format=format, engine="kaleido",
                           scale=scale)

def generate_ticker(ch, sv):
    """Generates seasonal ticker for port compliance and mean vessel speed."""
    fig = None
    fig = go.Figure(data=[go.Table(
        header=dict(values=[""],
                    line_color="white",
                    fill_color="#FFFFFF",
                    height=0),
        cells=dict(values=[["<b>Charleston:</b> " +
                            str(round(sum(ch.loc[:, "VSPD kn"] <= 10) /
                            len(ch) * 100, 2)) + "% Compliance, " +
                            str(round(ch.loc[:, "VSPD kn"].mean(), 2)) +
                            " kn Mean VSPD",
                            "<b>Savannah:</b>  " +
                            str(round(sum(sv.loc[:, "VSPD kn"] <= 10) /
                            len(sv) * 100, 2)) + "% Compliance, " +
                            str(round(sv.loc[:, "VSPD kn"].mean(), 2)) +
                            " kn Mean VSPD"]],
                   line_color="white", fill_color="#FFFFFF", align="left",
                   font_size=14, height=0))
                   ])
    fig.update_layout(height=75, width=470, margin=dict(l=0, r=0, t=0, b=0))
    return fig

_write_image(generate_ticker(ch.dropna(), sv.dropna()),
             "../html/seasonal_ticker.png", "png", 5)

def generate_vspd_hist(df):
    """Generates vessel speed histogram."""
    fig = px.histogram(df, x="VSPD kn", nbins=20,
                       color_discrete_sequence=["#19336A"])
    fig.update_layout(xaxis_title_text = "VSPD kn",
                       yaxis_title_text = "Unique AIS Positions",
                       title = "<b>Vessel Speed Histogram</b><br>" +
                               "Compliance Rate: " +
                               str(round(sum(df.loc[:, "VSPD kn"] <= 10) /
                               df.shape[0] * 100, 2)) + "%<br>Mean VSPD: " +
                               str(round(df.loc[:, "VSPD kn"].mean(), 2)) +
                               " kn",
                       showlegend = True, hoverlabel=dict(bgcolor="white",
                                                          font_size=13),
                       legend_title_text="", width=875, height=600,
                       plot_bgcolor="#F1F1F1", font=dict(size=12),
                       titlefont=dict(size=14),
                       margin=dict(l=80, r=80, t=90, b=20))
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90,
                       font=dict(color="red"), xref="x", x=10.2, yref="paper",
                       y=1, hovertext="10 kn")
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    return fig

generate_vspd_hist(ch.dropna())

_write_html(generate_vspd_hist(ch.dropna()),
            "../html/seasonal_vspd_hist_ch.html")

def generate_vspd_hist(df):
    """Generates vessel speed histogram."""
    fig = px.histogram(df, x="VSPD kn", nbins=20,
                       color_discrete_sequence=["#19336A"])
    fig.update_layout(xaxis_title_text = "VSPD kn",
                       yaxis_title_text = "Unique AIS Positions",
                       title = "<b>Vessel Speed Histogram</b><br>" +
                               "Compliance Rate: " +
                               str(round(sum(df.loc[:, "VSPD kn"] <= 10) /
                               df.shape[0] * 100, 2)) + "%<br>Mean VSPD: " +
                               str(round(df.loc[:, "VSPD kn"].mean(), 2)) +
                               " kn",
                       showlegend = True, hoverlabel=dict(bgcolor="white",
                                                          font_size=13),
                       legend_title_text="", width=875, height=600,
                       plot_bgcolor="#F1F1F1", font=dict(size=12),
                       titlefont=dict(size=14),
                       margin=dict(l=80, r=80, t=90, b=20))
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90,
                       font=dict(color="red"), xref="x", x=10.15, yref="paper",
                       y=1, hovertext="10 kn")
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    return fig
generate_vspd_hist(sv.dropna())

_write_html(generate_vspd_hist(sv.dropna()),
            "../html/seasonal_vspd_hist_sv.html")

def generate_strip_plot(df):
    """Generates vessel strip plot."""
    hover_dict = {"VSPD kn":True, "WSPD mph":True, "Transit":True,
                  "% Channel Occupied":True, "Class":True,
                  "Course Behavior":True, "Yaw deg":True, "LOA ft":True,
                  "Beam ft":True, "Effective Beam ft":True, "Location":True,
                  "Date/Time UTC":True, "Name":False}
    fig = px.strip(df, x="Name", y="VSPD kn", color="Transit",
                   hover_data=hover_dict, hover_name="Name",
                   stripmode="overlay",
                   color_discrete_sequence=["#19336A", "green"],
                   width=900, height=600,
                   title= "<b>Vessel Speed Plot</b><br>" +
                           "One-way Transits: " +
                           str(round((df[df.loc[:,
                           ("Transit")] == "One-way Transit"]
                           .shape[0] / df.shape[0]) * 100, 2)) + "%<br>" +
                           "Two-way Transits: " +
                           str(round((df[df.loc[:,
                           ("Transit")] == "Two-way Transit"]
                           .shape[0] / df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.update_layout(xaxis_title_text = "Vessels",
                      hoverlabel=dict(bgcolor="white", font_size=13),
                      legend_title_text="", width=900, height=650,
                      plot_bgcolor="#F1F1F1", font=dict(size=12),
                      titlefont=dict(size=14))
    fig.update_traces(marker_size=4)
    fig.update_xaxes(showticklabels=False)
    fig.add_annotation(text="Speed Limit", showarrow=False,
                       font=dict(color="red", size=15), yref="y", y=10.3, xref="paper",
                       x=0.86, hovertext="10 kn")
    return fig

generate_strip_plot(ch.dropna())

_write_html(generate_strip_plot(ch.dropna()),
            "../html/seasonal_vspd_strip_ch.html")

def generate_strip_plot(df):
    """Generates vessel strip plot."""
    hover_dict = {"VSPD kn":True, "WSPD mph":True, "Transit":True,
                  "% Channel Occupied":True, "Class":True,
                  "Course Behavior":True, "Yaw deg":True, "LOA ft":True,
                  "Beam ft":True, "Effective Beam ft":True, "Location":True,
                  "Date/Time UTC":True, "Name":False}
    fig = px.strip(df, x="Name", y="VSPD kn", color="Transit",
                   hover_data=hover_dict, hover_name="Name",
                   stripmode="overlay",
                   color_discrete_sequence=["#19336A", "green"],
                   width=900, height=600,
                   title= "<b>Vessel Speed Plot</b><br>" +
                           "One-way Transits: " +
                           str(round((df[df.loc[:,
                           ("Transit")] == "One-way Transit"]
                           .shape[0] / df.shape[0]) * 100, 2)) + "%<br>" +
                           "Two-way Transits: " +
                           str(round((df[df.loc[:,
                           ("Transit")] == "Two-way Transit"]
                           .shape[0] / df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.update_layout(xaxis_title_text = "Vessels",
                      hoverlabel=dict(bgcolor="white", font_size=13),
                      legend_title_text="", width=900, height=650,
                      plot_bgcolor="#F1F1F1", font=dict(size=12),
                      titlefont=dict(size=14))
    fig.update_traces(marker_size=4)
    fig.update_xaxes(showticklabels=False)
    fig.add_annotation(text="Speed Limit", showarrow=False,
                       font=dict(color="red", size=15), yref="y", y=10.3, xref="paper",
                       x=0.985, hovertext="10 kn")
    return fig

generate_strip_plot(sv.dropna())

_write_html(generate_strip_plot(sv.dropna()),
            "../html/seasonal_vspd_strip_sv.html")

def generate_channel_occ(df):
    """Generates channel occupancy and vessel speed scatter plot."""
    hover_dict = {"VSPD kn":True, "WSPD mph":True, "Transit":True,
                  "Class":True, "Course Behavior":True, "Yaw deg":True,
                  "LOA ft":True, "Beam ft":True, "Effective Beam ft":True,
                  "Location":True, "Name":False, "Date/Time UTC":True}
    fig = px.scatter(df, x="VSPD kn", y="% Channel Occupied", color="Transit",
                     color_discrete_sequence=["#19336A", "green"],
                     hover_data=hover_dict, hover_name="Name",
                     title="<b>Vessel Speed and Occupied Channel</b><br>" +
                     "One-way Transits: " +
                     str(round((df[df.loc[:,
                     ("Transit")] == "One-way Transit"].shape[0] /
                     df.shape[0]) * 100, 2)) + "%<br>" +
                     "Two-way Transits: " +
                     str(round((df[df.loc[:,
                     ("Transit")] == "Two-way Transit"].shape[0] /
                     df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90,
                       font=dict(color="red", size=13), xref="x", x=10.3, yref="paper",
                       y=1, hovertext="10 kn")
    fig.update_layout(hoverlabel=dict(bgcolor="white", font_size=13),
                      legend_title_text="", width=875, height=650,
                      plot_bgcolor="#F1F1F1", font=dict(size=12),
                      titlefont=dict(size=14))
    fig.update_traces(marker_size=6)
    return fig

generate_channel_occ(ch.dropna())

_write_html(generate_channel_occ(ch.dropna()),
            "../html/seasonal_channel_occupation_ch.html")

generate_channel_occ(sv.dropna())
_write_html(generate_channel_occ(sv.dropna()),
            "../html/seasonal_channel_occupation_sv.html")

def _check_wind_outages(df, df_dropna):
    """Checks for major wind outages on a given day."""
    if 1 - len(df_dropna) / len(df) >= OUTAGE_THRESHOLD:
        return True
    return False

def generate_wspd_hist(df, df_dropna):
    """Generates windspeed histogram."""
    fig = None
    if not _check_wind_outages(df, df_dropna):
        # fig = px.histogram(df_dropna, x="WSPD mph", color="Buoy Source", nbins=15)
        fig = px.histogram(df_dropna.loc[:, "WSPD mph"],
                           color_discrete_sequence=["steelblue"], nbins=20)
        fig.update_layout(title="<b>Windspeed Histogram</b><br>" +
                                "Adverse Wind Conditions: " +
                                str(round((df_dropna[df_dropna.loc[:,
                                ("WSPD mph")] >= 30].shape[0] /
                                df_dropna.shape[0]) * 100, 2)) + "%",
                                xaxis_title_text="WSPD mph",
                                yaxis_title_text="Unique AIS Positions",
                                showlegend=False,
                                hoverlabel=dict(bgcolor="white",font_size=13),
                                width=875, height=600, plot_bgcolor="#F1F1F1",
                                font=dict(size=12), titlefont=dict(size=14),
                                margin=dict(t=100))
        fig.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                                      x0=30, y0=0, x1=30, y1=1,
                                      line={"dash": "solid", "width":1.5}))
        fig.add_annotation(text="Adverse WSPD Threshold", showarrow=False,
                           textangle=90, font=dict(color="black"),
                           xref="x", x=30.4, yref="paper", y=1)
        fig.data[0].marker.line.width = 0.5
        fig.data[0].marker.line.color = "black"
    else:
        fig = px.histogram(pd.DataFrame({"WSPD mph":[]}), x="WSPD mph")
        fig.add_annotation(text="Major Wind Outage<br>" +
                                str(round(100 - len(df_dropna) /
                                len(df) * 100, 2)) + "% of Data Missing",
                           showarrow=False, textangle=0,
                           font=dict(color="black", size=20),
                           xref="paper", x=0.5, yref="paper", y=0.5)
        fig.update_layout(title="<b>Windspeed Histogram</b>",
                          yaxis_title_text="Unique AIS Positions",
                          width=875, height=600, plot_bgcolor="#F1F1F1",
                          font=dict(size=12), titlefont=dict(size=14))
    return fig
generate_wspd_hist(ch, ch.dropna())
_write_html(generate_wspd_hist(ch, ch.dropna()),
            "../html/seasonal_wspd_hist_ch.html")

generate_wspd_hist(sv, sv.dropna())

_write_html(generate_wspd_hist(sv, sv.dropna()),
            "../html/seasonal_wspd_hist_sv.html")

def generate_wspd_vs_vspd(df, df_dropna):
    """Generates vessel speed and wind speed density plot."""
    fig = None
    if not _check_wind_outages(df, df_dropna):
        fig = px.density_contour(df_dropna, x="VSPD kn", y="WSPD mph")
        fig.update_traces(contours_coloring="fill", colorscale="blues")
        fig.update_layout(xaxis_title_text="VSPD kn",
                          title="<b>Vessel and Wind Speed Density Plot</b>" +
                                "<br>" +
                                 "VSPD-WSPD Correlation: " +
                                 str(round(df_dropna.loc[:,
                                 ("VSPD kn", "WSPD mph")]
                                 .corr().iloc[0][1], 2)),
                          hoverlabel=dict(bgcolor="white", font_size=13),
                          width=875, height=600, plot_bgcolor="#F1F1F1",
                          font=dict(size=12), titlefont=dict(size=14),
                          margin=dict(t=100))
        fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x",
                      yref="paper", line=dict(color="red", dash="solid",
                      width=1.5))
        fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90,
                           font=dict(color="red"), xref="x", x=10.2,
                           yref="paper", y=1, hovertext="10 kn")
    else:
        fig = px.density_contour(pd.DataFrame({"WSPD mph":[], "VSPD kn":[]}),
                                 x="VSPD kn", y="WSPD mph")
        fig.add_annotation(text="Major Wind Outage<br>" +
                           str(round(100 - len(df_dropna) / len(df) * 100, 2)) +
                           "% of Data Missing", showarrow=False, textangle=0,
                           font=dict(color="black", size=20), xref="paper",
                           x=0.5, yref="paper", y=0.5)
        fig.update_layout(title="<b>Vessel and Wind Speed Density Plot</b>",
                          width=875, height=600, plot_bgcolor="#F1F1F1",
                          font=dict(size=12), titlefont=dict(size=14))
    return fig

generate_wspd_vs_vspd(ch, ch.dropna())

_write_html(generate_wspd_vs_vspd(ch, ch.dropna()),
            "../html/seasonal_wspd_vs_vspd_ch.html")

def generate_wspd_vs_vspd(df, df_dropna):
    """Generates vessel speed and wind speed density plot."""
    fig = None
    if not _check_wind_outages(df, df_dropna):
        fig = px.density_contour(df_dropna, x="VSPD kn", y="WSPD mph")
        fig.update_traces(contours_coloring="fill", colorscale="blues")
        fig.update_layout(xaxis_title_text="VSPD kn",
                          title="<b>Vessel and Wind Speed Density Plot</b>" +
                                "<br>" +
                                 "VSPD-WSPD Correlation: " +
                                 str(round(df_dropna.loc[:,
                                 ("VSPD kn", "WSPD mph")]
                                 .corr().iloc[0][1], 2)),
                          hoverlabel=dict(bgcolor="white", font_size=13),
                          width=875, height=600, plot_bgcolor="#F1F1F1",
                          font=dict(size=12), titlefont=dict(size=14),
                          margin=dict(t=100))
        fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x",
                      yref="paper", line=dict(color="red", dash="solid",
                      width=1.5))
        fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90,
                           font=dict(color="red"), xref="x", x=10.16,
                           yref="paper", y=1, hovertext="10 kn")
    else:
        fig = px.density_contour(pd.DataFrame({"WSPD mph":[], "VSPD kn":[]}),
                                 x="VSPD kn", y="WSPD mph")
        fig.add_annotation(text="Major Wind Outage<br>" +
                           str(round(100 - len(df_dropna) / len(df) * 100, 2)) +
                           "% of Data Missing", showarrow=False, textangle=0,
                           font=dict(color="black", size=20), xref="paper",
                           x=0.5, yref="paper", y=0.5)
        fig.update_layout(title="<b>Vessel and Wind Speed Density Plot</b>",
                          width=875, height=600, plot_bgcolor="#F1F1F1",
                          font=dict(size=12), titlefont=dict(size=14))
    return fig
generate_wspd_vs_vspd(sv, sv.dropna())
_write_html(generate_wspd_vs_vspd(sv, sv.dropna()),
            "../html/seasonal_wspd_vs_vspd_sv.html")

def generate_line_plot(df):
    """Generates vessel speed and yaw line plot."""
    t1 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn").loc[:, "VSPD kn"],
                    mode="lines", name="VSPD kn", line=dict(width=1.5,
                    color="#19336A"), hoverinfo="skip")
    t2 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn").loc[:, "Yaw deg"],
                    mode="lines", name="Yaw deg",
                    line=dict(width=1.5, color="green"), hoverinfo="skip")
    fig = go.Figure(data=[t1, t2])
    fig.update_layout(title="<b>Vessel Speed and Yaw Line Plot</b><br>" +
                             "VSPD-Yaw Correlation: " +
                             str(round(df.dropna().loc[:,
                             ("VSPD kn", "Yaw deg")].corr().iloc[0][1], 2)) +
                             "<br>" + "Compliant VSPD mean Yaw: " +
                             str(round(df[df.loc[:, "VSPD kn"] <= 10].loc[:,
                             "Yaw deg"].mean(), 2)) + " deg" + "<br>" +
                             "Non-compliant VSPD mean Yaw:  " +
                             str(round(df[df.loc[:, "VSPD kn"] > 10].loc[:,
                             "Yaw deg"].mean(), 2)) + " deg",
                      xaxis_title_text="AIS Positions",
                      yaxis_title_text="Degrees and Knots", width=875,
                      height=600, plot_bgcolor="#F1F1F1", font=dict(size=12),
                      titlefont=dict(size=14),
                      margin=dict(l=80, r=20, t=120, b=20))
    fig.update_xaxes(showticklabels=False)
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False,
                       font=dict(color="red", size=13), yref="y", y=10.43, xref="paper",
                       x=0.915, hovertext="10 kn")
    return fig

generate_line_plot(ch.dropna().reset_index())

_write_html(generate_line_plot(ch.dropna().reset_index()),
            "../html/seasonal_line_ch.html")

def generate_line_plot(df):
    """Generates vessel speed and yaw line plot."""
    t1 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn").loc[:, "VSPD kn"],
                    mode="lines", name="VSPD kn", line=dict(width=1.5,
                    color="#19336A"), hoverinfo="skip")
    t2 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn").loc[:, "Yaw deg"],
                    mode="lines", name="Yaw deg",
                    line=dict(width=1.5, color="green"), hoverinfo="skip")
    fig = go.Figure(data=[t1, t2])
    fig.update_layout(title="<b>Vessel Speed and Yaw Line Plot</b><br>" +
                             "VSPD-Yaw Correlation: " +
                             str(round(df.dropna().loc[:,
                             ("VSPD kn", "Yaw deg")].corr().iloc[0][1], 2)) +
                             "<br>" + "Compliant VSPD mean Yaw: " +
                             str(round(df[df.loc[:, "VSPD kn"] <= 10].loc[:,
                             "Yaw deg"].mean(), 2)) + " deg" + "<br>" +
                             "Non-compliant VSPD mean Yaw:  " +
                             str(round(df[df.loc[:, "VSPD kn"] > 10].loc[:,
                             "Yaw deg"].mean(), 2)) + " deg",
                      xaxis_title_text="AIS Positions",
                      yaxis_title_text="Degrees and Knots", width=875,
                      height=600, plot_bgcolor="#F1F1F1", font=dict(size=12),
                      titlefont=dict(size=14),
                      margin=dict(l=80, r=20, t=120, b=20))
    fig.update_xaxes(showticklabels=False)
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                  line=dict(color="red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False,
                       font=dict(color="red", size=13), yref="y", y=10.43, xref="paper",
                       x=0.07, hovertext="10 kn")
    return fig
generate_line_plot(sv.dropna().reset_index())

_write_html(generate_line_plot(sv.dropna().reset_index()),
            "../html/seasonal_line_sv.html")

def generate_geo_plot(df, zoom, center, size, opacity, hover, token):
    """Generates geo plot using Mapbox token."""
    fig = None
    fig = px.scatter_mapbox(df, hover_name="Name",
                            lat="Latitude", lon="Longitude",
                            hover_data=hover,
                            color="Max Speed kn",
                            range_color=[8, 22],
                            color_continuous_scale="ylorrd",
                            zoom=zoom, height=size[0], width=size[1])
    fig.update_traces(marker_size=5, marker_opacity=opacity)
    fig.update_layout(mapbox_accesstoken=token,
                      mapbox_style="satellite-streets", showlegend=False)
    if center:
        fig.update_layout(mapbox_center=center)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

token = open("../conf/.mapbox_token").read()
hover = ["Date/Time UTC", "Course Behavior", "Max Speed kn",
         "Mean Speed kn", "WSPD mph", "Buoy Source", "Transit",
         "Class", "LOA ft", "Beam ft", "Yaw deg",
         "Effective Beam ft", "% Channel Occupied", "Location"]

_write_html(generate_geo_plot(ch_max.dropna(), 8.5, dict(lat=32.68376,
                                                         lon=-79.72794),
                             [431, 819], 0.75, hover, token),
            "../html/seasonal_charleston.html")

_write_html(generate_geo_plot(sv_max.dropna(), 9.25, dict(lat=31.99753,
           lon=-80.78728), [431, 819], 0.75, hover, token),
            "../html/seasonal_savannah.html")

_write_html(generate_geo_plot(pd.concat([ch_max, sv_max]).dropna(), 7, dict(),
            [431, 819], 0.6, hover, token),
            "../html/level_one.html")

fig = sns.kdeplot(data=ch.dropna(), x="VSPD kn", y="WSPD mph", fill=True, cmap="mako_r")
plt.title("Vessel and Wind Speed Density Plot\n" +
       "VSPD-WSPD Correlation: " +
       str(round(ch.dropna().loc[:, ("VSPD kn", "WSPD mph")].corr().iloc[0][1], 2)))
plt.axvline(10,0,1, c="red")
plt.show()
