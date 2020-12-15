# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)

# from import_maritime_data import *

import plotly.graph_objects as go
import plotly.express as px
# import pandas as pd

def generate_geo_plot(df, zoom, size, heatmap_enabled, token):
    fig = None
    if not heatmap_enabled:
        fig = px.scatter_mapbox(df, hover_name="Name",
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "Course Behavior",
                                "Max Speed kn", "Mean Speed kn", "WSPD mph", "LOA ft"],
                                color_discrete_sequence=["white"],
                                zoom=zoom, height=size[0], width=size[1])
        fig.update_traces(marker_size=4)
    else:
        fig = px.density_mapbox(df, hover_name="Name",
                                z="Max Speed kn", radius=5,
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "Course Behavior",
                                "Max Speed kn", "Mean Speed kn", "WSPD mph", "LOA ft"],
                                zoom=zoom, height=size[0], width=size[1])
    fig.update_layout(
        mapbox_accesstoken=token,
        mapbox_style="satellite-streets",
        showlegend=False
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def generate_vspd_hist(df):
    # fig = None
    # print(df)
    fig = px.histogram(df, x="VSPD kn", color="Transit", nbins=20, color_discrete_sequence=["darkslateblue", "salmon"])
    fig.update_layout(barmode="overlay",
                       xaxis_title_text = "VSPD kn",
                       yaxis_title_text = "Unique AIS Positions",
                       title = "Compliance Rate: " + str(round(sum(df["VSPD kn"] <= 10) / df.shape[0] * 100, 2)) + "%" "<br>"
                               "Mean VSPD: " + str(round(df["VSPD kn"].mean(), 2)) + " kn",
                       showlegend = True, hoverlabel=dict(bgcolor="white",
                                         font_size=13),
                       legend_title_text="",
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=11))
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                    line=dict(color="Red", dash="solid", width=1.5), name="test")
    fig.add_shape(type="line", x0=df["VSPD kn"].mean(), y0=0, x1=df["VSPD kn"].mean(), y1=1,
                   xref="x", yref="paper",
                   line=dict(color="black", dash="dash", width=1.5), name="test")
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                        xref="x", x=10.15, yref="paper", y=1)
    fig.add_annotation(text="Mean", showarrow=False, textangle=90, font=dict(color="black"),
                        xref="x", x=df["VSPD kn"].mean()+0.15, yref="paper", y=1,
                        hovertext=str(round(df["VSPD kn"].mean(), 2)))
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    fig.data[1].marker.line.width = 0.5
    fig.data[1].marker.line.color = "black"
    return fig

def generate_wspd_hist(df, df_dropna):
    fig = px.histogram(df_dropna["WSPD mph"], color_discrete_sequence=["lightsteelblue"], nbins=15)
    fig.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                            x0=30, y0=0, x1=30, y1=1, line={"dash": "solid", "width":1.5}))
    fig.update_layout(title="Adverse Wind Conditions: " + str(round((df_dropna[df_dropna["WSPD mph"] >= 30].shape[0] / df_dropna.shape[0]) * 100, 2)) + "% ",
                      xaxis_title_text="WSPD mph", yaxis_title_text="Unique AIS Positions",
                      showlegend = False, hoverlabel=dict(bgcolor="white",
                                        font_size=13),
                                        plot_bgcolor="#F1F1F1",
                                        font=dict(size=11))
    fig.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=90, font=dict(color="black"),
                        xref="x", x=30.4, yref="paper", y=1)
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    return fig

def generate_wspd_vs_vspd(df):
    fig = None
    return fig

def generate_strip_plot(df):
    fig = None
    hover_dict = {"Date/Time UTC":True, "MMSI":False, "VSPD kn":True, "WSPD mph":True, "Course Behavior":True,
                  "Yaw":True, "LOA ft":False, "Beam ft":False, "Effective Beam ft":True,
                  "Location":False, "Name":False}
    return fig

def generate_line_plot(df):
    fig = None
    return fig

def generate_channel_occ(df):
    fig = None
    return fig
