# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)

from import_vessel_data import *

import os
import glob

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# def generate_plots(map_data, zoom, heatmap_enabled, token):
def generate_plots(map_data, zoom, token):
    fig = px.scatter_mapbox(map_data, hover_name="Name",
                            lat="Latitude", lon="Longitude",
                            hover_data=["Date/Time UTC", "COURSE",
                            "Max speed kn", "Mean speed kn", "LOA ft"],
                            color_discrete_sequence=["white"],
                            zoom=zoom, height=600)
    # fig = None
    # if not heatmap_enabled:
    #     fig = px.scatter_mapbox(map_data, hover_name="Name",
    #                             lat="Latitude", lon="Longitude",
    #                             hover_data=["Date/Time UTC", "COURSE",
    #                             "Max speed kn", "Mean speed kn", "LOA ft"],
    #                             color_discrete_sequence=["white"],
    #                             zoom=zoom, height=600)
    # else:
    #     fig = px.density_mapbox(map_data, hover_name="Name",
    #                      z="Mean speed kn", radius=5,
    #                      lat="Latitude", lon="Longitude",
    #                      hover_data=["Date/Time UTC", "COURSE",
    #                      "Max speed kn", "Mean speed kn", "LOA ft"],
    #                      zoom=zoom, height=600)
    fig.update_layout(
        mapbox_accesstoken=token,
        mapbox_style="satellite-streets",
        showlegend=False
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
