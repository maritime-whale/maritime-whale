# this script will parse all VMR emails retrieving all data for the entire season.
# and filter/clean said data but only leaving sub-panamax vessels at both
# charleston and savannah. it will also fold said data into max and mean speeds
# for each of the vessels that appear throughout the season.


# step 1, retrieve data from VMR emails and store it as df

# step 2, filter daily VMR for blacklist ships as well as all normal cleaning
# schemes we normally deploy, but only capture Subpan vessels >= 492 and < 656 feet
# no need for meetpass analysis here
# do we need winds?

# step 3, create four master CSVs similar to what exists currently, all Positions
# and max speeds for ch and sv, but this time only for Subpan classes
#        subpan-master-ch.csv
#        subpan-master-ch-max.csv
#        subpan-master-sv.csv
#        subpan-master-sv-max.csv

# step 4, save above csv's into html/riwhale.github.io

from process_maritime_data import *
from match_wind_data import *
from datetime import *
from meet_and_pass import *
from fetch_vessel_data import *

import pandas as pd
import math
import sys

SUB_PANAMAX = (492, 656) # threshold in feet

def _wrangle_vmr(df, rename):
    """Rounds, renames, and sanitizes vessel movment DataFrame. Creates new
    columns.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Cleaned vessel movement report DataFrame.
    """
    df.rename(rename, axis=1, inplace=True)
    df.loc[:, "LOA ft"] = (df.loc[:, "A"] + df.loc[:, "B"]) * M_TO_FT
    df.loc[:, "LOA ft"] = df.loc[:, "LOA ft"].round(0)
    df.loc[:, "Beam ft"] = (df.loc[:, "C"] + df.loc[:, "D"]) * M_TO_FT
    df.loc[:, "Beam ft"] = df.loc[:, "Beam ft"].round(0)
    df.loc[:, "Latitude"] = df.loc[:, "Latitude"].round(5)
    df.loc[:, "Longitude"] = df.loc[:, "Longitude"].round(5)
    df = _sanitize_vmr(df)
    # filter only for sub-panamax class vessels
    df = df.loc[(df.loc[:, "LOA ft"] >= SUB_PANAMAX[0]) &
                (df.loc[:, "LOA ft"] < SUB_PANAMAX[1]), :]
    df.loc[:, "Date/Time UTC"] = df.loc[:, "Date/Time UTC"].str.strip("UTC")
    df.loc[:, "Date/Time UTC"] = pd.to_datetime(df.loc[:, "Date/Time UTC"])
    df = df.loc[:, (["Date/Time UTC", "Name", "MMSI", "LOA ft", "Latitude",
                     "Longitude", "Course", "AIS Type", "Heading", "VSPD kn",
                     "Beam ft"])]
    return df

def _fold_vmr(ports, i):
    """Reduces movement report to a DataFrame with a single entry for each
    vessel at the point of it's maximum speed in the channel. Includes a column
    with the vessel's mean speed.
    """
    mean = pd.DataFrame(ports[i].groupby(["Name", "MMSI"])["VSPD kn"]
           .mean()).rename({"VSPD kn": "Mean Speed kn"}, axis=1).round(1)
    maxes = pd.DataFrame(ports[i].groupby(["Name", "MMSI"])["VSPD kn"]
            .max()).rename({"VSPD kn": "Max Speed kn"}, axis=1)
    merged_speeds = maxes.merge(mean, on=["Name", "MMSI"])
    max_dict = merged_speeds.loc[:, "Max Speed kn"].to_dict()
    columns = {"Longitude":[], "Latitude":[], "Date/Time UTC":[],
               "LOA ft":[], "Course":[], "AIS Type":[], "WSPD mph":[],
               "GST mph":[], "WDIR degT":[], "Buoy Source":[], "Beam ft":[],
               "Heading":[], "Course Behavior":[], "Effective Beam ft":[],
               "Class":[], "Location":[], "Yaw deg":[]}
    # grab remaining data based on max speed position
    for key, value in max_dict.items():
        for k in columns.keys():
            columns[k].append(ports[i][(ports[i].loc[:, "Name"] == key[0]) &
                             (ports[i].loc[:, "VSPD kn"] == value)][k].iloc[0])
    for key in columns.keys():
        merged_speeds[key] = columns[key]
    merged_speeds = merged_speeds.reset_index()
    fold_res = merged_speeds
    fold_res.sort_values("Max Speed kn", ascending=False, inplace=True)
    return fold_res

def _add_vessel_class(df):
    """Creates 'Class' column based on vessel LOA ft."""
    df.loc[:, "Class"] = "Sub-Panamax"
    return df

