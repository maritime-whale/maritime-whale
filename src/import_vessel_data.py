from util import *

import pandas as pd
import sys


def import_report(path, mode):
# def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    if mode not in MODES:
        sys.stderr.write("Error: Import mode not recognized...\n")
        exit(1)
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
    sub_panamax = None
    # if mode == "sub-panamax":
    #     sub_panamax = df[df["LOA m"] < 200]
    df = df[df["LOA m"] >= 200]
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    df = df[["Date/Time UTC", "Name", "MMSI", "LOA m", "LOA ft", "Latitude",
             "Longitude", "COURSE", "AIS TYPE", "HEADING", "SPEED"]]

    ch_course_ranges = ((100, 140), (280, 320)) # (outbound, inbound)
    sv_course_ranges = ((100, 160), (280, 340))
    channel_midpoint = ((-79.74169), (-80.78522)) # less than this value is nearshore, greater is offshore. both longitude values
    course_ranges = (ch_course_ranges, sv_course_ranges)
    course_behavior = ("Outbound", "Inbound")
    ports = [None, None] # ch, sv
    # [{ch_off, ch_near}, {sv_off, sv_near}]
    buoys = [{"41004":None, "41029":None}, {"41008":None, "41033":None}]
    for i in range(len(course_ranges)):
        ports[i] = df[df.Latitude >= 32.033] if (i == 0) else df[df.Latitude < 32.033]
        nearshore_index = ports[i][ports[i]['Longitude'] <= channel_midpoint[i]].index
        offshore_index = ports[i][ports[i]['Longitude'] > channel_midpoint[i]].index
        nearshore = pd.Series(['nearshore' for j in range(len(nearshore_index))],
                            index = nearshore_index)
        offshore = pd.Series(['offshore' for j in range(len(offshore_index))],
                            index = offshore_index)
        location = pd.concat([offshore, nearshore]).sort_index(axis=0).to_frame().rename({0:'location'}, axis=1)
        ports[i]['location'] = location

        # offshore: 41004 (ch), 41008 (sv)
        # nearshore: 41029 (ch), 41033 (sv)
        # winds = None
        dir = "tests" # switch to temp and delete this variable when done testing
        year = ports[i]['Date/Time UTC'].iloc[0].strftime('%Y')
        month = ports[i]['Date/Time UTC'].iloc[0].strftime('%m')
        day = ports[i]['Date/Time UTC'].iloc[0].strftime('%d')
        for buoy in buoys[i].keys():
            try:
                buoys[i][buoy] = pd.read_csv("../" + dir + "/" + buoy + ".txt", delim_whitespace=True).drop(0)
            except FileNotFoundError:
                sys.stderr.write("Error: Wind data not found for buoy with ID: " + buoy + "...\n")
                continue
        for buoy in buoys[i].items():
            id = buoy[0]
            data = buoy[1]
            data = data[(data['#YY'] == year) &
                        (data['MM'] == month) &
                        (data['DD'] == day)]
            if data.shape[0] == 0:
                sys.stderr.write("Error: Wind data not found for " +
                                 str(year) + "-" + str(month) + "-" +
                                 str(day) + " for buoy with ID: " +
                                 id + "...\n")
                continue
            data['Date/Time UTC'] = pd.to_datetime(data['#YY'] + data['MM'] + data['DD'] + data['hh'] + data['mm'],
                                                 infer_datetime_format=True)
            data.rename({'WDIR':'WDIR degT', 'WSPD':'WSPD m/s', 'GST':'GST m/s'}, axis=1, inplace=True)
            data = data[(data['WDIR degT'] != 'MM') &
                        (data['WSPD m/s'] != 'MM') &
                        (data['GST m/s'] != 'MM')]
            data['WSPD mph'] = data['WSPD m/s'].astype('float') * 2.237
            data['GST mph'] = data['GST m/s'].astype('float') * 2.237
            data['WSPD mph'] = data['WSPD mph'].round(2)
            data['GST mph'] = data['GST mph'].round(2)
            buoys[i][id] = data[['Date/Time UTC', 'WDIR degT', 'WSPD mph', 'GST mph']]
            # do windspeed matching here




        ports[i] = ports[i][(ports[i].COURSE >= course_ranges[i][0][0]) &
                            (ports[i].COURSE <= course_ranges[i][0][1]) |
                            (ports[i].COURSE >= course_ranges[i][1][0]) &
                            (ports[i].COURSE <= course_ranges[i][1][1])]
        ports[i].COURSE = round(ports[i].COURSE).astype("int")
        ports[i]['course behavior'] = ports[i].COURSE
        courses = {}
        for behavior, course_range in zip(course_behavior, course_ranges[i]):
            lower_bound = course_range[0]
            upper_bound = course_range[1]
            for j in range(lower_bound, upper_bound + 1):
                courses[j] = behavior
        if mode == LVL_PLTS:
            ports[i].COURSE = ports[i].COURSE.replace(courses).astype("str")
            mean = pd.DataFrame(
                ports[i].groupby(["Name", "MMSI"])["SPEED"].mean()).rename(
                {"SPEED": "Mean speed kn"}, axis=1).round(1)
            maxes = pd.DataFrame(
                ports[i].groupby(["Name", "MMSI"])["SPEED"].max()).rename(
                {"SPEED": "Max speed kn"}, axis=1)
            merged_speeds = maxes.merge(mean, on=["Name", "MMSI"])
            d = merged_speeds["Max speed kn"].to_dict()
            columns = {"Longitude":[], "Latitude":[], "Date/Time UTC":[],
                       "LOA m":[], "LOA ft":[], "COURSE":[], "AIS TYPE":[]}
            for key, value in d.items():
                for k in columns.keys():
                    columns[k].append(ports[i][(ports[i].Name == key[0]) &
                                     (ports[i].SPEED == value)][k].iloc[0])
            for key in columns.keys():
                merged_speeds[key] = columns[key]
            merged_speeds = merged_speeds.reset_index()
        elif mode == STATS:
            ports[i]['course behavior'] = ports[i]['course behavior'].replace(courses).astype("str")
            ### vessel class specification
            panamax_index = ports[i][ports[i]['LOA ft'] <= 965].index
            post_panamax_index = ports[i][ports[i]['LOA ft'] > 965].index
            panamax = pd.Series(['Panamax' for j in range(len(panamax_index))],
                                index = panamax_index)
            post_panamax = pd.Series(['Post Panamax' for j in range(len(post_panamax_index))],
                                index = post_panamax_index)
            vessel_class = pd.concat([panamax, post_panamax]).sort_index(axis=0).to_frame().rename(
                                        {0:'vessel class'}, axis=1)
            ports[i]['vessel class'] = vessel_class

            ### location specification
            # nearshore_index = ports[i][ports[i]['Longitude'] <= channel_midpoint[i]].index
            # offshore_index = ports[i][ports[i]['Longitude'] > channel_midpoint[i]].index
            # nearshore = pd.Series(['nearshore' for j in range(len(nearshore_index))],
            #                     index = nearshore_index)
            # offshore = pd.Series(['offshore' for j in range(len(offshore_index))],
            #                     index = offshore_index)
            # location = pd.concat([offshore, nearshore]).sort_index(axis=0).to_frame().rename({0:'location'}, axis=1)
            # ports[i]['location'] = location


            ### Yaw calculcation
            # compliant_index = ports[i][ports[i].SPEED <= 10].index
            # non_compliant_index = ports[i][ports[i].SPEED > 10].index
            # compliant = pd.Series([abs(ports[i].COURSE - ports[i].HEADING) for j in range(len(compliant_index))],
            #                     index = compliant_index)
            # non_compliant = pd.Series([float("NaN") for i in range(len(non_compliant_index))],
            #                     index=non_compliant_index)
            # yaw = pd.concat([compliant, non_compliant]).sort_index(axis=0).to_frame().rename({0: "Yaw"}, axis=1)
            # ports[i]["Yaw"] = yaw

        res = None
        if mode == LVL_PLTS:
            res = merged_speeds
        elif mode == STATS:
            res = ports[i]
        res = res[~res.MMSI.isin(blacklist)]
        new_blacklisters = []
        for j in range(res.shape[0]):
            if res.iloc[j]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36, 37,
                                           51, 52, 53, 55, 57, 58, 59]:
                new_blacklisters.append(res.iloc[j].MMSI)
        with open("../cache/blacklist.txt", "a") as f:
            f.write("\n".join([str(mmsi) for mmsi in new_blacklisters]))

        res = res[~res.MMSI.isin(new_blacklisters)]
        if mode == LVL_PLTS:
            res.sort_values("Max speed kn", ascending=False, inplace=True)
            res = res[["Date/Time UTC", "Name", "MMSI", "Max speed kn",
                       "Mean speed kn", "LOA m", "LOA ft", "Latitude",
                       "Longitude", "COURSE"]]
        elif mode == STATS:
            res = res[["Name", "MMSI", "Date/Time UTC", "SPEED", "LOA m",
                       "LOA ft", "Latitude", "Longitude", "AIS TYPE", "COURSE",
                       "course behavior", "HEADING", "location", "vessel class"#,
                       # "Yaw"
                       ]]

        ports[i] = res

    return ports[0], ports[1] # ch, sv


# path = "/Users/omrinewman/riwhale/maritime-whale/tests/2020-11-16.csv"
# out = import_report(path, STATS)
# ch = out[0]
# sv = out[1]
