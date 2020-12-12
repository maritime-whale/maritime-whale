from import_maritime_data import *
from fetch_vessel_data import *
from cache import *
from plot import *
from util import *
from log import *

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import datetime
import glob
import os

def main():
    # fetch any vessel movement report CSVs marked as UNSEEN from Gmail
    logfile = datetime.datetime.now().strftime("../logs/%Y_%m_%d_%H_%M_%S.log")
    days = fetch_latest_reports(logfile)
    if not days:
        log(logfile, "No new vessel movement reports.")
        return
    dates = (day.strftime("%Y_%m_%d") for day in days)
    date_strs = (day.strftime("%B %d %Y") for day in days)
    sync_required = False
    for date, date_str, day in zip(dates, date_strs, days):
        # data_frames = []
        if not os.path.exists("../cache/" + date):
            if not sync_required:
                sync_required = True
            input_filename = day.strftime("%Y-%m-%d.csv")
            maritime_report = import_report("../temp/" + input_filename)
            # data_frames.append(import_report("../temp/" + input_filename))
            log(logfile, "Importing data from " + input_filename + "...")
            os.makedirs(os.path.dirname("../cache/" + date + "/"), exist_ok=True)
            # map_data = [[], []] # [charleston, savannah]
            # stats_data = [[], []] # [charleston, savannah]
            # for df in data_frames:
            #     for j in range(len(map_data)):
            #         map_data[j].append(df[j][0])
            maritime_data = [[port[0] for port in maritime_report],
                             [port[1] for port in maritime_report]]
            caches = ((date + "/ch-geo", date + "/sv-geo"),
                      (date + "/ch", date + "/sv"))
            for i in range(len(caches)):
                for j in range(len(maritime_data[i])):
                    create_csv_cache([maritime_data[i][j]], caches[i][j])
            log(logfile, "Created cache for " + date_str + ".")
        else:
            # latest data already exists in cache
            log(logfile, "Cache already exists for " + date_str + ".")

    if sync_required:
        # load cache into memory
        span = 0
        data_frames = []
        dirs = sorted([f.name for f in os.scandir("../cache/")
                      if f.is_dir()], reverse=True)
        for subdir in dirs:
            path = "../cache/" + subdir + "/*.csv"
            # [[geo_ch, geo_sv], [stats_ch, stats_sv]]
            # csvs = [[None, None],[None, None]]

            # geo_ch_cache = None
            # geo_sv_cache = None
            # stats_ch_cache = None
            # stats_sv_cache = None

            # [geo_ch, geo_sv, stats_ch, stats_sv]
            caches = [None, None, None, None]
            for filename in glob.glob(path):
                if filename.endswith(".csv"):
                    if "ch-geo.csv" in filename:
                        caches[0] = pd.read_csv(filename)
                    elif "sv-geo.csv" in filename:
                        caches[1] = pd.read_csv(filename)
                    elif "ch.csv" in filename:
                        caches[2] = pd.read_csv(filename)
                    elif "sv.csv" in filename:
                        caches[3] = pd.read_csv(filename)
            if True in [isinstance(cache, type(None)) for cache in caches]:
                log(logfile, "Empty/partial cache found: " + subdir)
                continue
            data_frames.append([caches[0], caches[1],
                                pd.concat([caches[0], caches[1]]),
                                caches[2], caches[3],
                                pd.concat([caches[2], caches[3]])])
            # data_frames.append([ch_cache, sv_cache,
            #                     pd.concat([ch_cache, sv_cache])])

        map_data = [[], [], []] # [charleston, savannah, aggregate]
        stats_data = [[], [], []]
        span = 0
        temp_ch = []
        temp_sv = []
        temp_ch_stats = []
        temp_sv_stats = []
        for df in data_frames:
            if span < 7:
                map_data[0].append(df[0])
                map_data[1].append(df[1])
                map_data[2].append(df[2])
                stats_data[0].append(df[3])
                stats_data[1].append(df[4])
                stats_data[2].append(df[5])
                span += 1
            else:
                temp_ch.append(df[0])
                temp_sv.append(df[1])
                map_data[2].append(df[2])
                temp_ch_stats.append(df[3])
                temp_ch_stats.append(df[4])
                stats_data[2].append(df[5])
        log(logfile, "Loaded the last " + str(span) + " days for level two plots.")
        create_xlsx_cache(map_data[0] + temp_ch, "master-ch")
        create_xlsx_cache(map_data[1] + temp_sv, "master-sv")
        create_csv_cache(map_data[0] + temp_ch, "master-ch")
        create_csv_cache(map_data[1] + temp_sv, "master-sv")
        for i in range(len(map_data)):
            map_data[i] = pd.concat(map_data[i]).reset_index().drop("index", axis=1)
        geo_plots = {"lvl2_CH":None, "lvl2_SV":None, "lvl1":None}
        zooms = (10.5, 11.5, 8)
        sizes = ((431, 707), (431, 707), (431, 707))
        heat = (False, False, False)
        token = open("../conf/.mapbox_token").read()
        for i, level in enumerate(geo_plots.keys()):
            geo_plots[level] = generate_geo_plot(map_data[i], zooms[i], sizes[i], heat[i], token)
        # output geo_plots in an interactive HTML format
        pio.write_html(geo_plots["lvl1"], file="../html/level_one.html", auto_open=False)
        pio.write_html(geo_plots["lvl2_CH"], file="../html/level_two_charleston.html", auto_open=False)
        pio.write_html(geo_plots["lvl2_SV"], file="../html/level_two_savannah.html", auto_open=False)
        log(logfile, "Finished program execution successfully.")
        log(logfile, "Preparing to upload...")
    else:
        log(logfile, "No new vessel movement reports. Caches already up-to-date.")

main()
