#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# If new data is ready to be fetched, loads cache files into memory, generates
# and writes new ouput and cache files.

from process_maritime_data import *
from fetch_vessel_data import *
from dashboard import *
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

def _write_html(fig, filename):
    return pio.write_html(fig, file=filename, auto_open=False)

def _write_image(fig, filename, format, scale):
    return pio.write_image(fig, file=filename, format=format, engine="kaleido",
                           scale=scale)

def _fetch_latest_data(logfile):
    """Checks for new data. If a cache already exists then ignore it. Any unseen
    data is processed and cached. Stores a simplified and an unsimplified
    version of the data. Indicates whether backend files are up-to-date."""
    days = fetch_latest_reports(logfile)
    if not days:
        return False
    dates = (day.strftime("%Y_%m_%d") for day in days)
    date_strs = (day.strftime("%B %d %Y") for day in days)
    sync_required = False
    for date, date_str, day in zip(dates, date_strs, days):
        if not os.path.exists("../cache/" + date):
            if not sync_required:
                sync_required = True
            input_filename = day.strftime("%Y-%m-%d.csv")
            report = process_report("../temp/" + input_filename)
            log(logfile, "Importing data from " + input_filename + "...")
            os.makedirs(os.path.dirname("../cache/" + date + "/"),
                        exist_ok=True)
            last_seven_days = [[port[0] for port in report],
                               [port[1] for port in report]]
            caches = ((date + "/ch-max", date + "/sv-max"),
                      (date + "/ch", date + "/sv"))
            for i in range(len(caches)):
                for j in range(len(last_seven_days[i])):
                    create_cache([last_seven_days[i][j]], caches[i][j], "csv")
            log(logfile, "Created cache for " + date_str + ".")
        else:
            # latest data already exists in cache
            log(logfile, "Cache already exists for " + date_str + ".")
    return sync_required

