# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Processes wind and vessel data. Performs simple analysis.

from datetime import *
from meetpass import *

import pandas as pd
import math
import sys

# vessel (AIS) types that should be automatically purged from analysis
# see details at https://api.vesselfinder.com/docs/ref-aistypes.html
AUTO_BLACKLIST = [30, 31, 32, 33, 34, 35, 36, 37, 51, 52, 53, 55, 57, 58, 59]

# thresholds and tolerances
SUB_PANAMAX = 656 # in feet
WIND_TIME_TOL = 3 # in hours

# conversions
MPS_TO_MPH = 2.237 # meters per sec to miles per hour
M_TO_FT = 3.28 # meters to feet

# TODO(omrinewman): revise function headers
# TODO(omrinewman): break process_report into smaller functions
# TODO: document wind speed matching design decisions and quirks in methodologies
# TODO: validate VMR (don't think we actually do this anywhere; could be valuable)

def _sanitize_vmr(df):
    """Filters entries with '511' error, impossibly high speed, abnormally
    high vessel width, as well as singletons (only one entry) from vessel
    movement DataFrame.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Sanitized vessel movement report DataFrame.
    """
    df = df[~df.index.isin(df[df["Beam ft"] >= 500].index)]
    df = df[~df.index.isin(df[df["Course"] == 511].index)]
    df = df[~df.index.isin(df[df["Heading"] == 511].index)]
    df = df[~df.index.isin(df[df["VSPD kn"] >= 40].index)]
    df = df[~df.MMSI.isin(
             df.MMSI.value_counts()[df.MMSI.value_counts() == 1].index.values)]
    return df

def _filter_blacklisters(df, blacklist):
    """Checks vessel AIS types and ommits blacklisted vessel types from the
    filtered data. Appends ommitted vessels' MMSI's to blacklist.txt.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Filtered vessel movement DataFrame.
    """
    df = df[~df.MMSI.isin(blacklist)]
    new_blacklisters = []
    for j in range(df.shape[0]):
        if df.iloc[j]["AIS Type"] in AUTO_BLACKLIST:
            new_blacklisters.append(df.iloc[j].MMSI)
    with open("../cache/blacklist.txt", "a") as f:
        contents = [str(mmsi) for mmsi in new_blacklisters]
        if contents:
            f.write("\n".join(contents) + "\n")
    df = df[~df.MMSI.isin(new_blacklisters)]
    return df

