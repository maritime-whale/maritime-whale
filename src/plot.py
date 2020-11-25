from import_vessel_data import *

import glob
import os

# import plotly.graph_objects as go
import plotly.express as px
import pandas as pd






def generate_plots(map_data):
    # us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
    # type(us_cities)
    # column_names = ["lat", "lon"]
    #
    # df = pd.DataFrame(columns = column_names)

    # map_data = import_report("../tests/2020-11-11.csv")
    # charles_dict = {"Latitude": 32.76, "Longitude": -79.99}
    # charles = pd.DataFrame(charles_dict, index=["Charleston Coordinates"])
    # charles_lvl2_dict = {"Latitude": 32.75, "Longitude": -79.889}
    # charles_lvl2 = pd.DataFrame(charles_lvl2_dict, index=["Charleston Coordinates"])
    # hover_dict = {"MMSI": False, "Date/Time UTC": True, "Max speed kn": True,
    #               "Mean speed kn": True, "LOA m": True, "LOA ft": True,
    #               "Latitude": False, "Longitude": False, "COURSE": False,
    #               "Coordinates": True}

    # fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=3, height=300)
    fig1 = px.scatter_mapbox(map_data[0], lat="Latitude", lon="Longitude", hover_name="Name", hover_data=["MMSI", "Date/Time UTC", "Max speed kn", "Mean speed kn", "LOA m", "LOA ft", "COURSE"],
                            color="COURSE", zoom=10, height=600)
                            # color="COURSE", color_discrete_sequence=["fuchsia"], zoom=3, height=600)
    fig1.update_layout(
        # mapbox_style="carto-positron"#,
        # mapbox_style="carto-darkmatter",
        mapbox_style="open-street-map",
        # mapbox_style="stamen-terrain",
        # mapbox_style="white-bg",
        # mapbox_style="https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png",
        mapbox_layers=[
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Ocean Basemap LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"],
            # },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "World Street Map LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"],
            # },
            {
                "below": "traces",
                "sourcetype": "raster",
                # "sourceattribution": "United States Geological Survey",
                "sourceattribution": "NOAA",
                "source": [
                    "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}",
                    # "https://tileservice.charts.noaa.gov/tiles/"
                    # "https://tileservice.charts.noaa.gov/tiles/tileservice.xml"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png"
                    # "https://tileservice.charts.noaa.gov/tiles/12/1142/1652.png"
                    # "mapbox://styles/mapbox/satellite-v9"
                    # "https://api.mapbox.com/v4/mapbox.satellite/1/0/0@2x.jpg90?access_token=pk.eyJ1Ijoicml3aGFsZSIsImEiOiJja2h3aHVoYWcxcnRrMnducHhmcXVlZTJqIn0.f4LguFteyKBqMBZyodb-iw"
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}",
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

                ]
            },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Government of Canada",
            #     "source": ["https://geo.weather.gc.ca/geomet/?"
            #                "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
            #                "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
            # }
          ],
          showlegend=False)
        # )
    fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig1.show()

    fig2 = px.scatter_mapbox(map_data[1], lat="Latitude", lon="Longitude", hover_name="Name", hover_data=["MMSI", "Date/Time UTC", "Max speed kn", "Mean speed kn", "LOA m", "LOA ft", "COURSE"],
                            color="COURSE", zoom=10, height=600)
                            # color="COURSE", color_discrete_sequence=["fuchsia"], zoom=3, height=600)
    fig2.update_layout(
        # mapbox_style="carto-positron"#,
        # mapbox_style="carto-darkmatter",
        mapbox_style="open-street-map",
        # mapbox_style="stamen-terrain",
        # mapbox_style="white-bg",
        # mapbox_style="https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png",
        mapbox_layers=[
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Ocean Basemap LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"],
            # },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "World Street Map LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"],
            # },
            {
                "below": "traces",
                "sourcetype": "raster",
                # "sourceattribution": "United States Geological Survey",
                "sourceattribution": "NOAA",
                "source": [
                    "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}",
                    # "https://tileservice.charts.noaa.gov/tiles/"
                    # "https://tileservice.charts.noaa.gov/tiles/tileservice.xml"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png"
                    # "https://tileservice.charts.noaa.gov/tiles/12/1142/1652.png"
                    # "mapbox://styles/mapbox/satellite-v9"
                    # "https://api.mapbox.com/v4/mapbox.satellite/1/0/0@2x.jpg90?access_token=pk.eyJ1Ijoicml3aGFsZSIsImEiOiJja2h3aHVoYWcxcnRrMnducHhmcXVlZTJqIn0.f4LguFteyKBqMBZyodb-iw"
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}",
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

                ]
            },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Government of Canada",
            #     "source": ["https://geo.weather.gc.ca/geomet/?"
            #                "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
            #                "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
            # }
          ],
          showlegend=False)
        # )
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig2.show()

    fig3 = px.scatter_mapbox(map_data[2], lat="Latitude", lon="Longitude", hover_name="Name", hover_data=["MMSI", "Date/Time UTC", "Max speed kn", "Mean speed kn", "LOA m", "LOA ft", "COURSE"],
                            color="COURSE", zoom=8.5, height=600)
                            # color="COURSE", color_discrete_sequence=["fuchsia"], zoom=3, height=600)
    fig3.update_layout(
        # mapbox_style="carto-positron"#,
        # mapbox_style="carto-darkmatter",
        mapbox_style="open-street-map",
        # mapbox_style="stamen-terrain",
        # mapbox_style="white-bg",
        # mapbox_style="https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png",
        mapbox_layers=[
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Ocean Basemap LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"],
            # },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "World Street Map LODs",
            #     "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"],
            # },
            {
                "below": "traces",
                "sourcetype": "raster",
                # "sourceattribution": "United States Geological Survey",
                "sourceattribution": "NOAA",
                "source": [
                    "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}",
                    # "https://tileservice.charts.noaa.gov/tiles/"
                    # "https://tileservice.charts.noaa.gov/tiles/tileservice.xml"
                    # "https://tileservice.charts.noaa.gov/tiles/50000_1/{z}/{x}/{y}.png"
                    # "https://tileservice.charts.noaa.gov/tiles/12/1142/1652.png"
                    # "mapbox://styles/mapbox/satellite-v9"
                    # "https://api.mapbox.com/v4/mapbox.satellite/1/0/0@2x.jpg90?access_token=pk.eyJ1Ijoicml3aGFsZSIsImEiOiJja2h3aHVoYWcxcnRrMnducHhmcXVlZTJqIn0.f4LguFteyKBqMBZyodb-iw"
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                    # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}",
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}"
                    # "https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

                ]
            },
            # {
            #     "sourcetype": "raster",
            #     "sourceattribution": "Government of Canada",
            #     "source": ["https://geo.weather.gc.ca/geomet/?"
            #                "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
            #                "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
            # }
          ],
          showlegend=False)
        # )
    fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig3.show()
    return fig3, fig1, fig2






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
lvl1, lvl2_CH, lvl2_SV = generate_plots(map_data)

