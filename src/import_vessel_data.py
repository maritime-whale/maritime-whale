import pandas as pd

# def import_report(path, mode):
def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    blacklist = [int(mmsi) for mmsi in open("../cache/blacklist.txt",
                                            "r").readlines()]
    df = pd.read_csv(path)
    df = df[~df.MMSI.isin(df[df.SPEED >= 40].MMSI.values)]
    df = df[~df.MMSI.isin(df.MMSI.value_counts()[df.MMSI.value_counts() == 1].index.values)]
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
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    df = df[["Date/Time UTC", "Name", "MMSI", "LOA m", "LOA ft",
             "Latitude", "Longitude", "COURSE", "AIS TYPE", "HEADING", "SPEED"]]

    ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
    sv_course_ranges = ((100, 160), (280, 340))
    course_ranges = (ch_course_ranges, sv_course_ranges)
    course_behavior = ("Outbound", "Inbound")
    ports = [None, None] # ch, sv
    for i in range(len(course_ranges)):
        ports[i] = df[df.Latitude >= 32.033] if (i == 0) else df[df.Latitude < 32.033]
        ports[i] = ports[i][(ports[i].COURSE >= course_ranges[i][0][0]) &
                            (ports[i].COURSE <= course_ranges[i][0][1]) |
                            (ports[i].COURSE >= course_ranges[i][1][0]) &
                            (ports[i].COURSE <= course_ranges[i][1][1])]
        ports[i].COURSE = round(ports[i].COURSE).astype("int")
        courses = {}
        for behavior, course_range in zip(course_behavior, course_ranges[i]):
            lower_bound = course_range[0]
            upper_bound = course_range[1]
            for j in range(lower_bound, upper_bound + 1):
                courses[j] = behavior
        ports[i].COURSE = ports[i].COURSE.replace(courses).astype("str")

        mean = pd.DataFrame(
            ports[i].groupby(["Name", "MMSI"])["SPEED"].mean()).rename(
            {"SPEED": "Mean speed kn"}, axis=1).round(1)
        maxes = pd.DataFrame(
            ports[i].groupby(["Name", "MMSI"])["SPEED"].max()).rename(
            {"SPEED": "Max speed kn"}, axis=1)
        merged_speeds = maxes.merge(mean, on=["Name", "MMSI"])
        d = merged_speeds["Max speed kn"].to_dict()
        columns = {"Longitude":[], "Latitude":[], "Date/Time UTC":[], "LOA m":[],
                 "LOA ft":[], "COURSE":[], "AIS TYPE":[]}
        for key, value in d.items():
            for k in columns.keys():
                columns[k].append(ports[i][(ports[i].Name == key[0]) &
                                   (ports[i].SPEED == value)][k].iloc[0])
        for key in columns.keys():
            merged_speeds[key] = columns[key]
        merged_speeds = merged_speeds.reset_index()
        merged_speeds = merged_speeds[~merged_speeds.MMSI.isin(blacklist)]
        new_blacklisters = []
        for j in range(merged_speeds.shape[0]):
            if merged_speeds.iloc[j]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36,
                                                 37, 51, 52, 53, 55, 57, 58, 59]:
                new_blacklisters.append(merged_speeds.iloc[j].MMSI)
        with open("../cache/blacklist.txt", "a") as f:
            f.write("\n".join([str(mmsi) for mmsi in new_blacklisters]))

        merged_speeds = merged_speeds[~merged_speeds.MMSI.isin(new_blacklisters)]
        merged_speeds.sort_values("Max speed kn", ascending=False, inplace=True)
        merged_speeds = merged_speeds[["Date/Time UTC", "Name", "MMSI", "Max speed kn",
            "Mean speed kn", "LOA m", "LOA ft", "Latitude", "Longitude", "COURSE"]]
        ports[i] = merged_speeds

    return ports[0], ports[1] # ch, sv
