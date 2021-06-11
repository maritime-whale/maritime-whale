import pandas as pd
import math
import sys
import os

import plotly.figure_factory as ff
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import text

AUTO_BLACKLIST = [30, 31, 32, 33, 34, 35, 36, 37, 51, 52, 53, 55, 57, 58, 59]
blacklist = [367771000, 368247000, 367863000, 367336000, 338931000, 367049000,
             368413000, 369928000, 367932000, 367501540]
SUB_PANAMAX = 656 # threshold in feet
M_TO_FT = 3.28 # meters to feet (conversion)
ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
sv_course_ranges = ((100, 160), (280, 340)) # (outbound, inbound)

def _sanitize_vmr(df):
    """Filters entries with '511' error, impossibly high speed, abnormally
    high vessel width, as well as singletons (only one entry) from vessel
    movement DataFrame.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Sanitized vessel movement report DataFrame.
    """
    df = df.loc[~df.index.isin(df[df.loc[:, "Beam ft"] >= 500].index), :]
    df = df.loc[~df.index.isin(df[df.loc[:, "Course"] == 511].index), :]
    df = df.loc[~df.index.isin(df[df.loc[:, "Heading"] == 511].index), :]
    df = df.loc[~df.index.isin(df[df.loc[:, "VSPD kn"] >= 30].index), :]
    singleton = (df.loc[:, "MMSI"].value_counts() == 1)
    single_mmsi = df.loc[:, "MMSI"].value_counts()[singleton].index.values
    df = df.loc[~df.loc[:, "MMSI"].isin(single_mmsi), :]
    return df
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
    # filter out sub-panamax class vessels
    df = df.loc[df.loc[:, "LOA ft"] < SUB_PANAMAX, :]
    df.loc[:, "Date/Time UTC"] = df.loc[:, "Date/Time UTC"].str.strip("UTC")
    df.loc[:, "Date/Time UTC"] = pd.to_datetime(df.loc[:, "Date/Time UTC"])
    df = df.loc[:, (["Date/Time UTC", "Name", "MMSI", "LOA ft", "Latitude",
                     "Longitude", "Course", "AIS Type", "Heading", "VSPD kn",
                     "Beam ft"])]
    return df
def _filter_blacklisters(df, blacklist):
    """Checks vessel AIS types and ommits blacklisted vessel types from the
    filtered data. Appends ommitted vessels' MMSI's to blacklist.txt.

    Args:
        df: Vessel movement DataFrame.

    Returns:
        Filtered vessel movement DataFrame.
    """
    df = df.loc[~df.loc[:, "MMSI"].isin(blacklist), :]
    new_blacklisters = []
    for j in range(df.shape[0]):
        if df.iloc[j]["AIS Type"] in AUTO_BLACKLIST:
            new_blacklisters.append(df.iloc[j]["MMSI"])
    # with open("../cache/blacklist.txt", "a") as f:
    #     contents = [str(mmsi) for mmsi in new_blacklisters]
    #     if contents:
    #         f.write("\n".join(contents) + "\n")
    df = df.loc[~df.loc[:, "MMSI"].isin(new_blacklisters), :]
    return df
def _course_behavior(df, ranges):
    """Creates 'Course Behavior' column based on channel specific course ranges.
    """
    course_behavior = ("Outbound", "Inbound")
    # filter on course ranges to isolate inbound and outbound ships only
    df = df[(df.loc[:, "Course"] >= ranges[0][0]) &
            (df.loc[:, "Course"] <= ranges[0][1]) |
            (df.loc[:, "Course"] >= ranges[1][0]) &
            (df.loc[:, "Course"] <= ranges[1][1])]
    df.loc[:, "Course"] = round(df.loc[:, "Course"]).astype("int")
    df.loc[:, "Course Behavior"] = df.loc[:, "Course"].copy()
    # replace course values with general inbound and outbound behavior
    courses = {}
    for behavior, bounds in zip(course_behavior, ranges):
        lower_bound = bounds[0]
        upper_bound = bounds[1]
        for j in range(lower_bound, upper_bound + 1):
            courses[j] = behavior
    df.loc[:, "Course Behavior"] = (df.loc[:, "Course Behavior"]
                                    .replace(courses).astype("str"))
    return df


df = pd.read_csv("../temp/raw_vmrs.csv")
df = _wrangle_vmr(df, {"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
                       "LATITUDE": "Latitude", "LONGITUDE": "Longitude",
                       "SPEED": "VSPD kn", "COURSE": "Course", "HEADING":
                       "Heading", "AIS TYPE": "AIS Type"})
df = _filter_blacklisters(df, blacklist)
# df = _course_behavior(df, )
df.shape
ch_df = df[(df.loc[:, "Latitude"] >= 32.033)]
sv_df = df[(df.loc[:, "Latitude"] < 32.033)]
len(ch_df)
len(sv_df)

ch_df = _course_behavior(ch_df, ch_course_ranges)
sv_df = _course_behavior(sv_df, sv_course_ranges)

len(ch_df.groupby(["MMSI", "Course Behavior"]).mean())

print("charleston post-pan made 414 transits")
print("charleston pan made 259 transits")
print("charleston sub-pan made 365 transits")
414+259+365
414/1038
259/1038
365/1038


len(sv_df.groupby(["MMSI", "Course Behavior"]).mean())

497+550+234
df.shape
ch_df.shape[0] + sv_df.shape[0]
df.shape[0] - (ch_df.shape[0] + sv_df.shape[0])



sv_df.to_csv("../html/riwhale.github.io/sub_pan_sv.csv")
ch_df.to_csv("../html/riwhale.github.io/sub_pan_ch.csv")
sv_df.to_excel("../html/riwhale.github.io/sub_pan_sv.xlsx")
ch_df.to_excel("../html/riwhale.github.io/sub_pan_ch.xlsx")
