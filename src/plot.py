# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)

from import_vessel_data import *

import os
import glob

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_plots(map_data, zoom, heatmap_enabled, token):
    # charles_dict = {"Latitude": 32.76, "Longitude": -79.99}
    # charles = pd.DataFrame(charles_dict, index=["Charleston Coordinates"])
    # sav_dict = {"Latitude": 32.0408, "Longitude": -81.0}
    # sav = pd.DataFrame(sav_dict, index=["Savannah Coordinates"])
    fig = None
    if not heatmap_enabled:
        fig = px.scatter_mapbox(map_data, hover_name="Name",
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "COURSE",
                                "Max speed kn", "Mean speed kn", "LOA ft"],
                                color_discrete_sequence=["white"],
                                zoom=zoom, height=600)
    else:
        fig = px.density_mapbox(map_data, hover_name="Name",
                         z="Mean speed kn", radius=5,
                         lat="Latitude", lon="Longitude",
                         hover_data=["Date/Time UTC", "COURSE",
                         "Max speed kn", "Mean speed kn", "LOA ft"],
                         zoom=zoom, height=600)
    fig.update_layout(
        mapbox_accesstoken=token,
        mapbox_style="satellite-streets",
        # mapbox_layers=[
        # {
        #     "below": 'traces',
        #     "sourcetype": "raster",
        #     "sourceattribution": "United States Geological Survey",
        #     "source": [
        #         # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
        #     ]
        # },
        # # {
        # #     "sourcetype": "raster",
        # #     "sourceattribution": "Government of Canada",
        # #     "source": [
        # #        "https://geo.weather.gc.ca/geomet/?"
        # #        "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
        # #        "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"
        # #     ],
        # # }
        # ],
        showlegend=False
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # fig.update_trace(hovertemplate=None, hoverinfo="skip")
    # fig.add_trace(go.Scatter(x=charles["Longitude"], y=charles["Latitude"],
    #               name="Charleston", showlegend=False, text="Charleston",
    #               mode="text", textposition="middle center",
    #               textfont=dict(size=16, family="sans-serif"), hoverinfo="skip"))
    # fig.add_trace(go.Scatter(x=sav["Longitude"], y=sav["Latitude"],
    #               name="Savannah", showlegend=False, text="Savannah",
    #               mode="text", textposition="top center",
    #               textfont=dict(size=16, family="sans-serif"), hoverinfo="skip"))
    return fig


# load cache into memory
span = 0
data_frames = []
dirs = sorted([f.name for f in os.scandir("../cache/")
              if f.is_dir()], reverse=True)
for subdir in dirs:
    path = "../cache/" + subdir + "/*.csv"
    csv = []
    for filename in glob.glob(path):
        if filename.endswith(".csv") and ("ch.csv" in filename or "sv.csv" in filename):
            csv.append(filename)
    if not csv:
        log(logfile, "Empty cache found: " + subdir)
        continue
    ch_cache = pd.read_csv(csv[1])
    sv_cache = pd.read_csv(csv[0])
    data_frames.append([ch_cache, sv_cache,
                        pd.concat([ch_cache, sv_cache])])

map_data = [[], [], []] # [charleston, savannah, aggregate]
span = 0
temp_ch = []
temp_sv = []
for df in data_frames:
    if span < 7:
        map_data[0].append(df[0])
        map_data[1].append(df[1])
        map_data[2].append(df[2])
        span += 1
    else:
        temp_ch.append(df[0])
        temp_sv.append(df[1])
        map_data[2].append(df[2])
# log(logfile, "Loaded the last " + str(span) + " days for level two plots.")
# create_xlsx_cache(map_data[0] + temp_ch, "master-ch")
# create_xlsx_cache(map_data[1] + temp_sv, "master-sv")
# create_csv_cache(map_data[0] + temp_ch, "master-ch")
# create_csv_cache(map_data[1] + temp_sv, "master-sv")
for i in range(len(map_data)):
    map_data[i] = pd.concat(map_data[i]).reset_index().drop("index", axis=1)
plots = {"lvl2_CH":None, "lvl2_SV":None, "lvl1":None}
zooms = [10.5, 10.5, 8.5]
heat = [False, False, True]
token = open("../conf/.mapbox_token").read()
for i, level in enumerate(plots.keys()):
    plots[level] = generate_plots(map_data[i], zooms[i], heat[i], token)
plots["lvl1"].show()
plots["lvl2_CH"].show()
plots["lvl2_SV"].show()
