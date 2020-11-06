import pandas as pd

def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    blacklist = [int(mmsi) for mmsi in open("../cache/blacklist.txt",
                                            "r").readlines()]
    df = pd.read_csv(path)
    df = df[~df.MMSI.isin(df[df.SPEED >= 40].MMSI.values)]
    df = df[~df.MMSI.isin(df.MMSI.value_counts()[df.MMSI.value_counts() == 1].index.values)]
    df.MMSI.value_counts()[df.MMSI.value_counts() == 1].index.values
    df.rename({"DATETIME (UTC)": "Date/Time UTC", "NAME": "Name",
               "LATITUDE": "Latitude", "LONGITUDE": "Longitude"}, axis=1,
               inplace=True)
    df["LOA m"] = df["A"] + df["B"]
    df["LOA ft"] = df["LOA m"] * 3.28
    df["LOA ft"] = df["LOA ft"].round(0)
    df["Latitude"] = df["Latitude"].round(5)
    df["Longitude"] = df["Longitude"].round(5)
    df = df[df["LOA m"] >= 200]
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    mean = pd.DataFrame(
        df.groupby(["Name", "MMSI"])["SPEED"].mean()).rename(
        {"SPEED": "Mean speed kn"}, axis=1).round(1)
    maxes = pd.DataFrame(
        df.groupby(["Name", "MMSI"])["SPEED"].max()).rename(
        {"SPEED": "Max speed kn"}, axis=1)
    aggregate = maxes.merge(mean, on=["Name", "MMSI"])
    d = aggregate["Max speed kn"].to_dict()
    stats = {"Longitude":[], "Latitude":[], "Date/Time UTC":[], "LOA m":[],
             "LOA ft":[], "COURSE":[], "AIS TYPE":[]}
    for key, value in d.items():
        for k in stats.keys():
            stats[k].append(df[(df.Name == key[0]) &
                               (df.SPEED == value)][k].iloc[0])
    for key in stats.keys():
        aggregate[key] = stats[key]
    aggregate = aggregate.reset_index()
    aggregate = aggregate[(aggregate.COURSE >= 115) &
                          (aggregate.COURSE <= 125) |
                          (aggregate.COURSE >= 295) &
                          (aggregate.COURSE <= 305)]
    aggregate.COURSE = round(aggregate.COURSE).astype("int")
    courses = {}
    for i in range (115, 126):
        courses[i] = "Outbound"
    for i in range (295, 306):
        courses[i] = "Inbound"
    aggregate.COURSE = aggregate.COURSE.replace(courses).astype("str")
    aggregate = aggregate[~aggregate.MMSI.isin(blacklist)]
    new_blacklisters = []
    for i in range(aggregate.shape[0]):
        if aggregate.iloc[i]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36,
                                             37, 51, 52, 53, 55, 57, 58, 59]:
            new_blacklisters.append(aggregate.iloc[i].MMSI)
    with open("../cache/blacklist.txt", "a") as f:
        f.write("\n".join([str(mmsi) for mmsi in new_blacklisters]))

    aggregate = aggregate[~aggregate.MMSI.isin(new_blacklisters)]
    aggregate.sort_values("Max speed kn", ascending=False, inplace=True)
    aggregate = aggregate[["Date/Time UTC", "Name", "MMSI", "Max speed kn",
        "Mean speed kn", "LOA m", "LOA ft", "Latitude", "Longitude", "COURSE"]]
    ch = aggregate[aggregate.Latitude >= 32.033]
    sv = aggregate[aggregate.Latitude < 32.033]
    return ch, sv
