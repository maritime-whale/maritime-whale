# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Generates season-to-date dashboard from DataFrame. Centralized view for
# statistics of interest.

import pandas as pd

def dashboard(df):
    """Generate DataFrame containing relevant port entrance statistics."""
    panamax = (df.loc[:, "Class"] == "Panamax")
    post_panamax = (df.loc[:, "Class"] == "Post-Panamax")
    nearshore = (df.loc[:, "Location"] == "Nearshore")
    offshore = (df.loc[:, "Location"] == "Offshore")
    inbound = (df.loc[:, "Course Behavior"] == "Inbound")
    outbound = (df.loc[:, "Course Behavior"] == "Inbound")
    dat = {"Proportion<br>of Transits":[
           str(round(sum(panamax) / len(df) * 100, 2)) + "%",
           str(round(sum(post_panamax) / len(df) * 100, 2)) + "%", "100%"
           ],
           "Compliance<br>Rate":[
           str(round(sum(panamax & (df.loc[:, "VSPD kn"] <= 10)) /
                     sum(panamax) * 100, 2)) + "%",
           str(round(sum(post_panamax & (df.loc[:, "VSPD kn"] <= 10)) /
                     sum(post_panamax) * 100, 2)) + "%",
           str(round(sum(df.loc[:, "VSPD kn"] <= 10) / len(df) * 100, 2)) + "%"
           ],
           "Mean<br>VSPD":[
           str(round(df[panamax].loc[:, "VSPD kn"].mean(), 2)) + " kn",
           str(round(df[post_panamax].loc[:, "VSPD kn"].mean(), 2)) + " kn",
           str(round(df.loc[:, "VSPD kn"].mean(), 2)) + " kn"
           ],
           "Nearshore<br>Median VSPD":[
           str(round(df[nearshore & panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[nearshore & post_panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[nearshore].loc[:, "VSPD kn"].median(), 2)) + " kn"
           ],
           "Offshore<br>Median VSPD":[
           str(round(df[offshore & panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[offshore & post_panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[offshore].loc[:, "VSPD kn"].median(), 2)) + " kn"
           ],
           "Inbound<br>Median VSPD":[
           str(round(df[inbound & panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[inbound & post_panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[inbound].loc[:, "VSPD kn"].median(), 2)) + " kn"
           ],
           "Outbound<br>Median VSPD":[
           str(round(df[outbound & panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[outbound & post_panamax].loc[:, "VSPD kn"].median(), 2)) +
           " kn",
           str(round(df[outbound].loc[:, "VSPD kn"].median(), 2)) + " kn"
           ],
           "VSPD-WSPD<br>Correlation":[
           str(round(df[panamax].dropna().loc[:, ("VSPD kn", "WSPD mph")].corr()
           .iloc[0][1], 2)),
           str(round(df[post_panamax].dropna().loc[:,
           ("VSPD kn", "WSPD mph")].corr().iloc[0][1], 2)),
           str(round(df.dropna().loc[:,
           ("VSPD kn", "WSPD mph")].corr().iloc[0][1], 2))
           ]
          }
    index = ["Panamax", "Post-Panamax", "Combined"]
    return pd.DataFrame(dat, index)
