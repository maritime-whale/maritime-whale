from datetime import *
from util import *

import pandas as pd
import math
# import timedelta
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
    # df["LOA m"] = df["A"] + df["B"]
    df["LOA ft"] = (df["A"] + df["B"]) * 3.28
    df["LOA ft"] = df["LOA ft"].round(0)
    # df["Beam m"] = df["C"] + df["D"]
    df["Beam ft"] = (df["C"] + df["D"]) * 3.28
    df["Beam ft"] = df["Beam ft"].round(0)
    df["Latitude"] = df["Latitude"].round(5)
    df["Longitude"] = df["Longitude"].round(5)
    # df['Yaw'] = abs(df.COURSE - df.HEADING)
    sub_panamax = None
    # if mode == "sub-panamax":
    #     sub_panamax = df[df["LOA m"] < 200]
    # df = df[df["LOA m"] >= 200]
    df = df[df["LOA ft"] >= 656]
    df["Date/Time UTC"] = df["Date/Time UTC"].str.strip("UTC")
    df["Date/Time UTC"] = pd.to_datetime(df["Date/Time UTC"])
    df = df[["Date/Time UTC", "Name", "MMSI", "LOA ft", "Latitude",
             "Longitude", "COURSE", "AIS TYPE", "HEADING", "SPEED", "Beam ft"]]

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
        # ports[i]['location'] = location # chain method
        ports[i].loc[:, 'location'] = location
        # offshore: 41004 (ch), 41008 (sv)
        # nearshore: 41029 (ch), 41033 (sv)
        year = ports[i]['Date/Time UTC'].iloc[0].strftime('%Y')
        month = ports[i]['Date/Time UTC'].iloc[0].strftime('%m')
        day = ports[i]['Date/Time UTC'].iloc[0].strftime('%d')
        for buoy in buoys[i].keys():
            try:
                buoys[i][buoy] = pd.read_csv("../temp/" + buoy + ".txt", delim_whitespace=True).drop(0)
            except FileNotFoundError:
                sys.stderr.write("Error: Wind data not found for buoy with ID: " + buoy + "...\n")
                continue
        for j, buoy in enumerate(buoys[i].items()):
            final_winds = {"WDIR degT":[], "WSPD mph":[], "GST mph":[]} # {wind_dir, wind_speed, gust}
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
            # data['Date/Time UTC'] = pd.to_datetime(data['#YY'] + data['MM'] + data['DD'] + data['hh'] + data['mm'],
            #                                      infer_datetime_format=True) chain method
            data.loc[:, "Date/Time UTC"] = pd.to_datetime(data['#YY'] + data['MM'] + data['DD'] + data['hh'] + data['mm'],
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
            # offshore: 41004 (ch), 41008 (sv)
            # nearshore: 41029 (ch), 41033 (sv)
            input_times = None
            wind_data = buoys[i][id]
            target_times = list(wind_data['Date/Time UTC'])
            # nearshore
            if j % 2:
                input_times = list(ports[i][ports[i]['location'] == 'nearshore']['Date/Time UTC'])
            # offshore
            else:
                input_times = list(ports[i][ports[i]['location'] == 'offshore']['Date/Time UTC'])
            for ii in range(len(input_times)):
                min_timedelta = timedelta(hours=WIND_TIME_TOL)
                min_timedelta_index = -1
                for jj in range(len(target_times)):
                    delta = abs(input_times[ii] - target_times[jj])
                    if delta <= timedelta(hours=WIND_TIME_TOL):
                        if min_timedelta > delta:
                            min_timedelta = delta
                            min_timedelta_index = jj
                    else:
                        continue
                if min_timedelta < timedelta(hours=WIND_TIME_TOL) and min_timedelta_index != -1:
                    for k in final_winds:
                        final_winds[k].append(wind_data[k].iloc[min_timedelta_index])
                else:
                    for k in final_winds:
                        final_winds[k].append(float("NaN"))

            # print(len(final_winds["WDIR degT"]))
            for k in final_winds:
                # ports[i][k] = final_winds[k] #chain version
                if j % 2:
                    # print("FUCK!")
                    ports[i].loc[ports[i].location == "nearshore", k] = final_winds[k]
                else:
                    ports[i].loc[ports[i].location == "offshore", k] = final_winds[k]
                    # print("GREAT success)
                    # print(ports[i].columns)
                # ports[i].loc[:, k] = final_winds[k] # loc version (might be broken)

        ports[i] = ports[i][(ports[i].COURSE >= course_ranges[i][0][0]) &
                            (ports[i].COURSE <= course_ranges[i][0][1]) |
                            (ports[i].COURSE >= course_ranges[i][1][0]) &
                            (ports[i].COURSE <= course_ranges[i][1][1])]
        ports[i].COURSE = round(ports[i].COURSE).astype("int")
        # ports[i]['course behavior'] = ports[i].COURSE # chain version
        ports[i].loc[:, 'course behavior'] = ports[i].COURSE
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
                       "LOA ft":[], "COURSE":[], "AIS TYPE":[],
                       "WSPD mph":[], "GST mph":[], "WDIR degT":[]}
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
            # ports[i]['vessel class'] = vessel_class # chain method
            ports[i].loc[:, 'vessel class'] = vessel_class

            ports[i]['Yaw'] = abs(ports[i]['COURSE'] - ports[i]['HEADING'])

            EB = []
            loa = ports[i]['LOA ft'].values
            beam = ports[i]['Beam ft'].values
            yaw = ports[i]['Yaw'].values
            for l in range(ports[i].shape[0]):
                    EB.append(round((math.cos(math.radians(90-yaw[l]))*loa[l]) + (math.cos(math.radians(yaw[l]))*beam[l])))

            ports[i].loc[:, 'effective beam ft'] = EB
            # ports[i].loc[:, 'effective beam ft'] = ports[i].loc[:, 'effective beam m'] * 3.28
            ports[i].loc[:, 'effective beam ft'] = ports[i].loc[:, 'effective beam ft'].round(0)
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
            # ports[i].loc[:, "Yaw"] = yaw

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
                       "Mean speed kn", "LOA ft", "Latitude",
                       "Longitude", "COURSE", "WDIR degT", "WSPD mph", "GST mph"]]
        elif mode == STATS:
            res = res[["Name", "MMSI", "Date/Time UTC", "SPEED",
                       "LOA ft", "Latitude", "Longitude", "AIS TYPE", "COURSE",
                       "course behavior", "HEADING", "location", "vessel class",
                       # "Yaw"
                       "Beam ft", "Yaw", "effective beam ft",
                       "WDIR degT", "WSPD mph", "GST mph"]]

        ports[i] = res

    return ports[0], ports[1] # ch, sv


# path = "/Users/omrinewman/riwhale/maritime-whale/tests/2020-11-16.csv"
# out = import_report(path, STATS)
# ch = out[0]
# sv = out[1]
