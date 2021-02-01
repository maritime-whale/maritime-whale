# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Matches wind data according to buoy availability, port entrance, and time.

from datetime import *

import pandas as pd

WIND_TIME_TOL = 3 # tolerance in hours
MPS_TO_MPH = 2.237 # meters per sec to miles per hour (conversion)

def _wrangle_winds(buoys, buoy_data, i, id, year, month, day):
    """Grabs wind data for specified day, removes missing values, performs
    unit conversions, and rounds columns.
    """
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
    return buoys[i][id]


def add_wind(ports, i, buoys, alt_buoys):
    """Holy fuck...

    Args:
        ports: Vessel movement DataFrame?
        i:
        buoys:
        alt_buots:

    Returns:
        Vessel movement DataFrame with winds?
    """
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
        buoys[i][id] = _wrangle_winds(buoys, buoy_data, i, id, year, month, day)
        # ensure alternate buoy data is not empty
        if not (isinstance(alt_buoy_data, type(None)) or
                alt_buoy_data.shape[0] == 0):
            alt_buoys[i][alt_id] = _wrangle_winds(alt_buoys, alt_buoy_data, i,
                                                  alt_id, year, month, day)
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
    return ports[i]
