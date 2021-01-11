from datetime import *
from meetpass import *
from util import *

import pandas as pd
import math
# import timedelta
import sys

def validate_vmr(df):
    df = df[~df.index.isin(df[df["Beam ft"] >= 500].index)] #check with Jon on this..
    df = df[~df.index.isin(df[df["Course"] == 511].index)]
    df = df[~df.index.isin(df[df["Heading"] == 511].index)]
    df = df[~df.index.isin(df[df["VSPD kn"] >= 40].index)]
    df = df[~df.MMSI.isin(df.MMSI.value_counts()[df.MMSI.value_counts() == 1].index.values)]
    return df

def filter_blacklisters(res, blacklist):
    res = res[~res.MMSI.isin(blacklist)]
    new_blacklisters = []
    for j in range(res.shape[0]):
        if res.iloc[j]["AIS Type"] in [30, 31, 32, 33, 34, 35, 36, 37,
                                       51, 52, 53, 55, 57, 58, 59]:
            new_blacklisters.append(res.iloc[j].MMSI)
    with open("../cache/blacklist.txt", "a") as f:
        contents = [str(mmsi) for mmsi in new_blacklisters]
        if contents != []:
            f.write("\n".join(contents) + "\n")

    res = res[~res.MMSI.isin(new_blacklisters)]
    return res

