# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)
from util import *

import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def check_wind_outages(df, df_dropna):
    if 1 - len(df_dropna) / len(df) >= OUTAGE_THRESHOLD:
        return True
    return False

def generate_geo_plot(df, zoom, center, size, opacity, hover, token):
    fig = None
    # if not heatmap_enabled:
        # fig = px.scatter_mapbox(df, hover_name="Name",
        #                         lat="Latitude", lon="Longitude",
        #                         hover_data=hover,
        #                         color_discrete_sequence=["white"],
        #                         zoom=zoom, height=size[0], width=size[1])
        # fig.update_traces(marker_size=4)
    # else:
    fig = px.scatter_mapbox(df, hover_name="Name",
                            lat="Latitude", lon="Longitude",
                            hover_data=hover,
                            color="Max Speed kn",
                            range_color=[8, 22],
                            color_continuous_scale="ylorrd_r",
                            zoom=zoom, height=size[0], width=size[1])
    fig.update_traces(marker_size=5, marker_opacity=opacity) # marker_cmin=10.0, marker_cmid=15.0, marker_cmax=20.0
    # fig = px.density_mapbox(df, hover_name="Name",
    #                         z="Max Speed kn", radius=5,
    #                         lat="Latitude", lon="Longitude",
    #                         hover_data=hover,
    #                         zoom=zoom, height=size[0], width=size[1])
    # fig.update_coloraxes(colorscale="ylorrd_r")
    fig.update_layout(mapbox_accesstoken=token,
                      mapbox_style="satellite-streets", showlegend=False)
    if center:
        fig.update_layout(mapbox_center=center)
    # if not show_scale:
    #     fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def generate_table(ch, sv):
    fig = None
    fig = go.Figure(data=[go.Table(
        header=dict(values=["<b>Port</b>", "<b>Compliance Rate</b>", "<b>Mean VSPD</b>"],
                    line_color="white",
                    fill_color="#ffffff",
                    align="left",
                    font_color="black",
                    font_size=12,
                    height=10),
        cells=dict(values=[["Charleston", "Savannah"],
                           [str(round(sum(ch["VSPD kn"] <= 10) / len(ch) * 100, 2)) + "%",
                            str(round(sum(sv["VSPD kn"] <= 10) / len(sv) * 100, 2)) + "%"],
                            [str(round(ch["VSPD kn"].mean(), 2)) + " kn",
                             str(round(sv["VSPD kn"].mean(), 2)) + " kn"]
                            ],
                   line_color="white",
                   fill_color="#ffffff",
                   align="left",
                   font_color="black",
                   font_size=12,
                   height=20))
    ])

    fig.update_layout(height=75, width=600, margin=dict(l=0, r=0, t=0, b=0))
    return fig

# def generate_table(ch, sv):
#     fig = None
#     data = go.Table(header=dict(fill_color="#ffffff"),
#                     cells=dict(values=[["Charleston:", "Savannah:"],
#                                        [str(round(sum(ch["VSPD kn"] <= 10) / len(ch) * 100, 2)) + "%" + " Compliance Rate, ", str(round(sum(sv["VSPD kn"] <= 10) / len(sv) * 100, 2)) + "%" + " Compliance Rate, "],
#                                        [str(round(ch["VSPD kn"].mean(), 2)) + " kn" + " Mean VSPD", str(round(sv["VSPD kn"].mean(), 2)) + " kn" + " Mean VSPD"]],
#                                fill_color="#ffffff", align='left'))
#     fig = go.Figure([data])
#
#     return fig

def generate_vspd_hist(df):
    fig = px.histogram(df, x="VSPD kn", nbins=20, color_discrete_sequence=["#19336a"])#"darkslateblue", "#ab63eb"])
    fig.update_layout(xaxis_title_text = "VSPD kn",
        #barmode="overlay"
                       yaxis_title_text = "Unique AIS Positions",
                       title = "<b>Vessel Speed Histogram</b>" "<br>"
                               "Compliance Rate: " + str(round(sum(df["VSPD kn"] <= 10) / df.shape[0] * 100, 2)) + "%" "<br>"
                               "Mean VSPD (Panamax and Post Panamax): " + str(round(df["VSPD kn"].mean(), 2)) + " kn",
                       showlegend = True, hoverlabel=dict(bgcolor="white",
                                         font_size=13),
                       legend_title_text="",
                       width=875,
                       height=600,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=14),
                       margin=dict(l=80, r=80, t=90, b=20))
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                    xref="x", x=10.15, yref="paper", y=1, hovertext="10 kn")
    # fig.add_shape(type="line", x0=df["VSPD kn"].mean(), y0=0, x1=df["VSPD kn"].mean(), y1=1,
    #                xref="x", yref="paper",
    #                line=dict(color="black", dash="dash", width=1.5))
    # fig.add_annotation(text="Mean", showarrow=False, textangle=90, font=dict(color="black"),
    #                     xref="x", x=df["VSPD kn"].mean()+0.15, yref="paper", y=1,
    #                     hovertext=str(round(df["VSPD kn"].mean(), 2)) + " kn")
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    # fig.data[1].marker.line.width = 0.5
    # fig.data[1].marker.line.color = "black"
    return fig

