# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Detect meeting and passing instances between ships.

from process_maritime_data import *
from datetime import timedelta

import pandas as pd
import numpy as np
import scipy
import math

MEET_PASS_TIME_TOL = 1 # in hours
MIN_DISTANCE = 20000 # in feet

def _radians(num):
    """
    Converts number to radians.
    """
    return num * math.pi / 180

def _calc_dist(lat1, long1, lat2, long2):
    """
    Computes distance in feet between two points using Pythagoras' theorem on an
    equirectuangular projection of the Earth.
    """
    x = _radians(long2 - long1) * math.cos(_radians((lat1 + lat2) / 2))
    y = _radians(lat2 - lat1)
    d = math.sqrt(x**2 + y**2) * 20902000 # Multuply by radius of Earth in feet
    return round(d, 2)

def _meetpass_helper(df, time_tolerance):
    """Identifies potential instances of meeting and passing. If the timestamps
    cooresponding to a pair of distinct vessel positions are within the limit
    and have opposing courses, then flag those particular movement entries.

    Args:
        df: Vessel movement DataFrame.
        time_tolerance: Maximum (inclusive) acceptable time delta -- in minutes.

    Returns:
        Vessel movement DataFrame containing only data points flagged as
        potentially meeting and passing.
    """
    # sorts timestamps such that entry channel data is in chronological order
    chrono_df = df.sort_values("Date/Time UTC")
    mmsi = list(chrono_df.MMSI)
    timestamp = list(chrono_df["Date/Time UTC"])
    course = list(chrono_df["Course Behavior"])
    potential_times = []
    for i in range(len(mmsi) - 1):
        if mmsi[i] != mmsi[i + 1]:
            if ((timestamp[i + 1] - timestamp[i]) <=
                timedelta(minutes=time_tolerance)):
                if course[i] != course[i + 1]:
                    potential_times.append(timestamp[i])
                    potential_times.append(timestamp[i + 1])
                    sorted(potential_times)
    res = chrono_df[chrono_df["Date/Time UTC"].isin(potential_times)]
    return res

def meetpass(df):
    """Identifies instances of meeting and passing between ships. Records moment
    of closest approach by comparing variations in timestamps as well as
    by minimizing distances.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Dictionary of verified meeting and passing encounters.
    """
    rounded_df = df.copy()
    rounded_df["Date/Time UTC"] = df["Date/Time UTC"].values.astype("<M8[m]")
    flagged = _meetpass_helper(df, MEET_PASS_TIME_TOL).groupby(
                             ["MMSI", "Course Behavior", pd.Grouper(
                              key="Date/Time UTC", freq="min")])[[
                              "Date/Time UTC"]].size()
    # potential_encs should contain all the flagged times
    potential_encs = {}
    for entry in flagged.index.unique(0):
        potential_encs[entry] = flagged.xs(entry, level=0).index
    potential_encs.items()
    true_encs = {}
    # TODO: minimize comparison operations between timestamps
    while len(potential_encs):
        item = potential_encs.popitem()
        cur_key = item[0]
        cur_val = item[1]
        i = 0
        while not cur_val.empty:
            this_course = cur_val.get_level_values(0)[0]
            this_time = cur_val.get_level_values(1)[0]
            matching_keys = (rounded_df.MMSI == cur_key)
            matching_times = (rounded_df["Date/Time UTC"] == this_time)
            this_lat = rounded_df[matching_keys &
                                  matching_times].Latitude.values[0].round(5)
            this_long = rounded_df[matching_keys &
                                   matching_times].Longitude.values[0].round(5)
            this_class = rounded_df[matching_keys &
                                    matching_times]["Vessel Class"].values[0]
            for inner_key, inner_val in potential_encs.items():
                for j, that in enumerate(inner_val):
                    that_course = that[0]
                    that_time = that[1]
                    matching_keys = (rounded_df.MMSI == inner_key)
                    matching_times = (rounded_df["Date/Time UTC"] == that_time)
                    that_lat = rounded_df[matching_keys &
                                          matching_times
                                         ].Latitude.values[0].round(5)
                    that_long = rounded_df[matching_keys &
                                           matching_times
                                          ].Longitude.values[0].round(5)
                    that_class = rounded_df[matching_keys &
                                            matching_times
                                           ]["Vessel Class"].values[0]
                    if ((this_time == that_time) and
                        (this_course != that_course)):
                        dist = _calc_dist(this_lat, this_long,
                                          that_lat, that_long)
                        # check if true encounter (within minimum distance)
                        if MIN_DISTANCE >= dist:
                            fragments = sorted([cur_key, inner_key])
                            if cur_key == fragments[0]:
                                fragments += [this_class, that_class,
                                              this_course, that_course]
                            else:
                                fragments += [that_class, this_class,
                                              that_course, this_course]
                            key = tuple(fragments)
                            if key not in true_encs:
                                # create new entry
                                true_encs[key] = (this_time, dist)
                            else:
                                # minimize distance (update)
                                if true_encs[key][1] > dist:
                                    true_encs[key] = (this_time, dist)
            multiindex = cur_val.delete(0)
            cur_val = multiindex
            i += 1
    return true_encs

def _twoway_helper(df, mmsi, course, enc_time):
    """Isolates entries up to and including encounter time, based on specified
    vessel MMSI and course.
    """
    res = df[(df.MMSI == mmsi) & (df["Course Behavior"] == course) &
             (df["rounded date"] <= enc_time)]
    return res

def twoway(df, true_encs):
    """Identifies and labels two way transit conditions within the data.

    Args:
        df: Vessel movement DataFrame.
        true_encs: Dictionary of verified meeting and passing encounters.

    Returns:
        Vessel movement DataFrame containing only entries that should be
        labelled as two way transit. (IMPORTANT) Preserves indices from original
        DataFrame, df.
    """
    two_way = []
    for key in true_encs:
        this_mmsi = key[0]
        that_mmsi = key[1]
        this_course = key[4]
        that_course = key[5]
        enc_time = true_encs[key][0]
        two_way.append(_twoway_helper(df, this_mmsi, this_course, enc_time))
        two_way.append(_twoway_helper(df, that_mmsi, that_course, enc_time))
    if not two_way:
        return
    return pd.concat(two_way)