def process_report(path):
    """Reads, processes, and wrangles data from vessel movement reports.
    Augments movement reports with wind data from sensor buoys as well as
    meeting and passing analysis. Computes some simple statistics, which are
    also added to the resulting DataFrames.

    Args:
        path: Relative path to raw vessel movement report (CSV).

    Returns:
        Two pairs of DataFrames cooresponding to the filtered movement reports.
        The first pair of DataFrames contains all vessel movements belonging to
        Charleston and Savannah, respectively. The second pair of DataFrames
        stores only the vessel movement entries at which each vessel achieved
        its maximum speed (again the first DataFrame in the pair belongs to
        Charleston and the second DataFrame belongs to Savannah).
    """
    # read in existing blacklisted vessel MMSI's as a list
    blacklist = [int(mmsi) for mmsi in open("../cache/blacklist.txt",
                                            "r").readlines()]
    df = pd.read_csv(path)
    df.rename({"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
               "LATITUDE": "Latitude", "LONGITUDE": "Longitude",
               "SPEED": "VSPD kn", "COURSE": "Course", "HEADING": "Heading",
               "AIS TYPE": "AIS Type"}, axis=1, inplace=True)
    df["LOA ft"] = (df["A"] + df["B"]) * M_TO_FT
    df["LOA ft"] = df["LOA ft"].round(0)
    df["Beam ft"] = (df["C"] + df["D"]) * M_TO_FT
    df["Beam ft"] = df["Beam ft"].round(0)
    df["Latitude"] = df["Latitude"].round(5)
    df["Longitude"] = df["Longitude"].round(5)
    df = _sanitize_vmr(df)
    df = df[df["LOA ft"] >= SUB_PANAMAX] # filter out sub-panamax class vessels
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    df = df[["Date/Time UTC", "Name", "MMSI", "LOA ft", "Latitude", "Longitude",
             "Course", "AIS Type", "Heading", "VSPD kn", "Beam ft"]]
    ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
    sv_course_ranges = ((100, 160), (280, 340)) # (outbound, inbound)
    # longitudinal channel midpoint for Charleston and Savannah respectively
    channel_midpoint = ((-79.74169), (-80.78522))
    course_ranges = (ch_course_ranges, sv_course_ranges)
    course_behavior = ("Outbound", "Inbound")
    ports = [None, None] # ch, sv
    # Charleston NOAA wind buoy ID (41004)
    # Savannah NOAA wind buoy ID (41008)
    buoys = [{"41004":None}, {"41008":None}] # main wind buoys
    alt_buoys = [{"41008":None}, {"41004":None}] # alternate wind buoys
    # split data into Charleston and Savannah DataFrames based on latitude
    for i in range(len(ports)):
        ch_df = (df.Latitude >= 32.033)
        sv_df = (df.Latitude < 32.033)
        ports[i] = df[ch_df] if (i == 0) else df[sv_df]
        # if there is no vessel data on a given day (e.g. major holidays)
        # return empty DataFrames
        if not len(ports[i]):
            empty = pd.DataFrame({"Date/Time UTC":[], "Name":[], "MMSI":[],
                                  "Max Speed kn":[], "Mean Speed kn":[],
                                  "LOA ft":[], "Beam ft":[], "Vessel Class":[],
                                  "AIS Type":[], "Course":[], "Heading":[],
                                  "Course Behavior":[], "Yaw deg":[],
                                  "Effective Beam ft":[], "WDIR degT":[],
                                  "WSPD mph":[], "GST mph":[], "Buoy Source":[],
                                  "Location":[], "Latitude":[], "Longitude":[],
                                  "Transit":[], "% Channel Occupied":[]})
            ports[i] = [empty, empty]
            continue
        # initialize location column to Nearshore; compute Offshore locations
        ports[i].loc[:, "Location"] = "Nearshore"
        off_locs = ports[i][ports[i]["Longitude"] > channel_midpoint[i]].index
        offshore_indices = ports[i].index.isin(off_locs)
        ports[i].loc[:, "Location"][offshore_indices] = "Offshore"
        # capture datetime info to be used for wind buoy matching
        year = ports[i]["Date/Time UTC"].iloc[0].strftime("%Y")
        month = ports[i]["Date/Time UTC"].iloc[0].strftime("%m")
        day = ports[i]["Date/Time UTC"].iloc[0].strftime("%d")
        # read main and alternate wind buoy txt files as DataFrames
        for buoy_set in [buoys, alt_buoys]:
            for buoy in buoy_set[i].keys():
                try:
                    buoy_set[i][buoy] = pd.read_csv("../temp/" + buoy + ".txt",
                                                    delim_whitespace=True
                                                    ).drop(0)
                except FileNotFoundError:
                    sys.stderr.write("Error: Wind data not found for buoy " +
                                     "with ID: " + buoy + "...\n")
                    continue
                except:
                    sys.stderr.write("Error: Could not load wind data for " +
                                     "buoy with ID: " + buoy + "...\n")
                    continue
        for buoy, alt_buoy in zip(buoys[i].items(), alt_buoys[i].items()):
            # initialize dictionary to store wind direction, speed, and gust
            final_winds = {"WDIR degT":[], "WSPD mph":[], "GST mph":[]}
            source_buoy = []
            id = buoy[0] # main buoy ID
            buoy_data = buoy[1] # main buoy data
            alt_id = alt_buoy[0] # alternate buoy ID
            alt_buoy_data = alt_buoy[1] # alternate buoy data
            # handle wind outages
            if ((isinstance(buoy_data, type(None)) or
                 buoy_data.shape[0] == 0) and
                (isinstance(alt_buoy_data, type(None)) or
                 alt_buoy_data.shape[0] == 0)):
                sys.stderr.write("Error: Wind data not found for " +
                                 str(year) + "-" + str(month) + "-" +
                                 str(day) + " for buoy with ID: " +
                                 id + "...\n")
                nans = [float("NaN") for ii in range(len(ports[i]))]
                outage = ["N/A" for ii in range(len(ports[i]))]
                ports[i].loc[:, "WDIR degT"] = nans
                ports[i].loc[:, "WSPD mph"] = nans
                ports[i].loc[:, "GST mph"] = nans
                ports[i].loc[:, "Buoy Source"] = outage
                continue
            # if no data exists for main buoy, switch to alternate
            elif isinstance(buoy_data, type(None)) or buoy_data.shape[0] == 0:
                buoy_data = alt_buoy_data
            # filter buoy data to correspond to the correct day
            buoy_data = buoy_data[(buoy_data["#YY"] == year) &
                        (buoy_data["MM"] == month) &
                        (buoy_data["DD"] == day)]
            converted_times = pd.to_datetime(buoy_data["#YY"] +
                                             buoy_data["MM"] +
                                             buoy_data["DD"] +
                                             buoy_data["hh"] +
                                             buoy_data["mm"],
                                             infer_datetime_format=True)
            buoy_data.loc[:, "Date/Time UTC"] = converted_times
            buoy_data.rename({"WDIR":"WDIR degT", "WSPD":"WSPD m/s",
                              "GST":"GST m/s"}, axis=1, inplace=True)
            # remove missing points from buoy data
            buoy_data = buoy_data[(buoy_data["WDIR degT"] != "MM") &
                        (buoy_data["WSPD m/s"] != "MM") &
                        (buoy_data["GST m/s"] != "MM")]
            # convert from m/s to mph and round
            buoy_data.loc[:, "WSPD mph"] = (buoy_data.loc[:, "WSPD m/s"].
                                            astype("float") * MPS_TO_MPH)
            buoy_data.loc[:, "GST mph"] = (buoy_data.loc[:, "GST m/s"].
                                           astype("float") * MPS_TO_MPH)
            buoy_data.loc[:, "WSPD mph"] = buoy_data.loc[:, "WSPD mph"].round(2)
            buoy_data.loc[:, "GST mph"] = buoy_data.loc[:, "GST mph"].round(2)
            buoys[i][id] = buoy_data[["Date/Time UTC", "WDIR degT", "WSPD mph",
                                      "GST mph"]]
            # ensure alternate buoy data is not empty
            if not (isinstance(alt_buoy_data, type(None)) or
                    alt_buoy_data.shape[0] == 0):
                # filter buoy data for current day
                alt_buoy_data = alt_buoy_data[(alt_buoy_data["#YY"] == year) &
                                              (alt_buoy_data["MM"] == month) &
                                              (alt_buoy_data["DD"] == day)]
                alt_buoy_data.loc[:, "Date/Time UTC"] = pd.to_datetime(
                                                        alt_buoy_data["#YY"] +
                                                        alt_buoy_data["MM"] +
                                                        alt_buoy_data["DD"] +
                                                        alt_buoy_data["hh"] +
                                                        alt_buoy_data["mm"],
                                                    infer_datetime_format=True)
                alt_buoy_data.rename({"WDIR":"WDIR degT", "WSPD":"WSPD m/s",
                                      "GST":"GST m/s"}, axis=1, inplace=True)
                # remove missing points from buoy data
                alt_buoy_data = alt_buoy_data[
                            (alt_buoy_data["WDIR degT"] != "MM") &
                            (alt_buoy_data["WSPD m/s"] != "MM") &
                            (alt_buoy_data["GST m/s"] != "MM")]
                # convert from m/s to mph and round
                alt_buoy_data.loc[:, "WSPD mph"] = (alt_buoy_data
                                                    .loc[:, "WSPD m/s"]
                                                    .astype("float") *
                                                    MPS_TO_MPH)
                alt_buoy_data.loc[:, "GST mph"] = (alt_buoy_data
                                                   .loc[:, "GST m/s"]
                                                   .astype("float") *
                                                   MPS_TO_MPH)
                alt_buoy_data.loc[:, "WSPD mph"] = (alt_buoy_data
                                                    .loc[:, "WSPD mph"]
                                                    .round(2))
                alt_buoy_data.loc[:, "GST mph"] = (alt_buoy_data
                                                   .loc[:, "GST mph"].round(2))
                alt_buoys[i][alt_id] = alt_buoy_data[["Date/Time UTC",
                                                      "WDIR degT",
                                                      "WSPD mph",
                                                      "GST mph"]]
            # match windspeed timestamp with closest vessel position timestamps
            input_times = None
            # set wind data based on the port and availability of main
            wind_data = buoys[i][id]
            target_times = list(wind_data["Date/Time UTC"]) # buoy timestamps
            input_times = list(ports[i]["Date/Time UTC"]) # vessel timestamps
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
                if (min_timedelta < timedelta(hours=WIND_TIME_TOL) and
                    min_timedelta_index != -1):
                    for count, k in enumerate(final_winds.keys()):
                        if count == 0:
                            source_buoy.append(str(id))
                        nearest_reading = wind_data[k].iloc[min_timedelta_index]
                        final_winds[k].append(nearest_reading)
                else:
                    # handle missing wind vals
                    for count, k in enumerate(final_winds.keys()):
                        if (isinstance(alt_buoy_data, type(None)) or
                            alt_buoy_data.shape[0] == 0):
                            if count == 0:
                                source_buoy.append("N/A")
                            final_winds[k].append(float("NaN"))
                        else:
                            alt_target_times = list(
                                               alt_buoy_data["Date/Time UTC"])
                            alt_min_timedelta = timedelta(hours=WIND_TIME_TOL)
                            alt_min_timedelta_index = -1
                            for jj in range(len(alt_target_times)):
                                delta = abs(input_times[ii] -
                                            alt_target_times[jj])
                                if delta <= timedelta(hours=WIND_TIME_TOL):
                                    if alt_min_timedelta > delta:
                                        alt_min_timedelta = delta
                                        alt_min_timedelta_index = jj
                                else:
                                    continue
                            if (alt_min_timedelta <
                                timedelta(hours=WIND_TIME_TOL) and
                                alt_min_timedelta_index != -1):
                                if count == 0:
                                    source_buoy.append(str(alt_id))
                                nearest_reading = alt_buoy_data[k].iloc[
                                                  alt_min_timedelta_index]
                                final_winds[k].append(nearest_reading)
                            else:
                                if count == 0:
                                    source_buoy.append("N/A")
                                final_winds[k].append(float("NaN"))
            for k in final_winds:
                ports[i].loc[:, k] = final_winds[k]
            ports[i].loc[:, "Buoy Source"] = source_buoy
        # filter on course ranges to isolate inbound and outbound ships only
        ports[i] = ports[i][(ports[i].Course >= course_ranges[i][0][0]) &
                            (ports[i].Course <= course_ranges[i][0][1]) |
                            (ports[i].Course >= course_ranges[i][1][0]) &
                            (ports[i].Course <= course_ranges[i][1][1])]
        ports[i].Course = round(ports[i].Course).astype("int")
        ports[i].loc[:, "Course Behavior"] = ports[i].loc[:, "Course"]
        # replace course values with general inbound and outbound behavior
        courses = {}
        for behavior, course_range in zip(course_behavior, course_ranges[i]):
            lower_bound = course_range[0]
            upper_bound = course_range[1]
            for j in range(lower_bound, upper_bound + 1):
                courses[j] = behavior
        ports[i].loc[:, "Course Behavior"] = ports[i].loc[:,
                                             "Course Behavior"].replace(
                                             courses).astype("str")
        # initialize Vessel Class column to Panamax, and update based on
        # Post-Panamax LOA ft values to minimize computation
        ports[i].loc[:, "Vessel Class"] = "Panamax"
        post_pan = ports[i].index.isin(ports[i][ports[i]["LOA ft"] > 965].index)
        ports[i].loc[:, "Vessel Class"][post_pan] = "Post-Panamax"
        # create yaw column based on difference between course and heading
        ports[i].loc[:, "Yaw deg"] = abs(ports[i].loc[:, "Course"] -
                                         ports[i].loc[:, "Heading"])
        # compute effective beam based on vessel beam, loa, and yaw
        EB = []
        loa = ports[i]["LOA ft"].values
        beam = ports[i]["Beam ft"].values
        yaw = ports[i]["Yaw deg"].values
        for l in range(ports[i].shape[0]):
            # effective beam formula derived using trigonometry and geometry
            # of vessel positions
            EB.append(round((math.cos(math.radians(90 - yaw[l])) * loa[l]) +
                            (math.cos(math.radians(yaw[l])) * beam[l])))
        ports[i].loc[:, "Effective Beam ft"] = EB
        ports[i].loc[:, "Effective Beam ft"] = ports[i].loc[:,
                                               "Effective Beam ft"].round(0)
        # remove unwanted blacklist vessels
        ports[i] = _filter_blacklisters(ports[i], blacklist)
        # create rounded DateTime column for meetpass analysis
        stamps = len(ports[i].loc[:, "Date/Time UTC"]) # number of timestamps
        round_times = ports[i].loc[:, "Date/Time UTC"].iloc[ii].floor("Min")
        ports[i].loc[:, "rounded date"] = [round_times for ii in range(stamps)]
        # run meetpass analysis and create Transit column based on results
        mp = meetpass(ports[i])
        two_way = twoway(ports[i], mp)
        ports[i]["Transit"] = "One-way Transit"
        if not isinstance(two_way, type(None)):
            two_way_indices = ports[i].index.isin(two_way.index)
            ports[i]["Transit"][two_way_indices] = "Two-way Transit"
        # reset index to clear previous pandas manipulations
        ports[i] = ports[i].reset_index()
        # total channel width for CH and SV are 1000 and 600 ft respectively,
        # but vary based on vessel class and transit condition
        channel_width = [[800, 400, 1000, 500], [600, 300, 600, 300]]
        # create % channel occupancy column for each vessel position based on
        # effective beam, transit, and corresponding channel width
        for row in range(len(ports[i])):
            vessel_class = ports[i].loc[row, "Vessel Class"]
            transit_type = ports[i].loc[row, "Transit"]
            eff_beam = ports[i].loc[row, "Effective Beam ft"]
            if ((vessel_class == "Post-Panamax") &
                (transit_type == "One-way Transit")):
                occ = (eff_beam / channel_width[i][0]) * 100
                ports[i].loc[row, "% Channel Occupied"] = round(occ, 2)
            elif ((vessel_class == "Post-Panamax") &
                  (transit_type == "Two-way Transit")):
                occ = (eff_beam / channel_width[i][1]) * 100
                ports[i].loc[row, "% Channel Occupied"] = round(occ, 2)
            elif ((vessel_class == "Panamax") &
                  (transit_type == "One-way Transit")):
                occ = (eff_beam / channel_width[i][2]) * 100
                ports[i].loc[row, "% Channel Occupied"] = round(occ, 2)
            elif ((vessel_class == "Panamax") &
                  (transit_type == "Two-way Transit")):
                occ = (eff_beam / channel_width[i][3]) * 100
                ports[i].loc[row, "% Channel Occupied"] = round(occ, 2)
            else:
                sys.stderr.write("Error: Undefined vessel class and " +
                                 "transit combination...\n")
                ports[i].loc[row, "% Channel Occupied"] = float("NaN")
        # save current format of data as all_res to be used for all positions
        all_res = ports[i]
        # remove sections of channel where ships turn
        if i % 2:
            all_res = all_res[(all_res.Latitude <= 32.02838) &
                                  (all_res.Latitude >= 31.9985) |
                                  (all_res.Latitude <= 31.99183)]
        else:
            all_res = all_res[all_res.Latitude >= 32.667473]
        # compute mean speed and identify max speed per vessel
        mean = pd.DataFrame(ports[i].groupby(["Name", "MMSI"])["VSPD kn"]
               .mean()).rename({"VSPD kn": "Mean Speed kn"}, axis=1).round(1)
        maxes = pd.DataFrame(ports[i].groupby(["Name", "MMSI"])["VSPD kn"]
                .max()).rename({"VSPD kn": "Max Speed kn"}, axis=1)
        merged_speeds = maxes.merge(mean, on=["Name", "MMSI"])
        max_dict = merged_speeds["Max Speed kn"].to_dict()
        columns = {"Longitude":[], "Latitude":[], "Date/Time UTC":[],
                   "LOA ft":[], "Course":[], "AIS Type":[], "WSPD mph":[],
                   "GST mph":[], "WDIR degT":[], "Buoy Source":[], "Beam ft":[],
                   "Heading":[], "Course Behavior":[], "Effective Beam ft":[],
                   "Vessel Class":[], "Location":[], "Yaw deg":[], "Transit":[],
                   "% Channel Occupied":[]}
        # grab remaining data based on max speed position
        for key, value in max_dict.items():
            for k in columns.keys():
                columns[k].append(ports[i][(ports[i].Name == key[0]) &
                                 (ports[i]["VSPD kn"] == value)][k].iloc[0])
        for key in columns.keys():
            merged_speeds[key] = columns[key]
        merged_speeds = merged_speeds.reset_index()
        # save result to variable and sort on max speeds
        fold_res = merged_speeds
        fold_res.sort_values("Max Speed kn", ascending=False, inplace=True)
        # return max and mean positional data in specified order
        fold_res = fold_res[["Date/Time UTC", "Name", "MMSI", "Max Speed kn",
                             "Mean Speed kn", "LOA ft", "Beam ft",
                             "Vessel Class", "AIS Type", "Course", "Heading",
                             "Course Behavior", "Yaw deg", "Effective Beam ft",
                             "WDIR degT", "WSPD mph", "GST mph", "Buoy Source",
                             "Location", "Latitude", "Longitude", "Transit",
                             "% Channel Occupied"]]
        # return positional data in specified order
        all_res = all_res[["Name", "MMSI", "VSPD kn", "WSPD mph", "Transit",
                           "% Channel Occupied", "Yaw deg", "Effective Beam ft",
                           "LOA ft", "Beam ft", "Vessel Class", "AIS Type",
                           "Course", "Heading", "Course Behavior", "WDIR degT",
                           "GST mph", "Buoy Source", "Location", "Latitude",
                           "Longitude", "Date/Time UTC"]]
        # save two copies of daily vmr for each port, one for all vessel
        # positions and one for maximum vesel speed positions
        ports[i] = [fold_res, all_res]
    return ports[0], ports[1] # ch, sv
