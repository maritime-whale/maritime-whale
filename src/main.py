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
    # days = fetch_latest_reports(logfile)
    # if not days:
    #     log(logfile, "No new vessel movement reports.")
    #     return
    # dates = (day.strftime("%Y_%m_%d") for day in days)
    # date_strs = (day.strftime("%B %d %Y") for day in days)
    # sync_required = False
    # for date, date_str, day in zip(dates, date_strs, days):
    #     if not os.path.exists("../cache/" + date):
    #         if not sync_required:
    #             sync_required = True
    #         input_filename = day.strftime("%Y-%m-%d.csv")
    #         maritime_report = import_report("../temp/" + input_filename)
    #         log(logfile, "Importing data from " + input_filename + "...")
    #         os.makedirs(os.path.dirname("../cache/" + date + "/"), exist_ok=True)
    #         maritime_data = [[port[0] for port in maritime_report],
    #                          [port[1] for port in maritime_report]]
    #         caches = ((date + "/ch-max", date + "/sv-max"),
    #                   (date + "/ch", date + "/sv"))
    #         for i in range(len(caches)):
    #             for j in range(len(maritime_data[i])):
    #                 create_csv_cache([maritime_data[i][j]], caches[i][j])
    #         log(logfile, "Created cache for " + date_str + ".")
    #     else:
    #         # latest data already exists in cache
    #         log(logfile, "Cache already exists for " + date_str + ".")
    sync_required = True

    if sync_required:
        # load cache into memory
        span = 0
        data_frames = []
        names = ["ch-max.csv", "sv-max.csv", "ch.csv", "sv.csv"]
        dirs = sorted([f.name for f in os.scandir("../cache/")
                      if f.is_dir()], reverse=True)
        for subdir in dirs:
            path = "../cache/" + subdir + "/*.csv"
            # [map_ch, map_sv, stats_ch, stats_sv]
            caches = [None, None, None, None]
            for filename in glob.glob(path):
                if filename.endswith(".csv"):
                    for i in range(len(names)):
                        if names[i] in filename:
                            caches[i] = pd.read_csv(filename) # NEED A TRY CATCH HERE
            if True in [isinstance(cache, type(None)) for cache in caches]:
                log(logfile, "Empty/partial cache found: " + subdir)
                continue
            data_frames.append([caches[0], caches[1],
                                pd.concat([caches[0], caches[1]]),
                                caches[2], caches[3],
                                pd.concat([caches[2], caches[3]])])
        # [[map_ch, map_sv, map_agg], [stats_ch, stats_sv, stats_agg]]
        maritime_data = [[[], [], []], [[], [], []]]
        span = 0
        # [[temp_ch, temp_sv], [temp_ch_stats, temp_sv_stats]]
        temps = [[[], []], [[],[]]]
        for df in data_frames:
            if span < 7:
                for i in range(6):
                    maritime_data[i // 3][i % 3].append(df[i])
                span += 1
            else:
                for i in range(6):
                    if i % 3 == 2:
                        maritime_data[i // 3][i % 3].append(df[i])
                    else:
                        temps[i // 3][i % 3].append(df[i])
        log(logfile, "Loaded the last " + str(span) + " days for level two plots.")

        filetypes = ["xlsx", "csv"]
        filenames = (("master-ch-max", "master-sv-max"), ("master-ch", "master-sv"))
        for i in range(len(filetypes)): # loop controlling file type
            for j in range(len(maritime_data)):
                for k in range(len(filenames[j])):
                    if i % 2 == 0:
                        create_xlsx_cache(maritime_data[j][k] + temps[j][k], filenames[j][k])
                    else:
                        create_csv_cache(maritime_data[j][k] + temps[j][k], filenames[j][k])
        for i in range(len(maritime_data[0])):
            maritime_data[0][i] = pd.concat(maritime_data[0][i]).reset_index().drop("index", axis=1)
        geo_plots = {"lvl2_CH":None, "lvl2_SV":None, "lvl1":None}
        zooms = (10.5, 11.5, 8)
        sizes = ((431, 707), (431, 707), (431, 707))
        heat = (False, False, False)
        token = open("../conf/.mapbox_token").read()
        for i, level in enumerate(geo_plots.keys()):
            geo_plots[level] = generate_geo_plot(maritime_data[0][i], zooms[i], sizes[i], heat[i], token)
        # output geo_plots in an interactive HTML format
        pio.write_html(geo_plots["lvl1"], file="../html/level_one.html", auto_open=False)
        pio.write_html(geo_plots["lvl2_CH"], file="../html/level_two_charleston.html", auto_open=False)
        pio.write_html(geo_plots["lvl2_SV"], file="../html/level_two_savannah.html", auto_open=False)

        stats_data = [pd.concat(maritime_data[1][0]).reset_index(), pd.concat(maritime_data[1][1]).reset_index()]
        stats_data.append(stats_data[0].dropna())
        stats_data.append(stats_data[1].dropna())

        pio.write_html(generate_vspd_hist(stats_data[0]), file="../html/vspd_hist_ch.html", auto_open=False)
        pio.write_html(generate_vspd_hist(stats_data[1]), file="../html/vspd_hist_sv.html", auto_open=False)

        pio.write_html(generate_wspd_hist(stats_data[0], stats_data[2]), file="../html/wspd_hist_ch.html", auto_open=False)
        pio.write_html(generate_wspd_hist(stats_data[1], stats_data[3]), file="../html/wspd_hist_sv.html", auto_open=False)

        # pio.write_html(generate_wspd_vs_vspd(stats_data[0], stats_data[3]), file="../html/wspd_vs_vspd_ch.html", auto_open=False)
        # pio.write_html(generate_wspd_vs_vspd(stats_data[1], stats_data[4]), file="../html/wspd_vs_vspd_sv.html", auto_open=False)
        #
        # pio.write_html(generate_strip_plot(stats_data[0]), file="../html/vspd_strip_ch.html", auto_open=False)
        # pio.write_html(generate_strip_plot(stats_data[1]), file="../html/vspd_strip_sv.html", auto_open=False)
        #
        # pio.write_html(generate_line_plot(stats_data[0]), file="../html/line_ch.html", auto_open=False)
        # pio.write_html(generate_line_plot(stats_data[1]), file="../html/line_sv.html", auto_open=False)
        #
        # pio.write_html(generate_channel_occ(stats_data[0]), file="../html/channel_occupation_ch.html", auto_open=False)
        # pio.write_html(generate_channel_occ(stats_data[1]), file="../html/channel_occupation_sv.html", auto_open=False)

        log(logfile, "Finished program execution successfully.")
        log(logfile, "Preparing to upload...")
    else:
        log(logfile, "No new vessel movement reports. Caches already up-to-date.")

main()
