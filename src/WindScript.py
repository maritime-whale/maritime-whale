import pandas as pd
import numpy as np
import glob
import os

# USEFUL SENSOR INFO (DO NOT DELETE):
# 41004 ch off 32.501 /  -79.099
# 41008 sv off 31.400 / -80.866
# 41029 ch near 32.803 /  -79.624
# 41033 sv near 32.279 / -80.406
# curl "https://www.ndbc.noaa.gov/view_text_file.php?filename=41004h2013.txt.gz&dir=data/historical/stdmet/" -o "../../WindBuoys/chOff/2013.txt"

buoys = (("41004", "chOff"), ("41008", "svOff"), ("41029", "chNear"), ("41033", "svNear"))
for buoy in buoys:
    for year in range(2009, 2020):
        os.system("curl 'https://www.ndbc.noaa.gov/view_text_file.php?filename=" + buoy[0] + "h" +
                  str(year) + ".txt.gz&dir=data/historical/stdmet/' -o '../../WindBuoys/" + buoy[1] + "/" + str(year) + ".txt'")

sub = ["/chNear", "/chOff", "/svNear", "/svOff"]
for path in sub:
    targets = []
    main_path = "../../WindBuoys" + path + "/*"
    dat = []
    years = []
    for filename in sorted(glob.glob(main_path)):
        if "summary" in filename:
            continue
        try:
            dat.append(pd.read_csv(filename, delim_whitespace=True, low_memory=False).drop(0))
        except Exception as e:
            continue
        years.append(filename[-8:-4])
    for df, year in zip(dat, years):
        df.rename({"WSPD":"WSPD m/s"}, axis=1, inplace=True)
        df.loc[:, "WSPD mph"] = df.loc[:, "WSPD m/s"].astype("float") * 2.237
        df.loc[:, "WSPD mph"] = df.loc[:, "WSPD mph"].round(2)


        target = pd.DataFrame({"Entries":len(df), "Mean":round(df["WSPD mph"].mean(), 2), "Std":round(df["WSPD mph"].std(), 2),
                      "Adverse":len(df[df["WSPD mph"] >= 30]), "Missing":len(df[df["WSPD mph"] == "MM"]),
                      "Erroneous":len(df[df["WSPD mph"] >= 200])}, index=[year])
        targets.append(target)

    final = pd.concat(targets)
    final.to_csv("../../WindBuoys" + path + "/" + path + "-summary.csv")