def _load_cache(logfile, data_frames, span, names):
    """Reads and combines files from cache directory. Keeps simplified and
    unsimplified data separate. Partitions both representations of data into
    most recent seven day period and rest of the season."""
    dirs = sorted([f.name for f in os.scandir("../cache/")
                  if f.is_dir()], reverse=True)
    for subdir in dirs:
        path = "../cache/" + subdir + "/*.csv"
        # [fold_ch, fold_sv, all_ch, all_sv]
        caches = [None, None, None, None]
        for filename in glob.glob(path):
            if filename.endswith(".csv"):
                for i in range(len(names)):
                    if names[i] in filename:
                        try:
                            content = pd.read_csv(filename)
                        except Exception as e:
                            log(logfile, e.message)
                            continue
                        if len(content):
                            caches[i] = content
        if True in [isinstance(cache, type(None)) for cache in caches]:
            if not subdir[0].isalpha():
                log(logfile, "Empty/partial cache found: " + subdir + ".")
            continue
        data_frames.append([caches[0], caches[1],
                            pd.concat([caches[0], caches[1]]),
                            caches[2], caches[3],
                            pd.concat([caches[2], caches[3]])])
    # [[fold_ch, fold_sv, fold_agg], [all_ch, all_sv, all_agg]]
    last_seven_days = [[[], [], []], [[], [], []]]
    span = 0
    # [[rest_of_season_ch, rest_of_season_sv],
    #  [rest_of_season_ch_all, rest_of_season_sv_all]]
    rest_of_season = [[[], []], [[],[]]]
    for df in data_frames:
        if span < 7:
            for i in range(6):
                last_seven_days[i // 3][i % 3].append(df[i])
            span += 1
        else:
            for i in range(6):
                if i % 3 == 2:
                    last_seven_days[i // 3][i % 3].append(df[i])
                else:
                    rest_of_season[i // 3][i % 3].append(df[i])
    log(logfile, "Loaded the last " + str(span) +
                 " days for level two plots.")
    return last_seven_days, rest_of_season

def _create_masters(last_seven_days, rest_of_season, filenames):
    """Generates rolling seven day and full season master files for both
    simplified and unsimplified versions of the data."""
    for i in range(len(rest_of_season)):
        for j in range(len(rest_of_season[i])):
            if i % 2 == 0:
                create_cache(last_seven_days[i][j] + rest_of_season[i][j],
                             filenames[j] + "-max", "all")
                create_cache(last_seven_days[i][j], filenames[j] +
                             "-max-roll", "all")
            else:
                create_cache(last_seven_days[i][j] +
                                 rest_of_season[i][j], filenames[j], "all")
                create_cache(last_seven_days[i][j], filenames[j] +
                                 "-roll", "all")

def main():
    logfile = datetime.datetime.now().strftime("../logs/%Y_%m_%d_%H_%M_%S.log")
    # fetch any vessel movement report CSVs marked as UNSEEN from Gmail
    if _fetch_latest_data(logfile):
        # load cache into memory if there is new data
        names = ["ch-max.csv", "sv-max.csv", "ch.csv", "sv.csv"]
        split_season = _load_cache(logfile, [], 0, names)
        last_seven_days = split_season[0]
        rest_of_season = split_season[1]
        filenames = ("master-ch", "master-sv")
        _create_masters(last_seven_days, rest_of_season, filenames)
        for i in range(len(last_seven_days[0])):
            last_seven_days[0][i] = (pd.concat(last_seven_days[0][i])
                                     .reset_index().drop("index", axis=1))
        geo_plots = {"lvl2_CH":None, "lvl2_SV":None, "lvl1":None}
        zooms = (8.5, 9.25, 7)
        centers = (dict(lat=32.68376, lon=-79.72794), dict(lat=31.99753,
                   lon=-80.78728), dict())
        opacity = (0.75, 0.75, 0.6)
        sizes = ([431, 819], [431, 819], [431, 819])
        token = open("../conf/.mapbox_token").read()
        for i, level in enumerate(geo_plots.keys()):
            hover = []
            if i <= 1:
                hover = ["Date/Time UTC", "Course Behavior", "Max Speed kn",
                         "Mean Speed kn", "WSPD mph", "Buoy Source", "Transit",
                         "Vessel Class", "LOA ft", "Beam ft", "Yaw deg",
                         "Effective Beam ft", "% Channel Occupied", "Location"]
            else:
                hover = ["Date/Time UTC", "Course Behavior", "Max Speed kn",
                         "Mean Speed kn", "WSPD mph", "Buoy Source"]

            geo_plots[level] = generate_geo_plot(last_seven_days[0][i],
                                                 zooms[i], centers[i], sizes[i],
                                                 opacity[i], hover, token)
        # output plots in an interactive HTML format
        _write_html(geo_plots["lvl1"], "../html/level_one.html")
        _write_html(geo_plots["lvl2_CH"], "../html/level_two_charleston.html")
        _write_html(geo_plots["lvl2_SV"], "../html/level_two_savannah.html")
        all_data = [pd.concat(last_seven_days[1][0]).reset_index(),
                    pd.concat(last_seven_days[1][1]).reset_index()]
        all_data.append(all_data[0].dropna())
        all_data.append(all_data[1].dropna())
        charleston = all_data[0]
        savannah = all_data[1]
        if rest_of_season[1][0]:
            charleston = pd.concat([all_data[0],
                                    pd.concat(
                                    rest_of_season[1][0]).reset_index()])
        if rest_of_season[1][1]:
            savannah = pd.concat([all_data[1],
                       pd.concat(rest_of_season[1][1]).reset_index()])
        dash = pd.concat([dashboard(charleston), dashboard(savannah)],
                          keys=["Charleston", "Savannah"],
                          axis=0).reset_index(level=1).rename(
                          {"level_1": "Vessel Class"}, axis=1)
        dash.to_csv("../html/dashboard.csv", mode="w", index=True)
        _write_image(generate_dashboard(dash), "../html/dashboard.pdf",
                     "pdf", 1)
        _write_image(generate_ticker(charleston, savannah),
                     "../html/seasonal_ticker.png", "png", 5)
        _write_html(generate_vspd_hist(all_data[0]),
                    "../html/vspd_hist_ch.html")
        _write_html(generate_vspd_hist(all_data[1]),
                    "../html/vspd_hist_sv.html")
        _write_html(generate_wspd_hist(all_data[0], all_data[2]),
                    "../html/wspd_hist_ch.html")
        _write_html(generate_wspd_hist(all_data[1], all_data[3]),
                    "../html/wspd_hist_sv.html")
        _write_html(generate_wspd_vs_vspd(all_data[0], all_data[2]),
                    "../html/wspd_vs_vspd_ch.html")
        _write_html(generate_wspd_vs_vspd(all_data[1], all_data[3]),
                    "../html/wspd_vs_vspd_sv.html")
        _write_html(generate_strip_plot(all_data[0]),
                    "../html/vspd_strip_ch.html")
        _write_html(generate_strip_plot(all_data[1]),
                    "../html/vspd_strip_sv.html")
        _write_html(generate_line_plot(all_data[0]), "../html/line_ch.html")
        _write_html(generate_line_plot(all_data[1]), "../html/line_sv.html")
        _write_html(generate_channel_occ(all_data[0]),
                    "../html/channel_occupation_ch.html")
        _write_html(generate_channel_occ(all_data[1]),
                    "../html/channel_occupation_sv.html")
        log(logfile, "Finished program execution successfully.")
        log(logfile, "Preparing to upload...")
    else:
        log(logfile,
            "No new vessel movement reports. Caches already up-to-date.")

if __name__ == "__main__":
    main()
