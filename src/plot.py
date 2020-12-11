# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)

from import_vessel_data import *

import plotly.express as px
import pandas as pd

def generate_geoplots(map_data, zoom, size, heatmap_enabled, token):
    fig = None
    if not heatmap_enabled:
        fig = px.scatter_mapbox(map_data, hover_name="Name",
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "COURSE",
                                "Max speed kn", "Mean speed kn", "LOA ft"],
                                color_discrete_sequence=["white"],
                                zoom=zoom, height=size[0], width=size[1])
        fig.update_traces(marker_size=4)
    else:
        fig = px.density_mapbox(map_data, hover_name="Name",
                                z="Max speed kn", radius=5,
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "COURSE",
                                "Max speed kn", "Mean speed kn", "LOA ft"],
                                zoom=zoom, height=size[0], width=size[1])
    fig.update_layout(
        mapbox_accesstoken=token,
        mapbox_style="satellite-streets",
        showlegend=False
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