# import plotly.graph_objects as go
# import plotly.express as px
# import pandas as pd
#
# def generate_plots(map_data):
#     charleston = map_data[0]
#     savannah =  map_data[1]
#     agg =  map_data[2]
#
#     for data in [charleston, savannah, agg]:
#         data["Coordinates"] = list(zip(data.Latitude.round(5),
#                                        data.Longitude.round(5)))
#
#     # begin mapping workflow
#     charles_dict = {"Latitude": 32.76, "Longitude": -79.99}
#     charles = pd.DataFrame(charles_dict, index=["Charleston Coordinates"])
#     charles_lvl2_dict = {"Latitude": 32.75, "Longitude": -79.889}
#     charles_lvl2 = pd.DataFrame(charles_lvl2_dict, index=["Charleston Coordinates"])
#     sav_dict = {"Latitude": 32.0408, "Longitude": -81.0}
#     sav = pd.DataFrame(sav_dict, index=["Savannah Coordinates"])
#     sav_lvl2_dict = {"Latitude": 32.05, "Longitude": -80.86}
#     sav_lvl2 = pd.DataFrame(sav_lvl2_dict, index=["Savannah Coordinates"])
#     hover_dict = {"MMSI": False, "Date/Time UTC": True, "Max speed kn": True,
#                   "Mean speed kn": True, "LOA m": True, "LOA ft": True,
#                   "Latitude": False, "Longitude": False, "COURSE": False,
#                   "Coordinates": True}
#
#     # level 1 coastline
#     lvl1_first_dict = {"Latitude": 31.4, "Longitude": -81.3}
#     lvl1_first = pd.DataFrame(lvl1_first_dict, index=["First Coordinate"])
#     sav_EC_dict = {"Latitude": 32.0408, "Longitude": -80.8548}
#     sav_EC = pd.DataFrame(sav_EC_dict, index=["Savannah Coordinates"])
#     charles_EC_dict = {"Latitude": 32.74, "Longitude": -79.85}
#     charles_EC = pd.DataFrame(charles_EC_dict, index=["Charleston Coordinates"])
#     lvl1_fifth_dict = {"Latitude": 33, "Longitude": -79.2721}
#     lvl1_fifth = pd.DataFrame(lvl1_fifth_dict, index=["Fifth Coordinates"])
#     lvl1_coast = pd.concat([lvl1_first, sav_EC, charles_EC, lvl1_fifth])
#
#     # level 2 charleston coastline
#     CH_lvl2_first_dict = {"Latitude": 32.71, "Longitude": -79.93}
#     CH_lvl2_first = pd.DataFrame(CH_lvl2_first_dict, index=["First Coordinate"])
#     CH_lvl2_third_dict = {"Latitude": 32.76, "Longitude": -79.65}
#     CH_lvl2_third = pd.DataFrame(CH_lvl2_third_dict, index=["Third Coordinate"])
#     CH_coast = pd.concat([CH_lvl2_first, charles_EC, CH_lvl2_third])
#
#     # level 2 savannah coastline
#     SV_lvl2_first_dict = {"Latitude": 32.028, "Longitude": -80.8478}
#     SV_lvl2_first = pd.DataFrame(SV_lvl2_first_dict, index=["First Coordinate"])
#     SV_lvl2_third_dict = {"Latitude": 32.04, "Longitude": -80.73}
#     SV_lvl2_third = pd.DataFrame(SV_lvl2_third_dict, index=["Third Coordinate"])
#     SV_port_dict = {"Latitude": 32.033, "Longitude": -80.83}
#     SV_port = pd.DataFrame(SV_port_dict, index=["Savannah Coordinates"])
#     SV_coast = pd.concat([SV_lvl2_first, SV_port, SV_lvl2_third])
#     SV_label_dict = {"Latitude": 32.033, "Longitude": -80.832}
#     SV_label = pd.DataFrame(SV_label_dict, index=["Savannah Coordinates"])
#
#     # begin level 1 plotting
#     lvl1 = px.scatter(agg, x="Longitude", y="Latitude", hover_data=hover_dict,
#                       hover_name="Name", color="COURSE")
#     lvl1.update_layout(hoverlabel=dict(bgcolor="White", font_size=13,
#                        font_family="sans-serif"))
#     lvl1.add_trace(go.Scatter(x=charles["Longitude"], y=charles["Latitude"],
#                    name="Charleston", showlegend=False, text="Charleston",
#                    mode="text", textposition="middle center",
#                    textfont=dict(size=16, family="sans-serif"), hoverinfo="skip"))
#     lvl1.add_trace(go.Scatter(x=sav["Longitude"], y=sav["Latitude"],
#                    name="Savannah", showlegend=False, text="Savannah",
#                    mode="text", textposition="top center",
#                    textfont=dict(size=16, family="sans-serif"), hoverinfo="skip"))
#     lvl1.add_trace(go.Scatter(x=lvl1_coast["Longitude"], y=lvl1_coast["Latitude"],
#                    line=dict(color="Black", width=1, shape="linear"),
#                    showlegend=False, name="Coast Line", mode="lines",
#                    hoverinfo="skip"))
#     lvl1.add_trace(
#         go.Scatter(x=CH_coast.loc[["Charleston Coordinates"]]["Longitude"],
#                    y=CH_coast.loc[["Charleston Coordinates"]]["Latitude"],
#                    name="Charleston Port Entrance", mode="markers",
#                    showlegend=False, hoverinfo="skip", marker=dict(color="Black",
#                    symbol="x-thin-open", size=10)))
#     lvl1.add_trace(
#         go.Scatter(x=lvl1_coast.loc[["Savannah Coordinates"]]["Longitude"],
#                    y=lvl1_coast.loc[["Savannah Coordinates"]]["Latitude"],
#                    name="Port Entrance", mode="markers", showlegend=True,
#                    hoverinfo="skip",
#                    marker=dict(color="Black", symbol="x-thin-open", size=10)))
#     lvl1.update_layout(legend_title_text="Legend")
#
#     # begin lvl2_charleston plotting
#     lvl2_CH = px.scatter(charleston, x="Longitude", y="Latitude",
#                          hover_data=hover_dict, hover_name="Name", color="COURSE")
#     lvl2_CH.update_layout(hoverlabel=dict(bgcolor="White",
#                           font_size=13, font_family="sans-serif"))
#     lvl2_CH.add_trace(
#         go.Scatter(x=charles_lvl2["Longitude"], y=charles_lvl2["Latitude"],
#                    name="Charleston", showlegend=False, text="Charleston",
#                    mode="text", textposition="bottom right",
#                    textfont=dict(size=16, family="sans-serif"),
#                    hoverinfo="skip"))
#     lvl2_CH.add_trace(go.Scatter(x=CH_coast["Longitude"], y=CH_coast["Latitude"],
#                       line=dict(color="Black", width=1, shape="linear"),
#                       showlegend=False, name="Coast Line", mode="lines",
#                       hoverinfo="skip"))
#     lvl2_CH.add_trace(
#         go.Scatter(x=CH_coast.loc[["Charleston Coordinates"]]["Longitude"],
#                    y=CH_coast.loc[["Charleston Coordinates"]]["Latitude"],
#                    name="Charleston Port Entrance", mode="markers",
#                    showlegend=True, hoverinfo="skip", marker=dict(color="Black",
#                    symbol="x-thin-open", size=10)))
#     lvl2_CH.update_layout(legend_title_text="Legend")
#
#     # begin lvl2_savannah plotting
#     lvl2_SV = px.scatter(savannah, x="Longitude", y="Latitude",
#                          hover_data=hover_dict, hover_name="Name",
#                          color="COURSE")
#     lvl2_SV.update_layout(hoverlabel=dict(bgcolor="White", font_size=13,
#                           font_family="sans-serif"))
#     lvl2_SV.add_trace(go.Scatter(x=SV_label["Longitude"], y=SV_label["Latitude"],
#                       name="Savannah", showlegend=False, text="Savannah",
#                       mode="text", textposition="top left",
#                       textfont=dict(size=16, family="sans-serif"),
#                       hoverinfo="skip"))
#     lvl2_SV.add_trace(go.Scatter(x=SV_coast["Longitude"],
#                       y=SV_coast["Latitude"], line=dict(color="Black", width=1,
#                       shape="linear"), showlegend=False, name="Coast Line",
#                       mode="lines", hoverinfo="skip"))
#     lvl2_SV.add_trace(go.Scatter(
#                       x=SV_port["Longitude"],
#                       y=SV_port["Latitude"],
#                       name="Savannah Port Entrance", mode="markers",
#                       showlegend=True, hoverinfo="skip",
#                       marker=dict(color="Black", symbol="x-thin-open",
#                       size=10)))
#     lvl2_SV.update_layout(legend_title_text="Legend")
#     return lvl1, lvl2_CH, lvl2_SV
