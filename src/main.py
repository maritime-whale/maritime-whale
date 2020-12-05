from import_vessel_data import *
from fetch_vessel_data import *
from cache import *
from plot import *
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
    dates = [day.strftime("%Y_%m_%d") for day in days]
    date_strs = [day.strftime("%B %d %Y") for day in days]
    sync_required = False
    for date, date_str, day in zip(dates, date_strs, days):
        data_frames = []
        if not os.path.exists("../cache/" + date):
            if not sync_required:
                sync_required = True
            input_filename = day.strftime("%Y-%m-%d.csv")
            data_frames.append(import_report("../temp/" + input_filename))
            log(logfile, "Importing data from " + input_filename + "...")
            os.makedirs(os.path.dirname("../cache/" + date + "/"), exist_ok=True)
            map_data = [[], []] # [charleston, savannah]
            for df in data_frames:
                for i, map in enumerate(map_data, start=0):
                    map.append(df[i])
            id = [date + "/ch", date + "/sv"]
            for i in range(len(map_data)):
                create_csv_cache(map_data[i], id[i])
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
        log(logfile, "Loaded the last " + str(span) + " days for level two plots.")
        create_xlsx_cache(map_data[0] + temp_ch, "master-ch")
        create_xlsx_cache(map_data[1] + temp_sv, "master-sv")
        create_csv_cache(map_data[0] + temp_ch, "master-ch")
        create_csv_cache(map_data[1] + temp_sv, "master-sv")
        for i in range(len(map_data)):
            map_data[i] = pd.concat(map_data[i]).reset_index().drop("index", axis=1)
        geoplots = {"lvl2_CH":None, "lvl2_SV":None, "lvl1":None}
        zooms = (10.5, 11.5, 7)
        sizes = ((431, 707), (431, 707), (320, 692))
        token = open("../conf/.mapbox_token").read()
        for i, level in enumerate(geoplots.keys()):
            geoplots[level] = generate_geoplots(map_data[i], zooms[i], sizes[i], token)
        # output geoplots in an interactive HTML format
        pio.write_html(geoplots["lvl1"], file="../html/level_one.html", auto_open=False)
        pio.write_html(geoplots["lvl2_CH"], file="../html/level_two_charleston.html", auto_open=False)
        pio.write_html(geoplots["lvl2_SV"], file="../html/level_two_savannah.html", auto_open=False)
        log(logfile, "Finished program execution successfully.")
        log(logfile, "Preparing to upload...")
    else:
        log(logfile, "No new vessel movement reports. Caches already up-to-date.")

main()
