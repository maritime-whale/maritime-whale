import pandas as pd

def dashboard(df):

    dat = {"Proportion<br> of Transits":[str(round(sum(df["Vessel Class"] == "Panamax") / len(df) * 100, 2)) + "%",
                                     str(round(sum(df["Vessel Class"] == "Post-Panamax") / len(df) * 100, 2)) + "%",
                                     "100%"],

          "Compliance <br> Rate":[str(round(sum((df["Vessel Class"] == "Panamax") & (df["VSPD kn"] <= 10)) / sum(df["Vessel Class"] == "Panamax") * 100, 2)) + "%",
                             str(round(sum((df["Vessel Class"] == "Post-Panamax") & (df["VSPD kn"] <= 10)) / sum(df["Vessel Class"] == "Post-Panamax") * 100, 2)) + "%",
                             str(round(sum(df["VSPD kn"] <= 10) / len(df) * 100, 2)) + "%"],

           "Mean <br> VSPD":[str(round(df[df["Vessel Class"] == "Panamax"]["VSPD kn"].mean(), 2)) + " kn",
                        str(round(df[df["Vessel Class"] == "Post-Panamax"]["VSPD kn"].mean(), 2)) + " kn",
                        str(round(df["VSPD kn"].mean(), 2)) + " kn"],

          "Nearshore<br> Median VSPD":[str(round(df[(df["Location"] == "Nearshore") & (df["Vessel Class"] == "Panamax")]["VSPD kn"].median(),2)) + " kn",
                                    str(round(df[(df["Location"] == "Nearshore") & (df["Vessel Class"] == "Post-Panamax")]["VSPD kn"].median(),2)) + " kn",
                                    str(round(df[df["Location"] == "Nearshore"]["VSPD kn"].median(),2)) + " kn"],

          "Offshore<br> Median VSPD":[str(round(df[(df["Location"] == "Offshore") & (df["Vessel Class"] == "Panamax")]["VSPD kn"].median(),2)) + " kn",
                                   str(round(df[(df["Location"] == "Offshore") & (df["Vessel Class"] == "Post-Panamax")]["VSPD kn"].median(),2)) + " kn",
                                   str(round(df[df["Location"] == "Offshore"]["VSPD kn"].median(),2)) + " kn"],

          "Inbound<br> Median VSPD":[str(round(df[(df["Course Behavior"] == "Inbound") & (df["Vessel Class"] == "Panamax")]["VSPD kn"].median(),2)) + " kn",
                                  str(round(df[(df["Course Behavior"] == "Inbound") & (df["Vessel Class"] == "Post-Panamax")]["VSPD kn"].median(),2)) + " kn",
                                  str(round(df[df["Course Behavior"] == "Inbound"]["VSPD kn"].median(),2)) + " kn"],

          "Outbound<br> Median VSPD":[str(round(df[(df["Course Behavior"] == "Outbound") & (df["Vessel Class"] == "Panamax")]["VSPD kn"].median(),2)) + " kn",
                                   str(round(df[(df["Course Behavior"] == "Outbound") & (df["Vessel Class"] == "Post-Panamax")]["VSPD kn"].median(),2)) + " kn",
                                   str(round(df[df["Course Behavior"] == "Outbound"]["VSPD kn"].median(),2)) + " kn"],

          "VSPD-WSPD <br>Correlation":[str(round(df[df["Vessel Class"] == "Panamax"].dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                   str(round(df[df["Vessel Class"] == "Post-Panamax"].dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2)),
                                   str(round(df.dropna()[["VSPD kn", "WSPD mph"]].corr().iloc[0][1], 2))]
                                   }

    index = ["Panamax", "Post-Panamax", "Combined"]

    return pd.DataFrame(dat, index)