def process_report(path):
    """Processes data from vessel movement report. Adds data from wind buoys,
    performs meeting and passing analysis. Creates other relevant columns.

    Args:
        path: Relative path to raw vessel movement report (CSV).

    Returns:
        Two pairs of two DataFrames cooresponding to the movement report.
        The first pair of DataFrames contains all vessel movements belonging to
        Charleston and Savannah, respectively. The second pair of DataFrames
        stores the vessel movement entries at which each vessel achieved
        its maximum speed. Again, the first DataFrame in the pair belongs to
        Charleston and the second DataFrame belongs to Savannah.
    """
    blacklist = [int(mmsi) for mmsi in open("../cache/blacklist.txt",
                                            "r").readlines()]
    df = pd.read_csv(path)
    df = _wrangle_vmr(df, {"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
                           "LATITUDE": "Latitude", "LONGITUDE": "Longitude",
                           "SPEED": "VSPD kn", "COURSE": "Course", "HEADING":
                           "Heading", "AIS TYPE": "AIS Type"})
    ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
    sv_course_ranges = ((100, 160), (280, 340)) # (outbound, inbound)
    # longitudinal channel midpoint for Charleston and Savannah respectively
    channel_midpoint = ((-79.74169), (-80.78522))
    course_ranges = (ch_course_ranges, sv_course_ranges)
    ports = [None, None] # ch, sv
    # Charleston NOAA wind buoy ID (41004)
    # Savannah NOAA wind buoy ID (41008)
    buoys = [{"41004":None}, {"41008":None}] # main wind buoys
    alt_buoys = [{"41008":None}, {"41004":None}] # alternate wind buoys
    # split data into Charleston and Savannah DataFrames based on latitude
    for i in range(len(ports)):
        ch_df = (df.loc[:, "Latitude"] >= 32.033)
        sv_df = (df.loc[:, "Latitude"] < 32.033)
        ports[i] = df[ch_df] if (i == 0) else df[sv_df]
        # if there is no vessel data on a given day (e.g. major holidays)
        # return empty DataFrames
        if not len(ports[i]):
            empty = pd.DataFrame({"Date/Time UTC":[], "Name":[], "MMSI":[],
                                  "Max Speed kn":[], "Mean Speed kn":[],
                                  "LOA ft":[], "Beam ft":[], "Class":[],
                                  "AIS Type":[], "Course":[], "Heading":[],
                                  "Course Behavior":[], "Yaw deg":[],
                                  "Effective Beam ft":[], "WDIR degT":[],
                                  "WSPD mph":[], "GST mph":[], "Buoy Source":[],
                                  "Location":[], "Latitude":[], "Longitude":[])
            ports[i] = [empty, empty]
            continue
        ports[i].loc[:, "Location"] = "Nearshore"
        off_row = (ports[i].loc[:, "Longitude"] > channel_midpoint[i])
        off_loc = ports[i].loc[off_row, :].index
        offshore_indices = ports[i].index.isin(off_loc)
        ports[i].loc[offshore_indices, "Location"] = "Offshore"
        ports[i] = add_wind(ports, i, buoys, alt_buoys)
        ports[i] = _course_behavior(ports[i], course_ranges[i])
        ports[i] = _add_vessel_class(ports[i])
        # create yaw column based on difference between course and heading
        ports[i].loc[:, "Yaw deg"] = abs(ports[i].loc[:, "Course"] -
                                         ports[i].loc[:, "Heading"])
        # compute effective beam based on vessel beam, loa, and yaw
        eff_beam = []
        loa = ports[i].loc[:, "LOA ft"].values
        beam = ports[i].loc[:, "Beam ft"].values
        yaw = ports[i].loc[:, "Yaw deg"].values
        for l in range(ports[i].shape[0]):
            # effective beam formula derived using trigonometry and geometry
            # of vessel positions
            eff_beam.append(round((math.cos(math.radians(90 - yaw[l])) *
                            loa[l]) + (math.cos(math.radians(yaw[l])) *
                            beam[l])))
        ports[i].loc[:, "Effective Beam ft"] = eff_beam
        ports[i].loc[:, "Effective Beam ft"] = ports[i].loc[:,
                                               "Effective Beam ft"].round(0)
        # remove unwanted blacklist vessels
        ports[i] = _filter_blacklisters(ports[i], blacklist)
        # save current format of data as all_res to be used for all positions
        all_res = ports[i]
        # remove sections of channel where ships turn
        if i % 2:
            all_res = all_res[(all_res.loc[:, "Latitude"] <= 32.02838) &
                              (all_res.loc[:, "Latitude"] >= 31.9985) |
                              (all_res.loc[:, "Latitude"] <= 31.99183)]
        else:
            all_res = all_res[all_res.loc[:, "Latitude"] >= 32.667473]
        fold_res = _fold_vmr(ports, i)
        # return max and mean positional data in specified order
        fold_res = fold_res.loc[:, ("Date/Time UTC", "Name", "MMSI",
                                    "Max Speed kn", "Mean Speed kn", "LOA ft",
                                    "Beam ft", "Class", "AIS Type", "Course",
                                    "Heading", "Course Behavior", "Yaw deg",
                                    "Effective Beam ft", "WDIR degT",
                                    "WSPD mph", "GST mph", "Buoy Source",
                                    "Location", "Latitude", "Longitude")]
        # return positional data in specified order
        all_res = all_res.loc[:, ("Name", "MMSI", "VSPD kn", "WSPD mph",
                                  "Yaw deg", "Effective Beam ft", "LOA ft",
                                  "Beam ft", "Class", "AIS Type", "Course",
                                  "Heading", "Course Behavior", "WDIR degT",
                                  "GST mph", "Buoy Source", "Location",
                                  "Latitude", "Longitude", "Date/Time UTC")]
        # save two copies of daily vmr for each port, one for all vessel
        # positions and one for maximum vessel speed positions
        ports[i] = [fold_res, all_res]
    return ports[0], ports[1] # ch, sv
