#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Generate season-to-date dashboard from DataFrame. Centralized view for
# statistics of interest.

import pandas as pd

def dashboard(df):
    """Computes relevant statistics for port entrance broken up by vessel class.

    Args:
        df: Pandas DataFrame with multiple days of vessel and wind data.

    Returns:
        Pandas DataFrame with vessel statistics.

    """
    panamax = (df["Vessel Class"] == "Panamax")
    post_panamax = (df["Vessel Class"] == "Post-Panamax")
    nearshore = (df["Location"] == "Nearshore")
    offshore = (df["Location"] == "Offshore")
    inbound = (df["Course Behavior"] == "Inbound")
    outbound = (df["Course Behavior"] == "Inbound")
    dat = {"Proportion<br>of Transits":[
           str(round(sum(panamax) / len(df) * 100, 2)) + "%",
           str(round(sum(post_panamax) / len(df) * 100, 2)) + "%", "100%"
           ],
           "Compliance<br>Rate":[
           str(round(sum(panamax & (df["VSPD kn"] <= 10)) /
                     sum(panamax) * 100, 2)) + "%",
           str(round(sum(post_panamax & (df["VSPD kn"] <= 10)) /
                     sum(post_panamax) * 100, 2)) + "%",
           str(round(sum(df["VSPD kn"] <= 10) / len(df) * 100, 2)) + "%"
           ],
           "Mean<br>VSPD":[
           str(round(df[panamax]["VSPD kn"].mean(), 2)) + " kn",
           str(round(df[post_panamax]["VSPD kn"].mean(), 2)) + " kn",
           str(round(df["VSPD kn"].mean(), 2)) + " kn"
           ],
           "Nearshore<br>Median VSPD":[
           str(round(df[nearshore & panamax]["VSPD kn"].median(), 2)) + " kn",
           str(round(df[nearshore & post_panamax]["VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[nearshore]["VSPD kn"].median(), 2)) + " kn"
           ],
           "Offshore<br>Median VSPD":[
           str(round(df[offshore & panamax]["VSPD kn"].median(), 2)) + " kn",
           str(round(df[offshore & post_panamax]["VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[offshore]["VSPD kn"].median(), 2)) + " kn"
           ],
           "Inbound<br>Median VSPD":[
           str(round(df[inbound & panamax]["VSPD kn"].median(), 2)) + " kn",
           str(round(df[inbound & post_panamax]["VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[inbound]["VSPD kn"].median(), 2)) + " kn"
           ],
           "Outbound<br>Median VSPD":[
           str(round(df[outbound & panamax]["VSPD kn"].median(), 2)) + " kn",
           str(round(df[outbound & post_panamax]["VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[outbound]["VSPD kn"].median(), 2)) + " kn"
           ],
           "VSPD-WSPD<br>Correlation":[
           str(round(df[panamax].dropna()[["VSPD kn", "WSPD mph"]].corr()
           .iloc[0][1], 2)),
           str(round(df[post_panamax].dropna()[["VSPD kn", "WSPD mph"]].corr()
           .iloc[0][1], 2)),
           str(round(df.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2))
           ]
          }
    index = ["Panamax", "Post-Panamax", "Combined"]
    return pd.DataFrame(dat, index)