def import_report(path):
# def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    blacklist = [int(mmsi) for mmsi in open("../cache/blacklist.txt",
                                            "r").readlines()]
    df = pd.read_csv(path)
    # df = filter_blacklisters(df, blacklist)
    # for row in range(len(ports[i])):
    #     print(row)
    # for row in range(len(df)):
    #     print(row)

    df.rename({"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
               "LATITUDE": "Latitude", "LONGITUDE": "Longitude", "SPEED": "VSPD kn",
               "COURSE": "Course", "HEADING": "Heading", "AIS TYPE": "AIS Type"}, axis=1,
               inplace=True)
    # df["LOA m"] = df["A"] + df["B"]
    df["LOA ft"] = (df["A"] + df["B"]) * 3.28
    df["LOA ft"] = df["LOA ft"].round(0)
    # df["Beam m"] = df["C"] + df["D"]
    df["Beam ft"] = (df["C"] + df["D"]) * 3.28
    df["Beam ft"] = df["Beam ft"].round(0)
    df["Latitude"] = df["Latitude"].round(5)
    df["Longitude"] = df["Longitude"].round(5)
    # df["Yaw deg"] = abs(df.COURSE - df.HEADING)
    sub_panamax = None
    # if mode == "sub-panamax":
    #     sub_panamax = df[df["LOA m"] < 200]
    # df = df[df["LOA m"] >= 200]
    # input validation function
    df = validate_vmr(df)
    df = df[df["LOA ft"] >= 656]
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    df = df[["Date/Time UTC", "Name", "MMSI", "LOA ft", "Latitude",
             "Longitude", "Course", "AIS Type", "Heading", "VSPD kn", "Beam ft"]]
    ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
    sv_course_ranges = ((100, 160), (280, 340))
    channel_midpoint = ((-79.74169), (-80.78522)) # less than this value is nearshore, greater is offshore. both longitude values
    course_ranges = (ch_course_ranges, sv_course_ranges)
    course_behavior = ("Outbound", "Inbound")
    ports = [None, None] # ch, sv
    # [{ch_off, ch_near}, {sv_off, sv_near}]
    buoys = [{"41004":None, "FBIS1":None}, {"41008":None, "41033":None}]
    for i in range(len(ports)):
        ports[i] = df[df.Latitude >= 32.033] if (i == 0) else df[df.Latitude < 32.033]
        if not len(ports[i]):
            ports[i] = [pd.DataFrame({"Date/Time UTC":[], "Name":[], "MMSI":[], "Max Speed kn":[],
                                      "Mean Speed kn":[], "LOA ft":[], "Beam ft":[], "Vessel Class":[], "AIS Type":[],
                                      "Course":[], "Heading":[], "Course Behavior":[], "Yaw deg":[], "Effective Beam ft":[],
                                      "WDIR degT":[], "WSPD mph":[], "GST mph":[], "Location":[], "Latitude":[],
                                      "Longitude":[], "Transit":[], "% Channel Occupied":[]}),#"Condition":[], "% Channel Occupied":[]}),
                        pd.DataFrame({"Date/Time UTC":[], "Name":[], "MMSI":[], "VSPD kn":[], "LOA ft":[],
                                      "Beam ft":[], "Vessel Class":[], "AIS Type":[], "Course":[], "Heading":[],
                                      "Course Behavior":[], "Yaw deg":[], "Effective Beam ft":[], "WDIR degT":[],
                                      "WSPD mph":[], "GST mph":[], "Location":[], "Latitude":[],
                                      "Longitude":[], "Transit":[], "% Channel Occupied":[]})]#"Condition":[], "% Channel Occupied":[]})]
            continue
        ports[i].loc[:, "Location"] = "Nearshore"
        ports[i].loc[:, "Location"][ports[i].index.isin(ports[i][ports[i]["Longitude"] > channel_midpoint[i]].index)] = "Offshore"
        # offshore: 41004 (ch), 41008 (sv)
        # nearshore: FBIS1 (ch), 41033 (sv)
        year = ports[i]["Date/Time UTC"].iloc[0].strftime("%Y")
        month = ports[i]["Date/Time UTC"].iloc[0].strftime("%m")
        day = ports[i]["Date/Time UTC"].iloc[0].strftime("%d")
        for buoy in buoys[i].keys():
            try:
                buoys[i][buoy] = pd.read_csv("../temp/" + buoy + ".txt", delim_whitespace=True).drop(0)
            except FileNotFoundError:
                sys.stderr.write("Error: Wind data not found for buoy with ID: " + buoy + "...\n")
                continue
            except:
                sys.stderr.write("Error: Could not load wind data for buoy with ID: " + buoy + "...\n")
                continue
        for j, buoy in enumerate(buoys[i].items()):
            final_winds = {"WDIR degT":[], "WSPD mph":[], "GST mph":[]} # {wind_dir, wind_speed, gust}
            id = buoy[0]
            data = buoy[1]
            if isinstance(data, type(None)) or data.shape[0] == 0:
                sys.stderr.write("Error: Wind data not found for " +
                                 str(year) + "-" + str(month) + "-" +
                                 str(day) + " for buoy with ID: " +
                                 id + "...\n")
                ports[i].loc[:, "WDIR degT"] = [float("NaN") for ii in range(len(ports[i]))]
                ports[i].loc[:, "WSPD mph"] = [float("NaN") for ii in range(len(ports[i]))]
                ports[i].loc[:, "GST mph"] = [float("NaN") for ii in range(len(ports[i]))]
                continue
            data = data[(data["#YY"] == year) &
                        (data["MM"] == month) &
                        (data["DD"] == day)]
            # data["Date/Time UTC"] = pd.to_datetime(data["#YY"] + data["MM"] + data["DD"] + data["hh"] + data["mm"],
            #                                      infer_datetime_format=True) chain method
            data.loc[:, "Date/Time UTC"] = pd.to_datetime(data["#YY"] + data["MM"] + data["DD"] + data["hh"] + data["mm"],
                                                 infer_datetime_format=True)
            data.rename({"WDIR":"WDIR degT", "WSPD":"WSPD m/s", "GST":"GST m/s"}, axis=1, inplace=True)
            data = data[(data["WDIR degT"] != "MM") &
                        (data["WSPD m/s"] != "MM") &
                        (data["GST m/s"] != "MM")]
            data.loc[:, "WSPD mph"] = data.loc[:, "WSPD m/s"].astype("float") * 2.237
            data.loc[:, "GST mph"] = data.loc[:, "GST m/s"].astype("float") * 2.237
            data.loc[:, "WSPD mph"] = data.loc[:, "WSPD mph"].round(2)
            data.loc[:, "GST mph"] = data.loc[:, "GST mph"].round(2)
            buoys[i][id] = data[["Date/Time UTC", "WDIR degT", "WSPD mph", "GST mph"]]
            # do windspeed matching here
            # offshore: 41004 (ch), 41008 (sv)
            # nearshore: FBIS1 (ch), 41033 (sv)
            input_times = None
            wind_data = buoys[i][id]
            target_times = list(wind_data["Date/Time UTC"])
            # nearshore
            if j % 2:
                input_times = list(ports[i][ports[i]["Location"] == "Nearshore"]["Date/Time UTC"])
            # offshore
            else:
                input_times = list(ports[i][ports[i]["Location"] == "Offshore"]["Date/Time UTC"])
            # match wind speed to location
            for ii in range(len(input_times)):
                min_timedelta = timedelta(hours=WIND_TIME_TOL)
                min_timedelta_index = -1
                for jj in range(len(target_times)):
                    delta = abs(input_times[ii] - target_times[jj])
                    if delta <= timedelta(hours=WIND_TIME_TOL):
                        if min_timedelta > delta:
                            min_timedelta = delta
                            min_timedelta_index = jj
                    else:
                        continue
                if min_timedelta < timedelta(hours=WIND_TIME_TOL) and min_timedelta_index != -1:
                    for k in final_winds:
                        final_winds[k].append(wind_data[k].iloc[min_timedelta_index])
                else:
                    # handle missing wind vals
                    for k in final_winds:
                        final_winds[k].append(float("NaN"))
            for k in final_winds:
                if j % 2:
                    ports[i].loc[ports[i].Location == "Nearshore", k] = final_winds[k]
                else:
                    ports[i].loc[ports[i].Location == "Offshore", k] = final_winds[k]
        ports[i] = ports[i][(ports[i].Course >= course_ranges[i][0][0]) &
                            (ports[i].Course <= course_ranges[i][0][1]) |
                            (ports[i].Course >= course_ranges[i][1][0]) &
                            (ports[i].Course <= course_ranges[i][1][1])]
        ports[i].Course = round(ports[i].Course).astype("int")
        ports[i].loc[:, "Course Behavior"] = ports[i].loc[:, "Course"]
        courses = {}
        for behavior, course_range in zip(course_behavior, course_ranges[i]):
            lower_bound = course_range[0]
            upper_bound = course_range[1]
            for j in range(lower_bound, upper_bound + 1):
                courses[j] = behavior
        ports[i].loc[:, "Course Behavior"] = ports[i].loc[:, "Course Behavior"].replace(courses).astype("str")
        ### Vessel Class specification
        ports[i].loc[:, "Vessel Class"] = "Panamax"
        ports[i].loc[:, "Vessel Class"][ports[i].index.isin(ports[i][ports[i]["LOA ft"] > 965].index)] = "Post-Panamax"

        ports[i].loc[:, "Yaw deg"] = abs(ports[i].loc[:, "Course"] - ports[i].loc[:, "Heading"])

        EB = []
        loa = ports[i]["LOA ft"].values
        beam = ports[i]["Beam ft"].values
        yaw = ports[i]["Yaw deg"].values
        for l in range(ports[i].shape[0]):
            EB.append(round((math.cos(math.radians(90-yaw[l]))*loa[l]) + (math.cos(math.radians(yaw[l]))*beam[l])))

        ports[i].loc[:, "Effective Beam ft"] = EB
        # ports[i].loc[:, "Effective Beam ft"] = ports[i].loc[:, "Effective Beam m"] * 3.28
        ports[i].loc[:, "Effective Beam ft"] = ports[i].loc[:, "Effective Beam ft"].round(0)
        ports[i] = filter_blacklisters(ports[i], blacklist)
        ports[i].loc[:, "rounded date"] = [ports[i].loc[:, "Date/Time UTC"].iloc[ii].floor("Min") for ii in range(len(ports[i].loc[:, "Date/Time UTC"]))]

        mp = meetpass(ports[i])
        two_way = twoway(ports[i], mp)
        ports[i]["Transit"] = "One-way Transit"
        if not isinstance(two_way, type(None)):
            ports[i]["Transit"][ports[i].index.isin(two_way.index)] = "Two-way Transit"

        ports[i] = ports[i].reset_index()
        channel_width = [[800, 400, 1000, 500], [600, 300, 600, 300]]
        for row in range(len(ports[i])):
            if (ports[i].loc[row, "Vessel Class"] == "Post-Panamax") & (ports[i].loc[row, "Transit"] == "One-way Transit"):
                ports[i].loc[row, "% Channel Occupied"] = round((ports[i].loc[row, "Effective Beam ft"] / channel_width[i][0]) * 100, 2)
            elif (ports[i].loc[row, "Vessel Class"] == "Post-Panamax") & (ports[i].loc[row, "Transit"] == "Two-way Transit"):
                ports[i].loc[row, "% Channel Occupied"] = round((ports[i].loc[row, "Effective Beam ft"] / channel_width[i][1]) * 100, 2)
            elif (ports[i].loc[row, "Vessel Class"] == "Panamax") & (ports[i].loc[row, "Transit"] == "One-way Transit"):
                ports[i].loc[row, "% Channel Occupied"] = round((ports[i].loc[row, "Effective Beam ft"] / channel_width[i][2]) * 100, 2)
            elif (ports[i].loc[row, "Vessel Class"] == "Panamax") & (ports[i].loc[row, "Transit"] == "Two-way Transit"):
                ports[i].loc[row, "% Channel Occupied"] = round((ports[i].loc[row, "Effective Beam ft"] / channel_width[i][3]) * 100, 2)
            else:
                sys.stderr.write("Error: Undefined vessel class and transit combination...\n")
                ports[i].loc[row, "% Channel Occupied"] = float("NaN")

        # for row in range(len(ports[i])):
        #     if (ports[i].loc[row, "WSPD mph"] >= 30) or (ports[i].loc[row, "Transit"] == "Two-way Transit"):
        #         ports[i].loc[row, "Condition"] = "Adverse Condition"
        #     elif (ports[i].loc[row, "WSPD mph"] < 30) or (ports[i].loc[row, "Transit"] == "One-way Transit"):
        #         ports[i].loc[row, "Condition"] = "Non-adverse Condition"
        #     else:
        #         sys.stderr.write("Error: Undefined wind speed and transit combination...\n")
        #         ports[i].loc[row, "Condition"] = float("NaN")

        # for row in range(len(ports[i])):
        #     if (ports[i].loc[row, "WSPD mph"] >= 30) & (ports[i].loc[row, "Transit"] == "Two-way Transit"):
        #         ports[i].loc[row, "Condition"] = "Adverse Condition (Two-Way Transit and High Wind)"
        #     elif (ports[i].loc[row, "WSPD mph"] >= 30) & (ports[i].loc[row, "Transit"] == "One-way Transit"):
        #         ports[i].loc[row, "Condition"] =  "Adverse Condition (High Wind)" # "Adverse Condition (High Wind and One-Way Transit)"
        #     elif (ports[i].loc[row, "WSPD mph"] < 30) & (ports[i].loc[row, "Transit"] == "Two-way Transit"):
        #         ports[i].loc[row, "Condition"] =  "Adverse Condition (Two-Way Transit)" # "Adverse Condition (Two-Way Transit and Low Wind)"
        #     elif (ports[i].loc[row, "WSPD mph"] < 30) & (ports[i].loc[row, "Transit"] == "One-way Transit"):
        #         ports[i].loc[row, "Condition"] =  "Non-adverse Condition (One-Way Transit)" # "Non-adverse Condition (One-Way Transit and Low Wind)"
        #     else:
        #         sys.stderr.write("Error: Undefined wind speed and transit combination...\n")
        #         ports[i].loc[row, "Condition"] = float("NaN")

        stats_res = ports[i]
        ######BELOW WILL BE REMOVED ONCE YAW ALGORITHM HAS BEEN DEVELOPED########
        if i % 2:
            stats_res = stats_res[(stats_res.Latitude <= 32.02838) & (stats_res.Latitude >= 31.9985) | (stats_res.Latitude <= 31.99183)]
        else:
            stats_res = stats_res[stats_res.Latitude >= 32.667473]
        ######ABOVE WILL BE REMOVED ONCE YAW ALGORITHM HAS BEEN DEVELOPED########

        mean = pd.DataFrame(
            ports[i].groupby(["Name", "MMSI"])["VSPD kn"].mean()).rename(
            {"VSPD kn": "Mean Speed kn"}, axis=1).round(1)
        maxes = pd.DataFrame(
            ports[i].groupby(["Name", "MMSI"])["VSPD kn"].max()).rename(
            {"VSPD kn": "Max Speed kn"}, axis=1)
        merged_speeds = maxes.merge(mean, on=["Name", "MMSI"])
        d = merged_speeds["Max Speed kn"].to_dict()
        columns = {"Longitude":[], "Latitude":[], "Date/Time UTC":[],
                   "LOA ft":[], "Course":[], "AIS Type":[],
                   "WSPD mph":[], "GST mph":[], "WDIR degT":[], "Beam ft":[],
                   "Heading":[], "Course Behavior":[], "Effective Beam ft":[],
                   "Vessel Class":[], "Location":[], "Yaw deg":[], "Transit":[],
                   "% Channel Occupied":[]}#, "Condition":[]}
        for key, value in d.items():
            for k in columns.keys():
                columns[k].append(ports[i][(ports[i].Name == key[0]) &
                                 (ports[i]["VSPD kn"] == value)][k].iloc[0])
        for key in columns.keys():
            merged_speeds[key] = columns[key]
        merged_speeds = merged_speeds.reset_index()

        lvl_res = merged_speeds
        lvl_res.sort_values("Max Speed kn", ascending=False, inplace=True)
        lvl_res = lvl_res[["Date/Time UTC", "Name", "MMSI", "Max Speed kn",
                   "Mean Speed kn", "LOA ft", "Beam ft", "Vessel Class", "AIS Type",
                   "Course", "Heading", "Course Behavior", "Yaw deg", "Effective Beam ft",
                   "WDIR degT", "WSPD mph", "GST mph", "Location", "Latitude",
                   "Longitude", "Transit", "% Channel Occupied"]]#"Condition", "% Channel Occupied"]]

        stats_res = stats_res[["Name", "MMSI", "VSPD kn", "WSPD mph", "Transit",
                                # "Condition",
                                "% Channel Occupied", "Yaw deg", "Effective Beam ft",
                                "LOA ft", "Beam ft", "Vessel Class", "AIS Type",
                                "Course", "Heading", "Course Behavior",
                                "WDIR degT", "GST mph",
                                "Location", "Latitude", "Longitude", "Date/Time UTC"]]

        ports[i] = [lvl_res, stats_res]

    return ports[0], ports[1] # ch, sv