def generate_strip_plot(df):
    hover_dict = {"VSPD kn":True, "WSPD mph":True, "Transit":True, "% Channel Occupied":True,
                  "Vessel Class":True, "Course Behavior":True, "Yaw deg":True,
                  "LOA ft":True, "Beam ft":True, "Effective Beam ft":True,
                  "Location":True, "Date/Time UTC":True, "Name":False}
    fig = px.strip(df, x="Name", y="VSPD kn",
                    color="Transit", hover_data=hover_dict, hover_name="Name", stripmode="overlay",
                    color_discrete_sequence=["#19336a", "green"], width=900, height=600, #darkslateblue, salmon
                    title= "<b>Vessel Speed Plot</b>" '<br>'
                           "One-way Transits: " + str(round((df[df.Transit == "One-way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%" "<br>"
                           "Two-way Transits: " + str(round((df[df.Transit == "Two-way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.update_layout(xaxis_title_text = "",
                      hoverlabel=dict(bgcolor="white",
                                        font_size=13),
                      legend_title_text="",
                       width=875,
                       height=650,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=14))
    fig.update_traces(marker_size=4)
    return fig


def generate_wspd_hist(df, df_dropna):
    fig = None
    if not check_wind_outages(df, df_dropna):

        fig = px.histogram(df_dropna["WSPD mph"], color_discrete_sequence=["steelblue"], nbins=15)
        fig.update_layout(title="<b>Windspeed Histogram</b><br>"
                                "Wind Buoy Data Available: " + str(round(len(df.dropna()) / len(df) * 100, 2)) + "%" "<br>"
                                "Adverse Wind Conditions: " + str(round((df_dropna[df_dropna["WSPD mph"] >= 30].shape[0] / df_dropna.shape[0]) * 100, 2)) + "%",
                                xaxis_title_text="WSPD mph", yaxis_title_text="Unique AIS Positions",
                                showlegend = False, hoverlabel = dict(bgcolor="white",font_size=13),
                                width=875,
                                height=600,
                                plot_bgcolor="#F1F1F1",
                                font=dict(size=12),
                                titlefont=dict(size=14),
                                margin=dict(t=100))
        fig.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                                x0=30, y0=0, x1=30, y1=1, line={"dash": "solid", "width":1.5}))
        fig.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=90, font=dict(color="black"),
                        xref="x", x=30.4, yref="paper", y=1)
        fig.data[0].marker.line.width = 0.5
        fig.data[0].marker.line.color = "black"

    else:
        fig = px.histogram(pd.DataFrame({"WSPD mph":[]}), x="WSPD mph")
        fig.add_annotation(text="Major Wind Outage<br>" + str(round(100 - len(df_dropna) / len(df) * 100, 2)) + "% " +
                                "of Data Missing", showarrow=False, textangle=0, font=dict(color="black", size=20),
                        xref="paper", x=0.5, yref="paper", y=0.5)
        fig.update_layout(title="<b>Windspeed Histogram</b>",
                          yaxis_title_text="Unique AIS Positions",
                          width=875,
                          height=600,
                          plot_bgcolor="#F1F1F1",
                          font=dict(size=12),
                          titlefont=dict(size=14))
    return fig


def generate_wspd_vs_vspd(df, df_dropna):
    fig = None
    if not check_wind_outages(df, df_dropna):
        fig = px.density_contour(df_dropna, x="VSPD kn", y="WSPD mph")
        fig.update_traces(contours_coloring = "fill", colorscale = "blues")
        fig.update_layout(xaxis_title_text = "VSPD kn",
                          title= "<b>Vessel and Wind Speed Density Plot</b>" '<br>'
                                 "Wind Buoy Data Available: " + str(round(len(df.dropna()) / len(df) * 100, 2)) + "%" "<br>"
                                 "VSPD-WSPD Correlation: " + str(round(df_dropna[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                           hoverlabel=dict(bgcolor="white", font_size=13),
                           width=875,
                           height=600,
                           plot_bgcolor="#F1F1F1",
                           font=dict(size=12),
                           titlefont=dict(size=14),
                           margin=dict(t=100))
        fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                        line=dict(color="Red", dash="solid", width=1.5))
        fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                        xref="x", x=10.15, yref="paper", y=1, hovertext="10 kn")
        # fig.add_shape(go.layout.Shape(type="line", xref="paper", yref="y",
        #                         x0=0, y0=30, x1=1, y1=30, line={"dash": "solid", "width":1.5}))
        # fig.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=0, font=dict(color="black"),
        #                 xref="paper", x=1, yref="y", y=30.6)
    else:
        fig = px.density_contour(pd.DataFrame({"WSPD mph":[], "VSPD kn":[]}), x="VSPD kn", y="WSPD mph")
        fig.add_annotation(text="Major Wind Outage<br>" + str(round(100 - len(df_dropna) / len(df) * 100, 2)) + "% " +
                                "of Data Missing", showarrow=False, textangle=0, font=dict(color="black", size=20),
                        xref="paper", x=0.5, yref="paper", y=0.5)
        fig.update_layout(title="<b>Vessel and Wind Speed Density Plot</b>",
                          width=875,
                          height=600,
                          plot_bgcolor="#F1F1F1",
                          font=dict(size=12),
                          titlefont=dict(size=14))
    return fig


def generate_line_plot(df):
    t1 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn")["VSPD kn"], mode="lines", name="VSPD kn", line=dict(width=1.5, color="#19336a"), hoverinfo="skip")
    t2 = go.Scatter(x=df.index, y=df.sort_values("VSPD kn")["Yaw deg"], mode="lines", name="Yaw deg", line=dict(width=1.5, color="green"), hoverinfo="skip")
    fig = go.Figure(data=[t1, t2])
    fig.update_layout(title="<b>Vessel Speed and Yaw Line Plot</b>" '<br>'
                             "VSPD-Yaw Correlation: " + str(round(df.dropna()[["VSPD kn", "Yaw deg"]].corr().iloc[0][1], 2)) + "<br>"
                             "Compliant VSPD mean Yaw: " + str(round(df[df["VSPD kn"] <= 10]["Yaw deg"].mean(), 2)) + " deg" + "<br>"
                             "Non-compliant VSPD mean Yaw:  " + str(round(df[df["VSPD kn"] > 10]["Yaw deg"].mean(), 2)) + " deg",
                      xaxis_title_text="AIS Positions",
                      yaxis_title_text="Degrees and Knots",
                      width=875,
                      height=600,
                      plot_bgcolor="#F1F1F1",
                      font=dict(size=12),
                      titlefont=dict(size=14),
                      margin=dict(l=80, r=20, t=120, b=20))
    fig.update_xaxes(showticklabels=False)
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                    line=dict(color="Red", dash="solid", width=1.5))
    return fig

def generate_channel_occ(df):
    hover_dict = {"VSPD kn":True, "WSPD mph":True, "Transit":True, "Vessel Class":True, "Course Behavior":True,
                  "Yaw deg":True, "LOA ft":True, "Beam ft":True, "Effective Beam ft":True,
                  "Location":True, "Name":False, "Date/Time UTC":True}
    fig = px.scatter(df, x="VSPD kn", y="% Channel Occupied", color="Transit", color_discrete_sequence=["#19336a", "green"],
               hover_data=hover_dict, hover_name="Name",
               title="<b>Vessel Speed and Occupied Channel</b>" + "<br>"
                     "One-way Transits: " + str(round((df[df.Transit == "One-way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%" "<br>"
                     "Two-way Transits: " + str(round((df[df.Transit == "Two-way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                    xref="x", x=10.15, yref="paper", y=1, hovertext="10 kn")
    fig.update_layout(hoverlabel=dict(bgcolor="white",
                                        font_size=13),
                      legend_title_text="",
                       width=875,
                       height=650,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=14))
    fig.update_traces(marker_size=6)
    return fig



    # fig = px.scatter(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)], x="VSPD kn", y="% Channel Occupied", hover_data=hover_dict,
    #                          color_discrete_sequence=["darkslateblue", "salmon"], width=800, height=500,
    #                          title="Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    # fig = px.density_contour(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)], x="VSPD kn", y="% Channel Occupied", width=800, height=500, hover_data=hover_dict,
    #                          title= "VSPD-Occupied Channel Desntiy Plot" '<br>'
    #                                 "Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    # df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]
    # fig = px.density_heatmap(df, x="VSPD kn", y="% Channel Occupied",
    #                         hover_data=hover_dict,
    #                         color_continuous_scale="greens",
    #                         nbinsx=20, nbinsy=20, #color_continuous_midpoint=20,
    #                          title= "Vessel Speed and Occupied Channel Heatmap")# '<br>'
                                    #"Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    # fig.update_traces(contours_coloring = "fill", colorscale = "greens")
    # fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=1, xref="x", yref="paper",
    #                 line=dict(color="Red", dash="solid", width=1.5))
    # fig.add_shape(type="line", x0=0, y0=20, x1=1, y1=20, xref="paper", yref="y",
    #                 line=dict(color="black", dash="solid", width=1.5))
    # fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
    #                 line=dict(color="Red", dash="solid", width=1.5))
    # fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
    #                     xref="x", x=10.15, yref="paper", y=1)
    # fig.update_layout(width=875,
    #                   height=600,
    #                   plot_bgcolor="#F1F1F1",
    #                   font=dict(size=12),
    #                   titlefont=dict(size=14))
