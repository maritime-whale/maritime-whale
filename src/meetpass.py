from datetime import timedelta

def import_report(path):
    # import data from vessel movement reports (csv format); clean and
    # restructure data, compute additional stats
    df = pd.read_csv(path)
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

    df = df[(df.COURSE >= 115) &
            (df.COURSE <= 125) |
            (df.COURSE >= 295) &
            (df.COURSE <= 305)]
    df.COURSE = round(df.COURSE).astype("int")
    courses = {}
    for i in range (115, 126):
        courses[i] = "Outbound"
    for i in range (295, 306):
        courses[i] = "Inbound"
    df.COURSE = df.COURSE.replace(courses).astype("str")
    new_blacklisters = []
    for i in range(df.shape[0]):
        if df.iloc[i]["AIS TYPE"] in [30, 31, 32, 33, 34, 35, 36,
                                             37, 51, 52, 53, 55, 57, 58, 59]:
            new_blacklisters.append(df.iloc[i].MMSI)


    df = df[~df.MMSI.isin(new_blacklisters)]
    df = df[["Name", "MMSI", "Date/Time UTC", "SPEED",
                           "LOA m", "LOA ft", "Latitude", "Longitude", "COURSE", "AIS TYPE"]]
    ch = df[df.Latitude >= 32.033]
    #sv = df[df.Latitude < 32.033]
    return ch


def meetpass_helper_helper(EC, time_interval):
    """This function takes in a cleaned up entry channel dataframe plus desired time_interval (int),
       and returns potential meeting/passing positions from the entry channel"""
    from datetime import timedelta
    #sorts the time stamp such that entry channel data is in chronological order
    times = EC.sort_values("Date/Time UTC")

    mmsi = list(times.MMSI)
    timestamp = list(times["Date/Time UTC"])
    course = list(times.COURSE)

    potential_times = []

    for i in range(len(mmsi) - 1):
            if mmsi[i] != mmsi[i + 1]:
                if (timestamp[i + 1] - timestamp[i]) <= timedelta(minutes = time_interval):
                    if course[i] != course[i + 1]:
                        potential_times.append(timestamp[i])
                        potential_times.append(timestamp[i + 1])
                        sorted(potential_times)

    df2 = times[times["Date/Time UTC"].isin(potential_times)]
    return df2


def timeavg(time_series):
    delta = time_series.max() - time_series.min()
    return time_series.min() + delta


# use '2020-10-05.csv' path for testing
almost = meetpass_helper(ch_agg[4],1).groupby(
        ['MMSI', 'COURSE', pd.Grouper(
            key='Date/Time UTC', freq='min')])[['Date/Time UTC']].size()

#meetpass_helper(ch_agg[4],1).groupby(['Name', 'MMSI', 'COURSE'])[['Date/Time UTC']].apply(timeavg).sort_values('Date/Time UTC')

sub = {}
for level in almost.index.unique(0):
    sub[level] = almost.xs(level, level=0).index

targets = []
tolerance = 5
# FUTURE OPTIMIZATION: minimize comparison operations between timestamps
while len(sub):
    item = sub.popitem()
    cur_key = item[0]
    cur_val = item[1]
    i = 0
    while not cur_val.empty:
        this_time = cur_val.get_level_values(1)[0]
        for inner_key, inner_val in sub.items():
            for j, that_time in enumerate(inner_val.get_level_values(1)):
                if abs(that_time - this_time) <= timedelta(minutes=tolerance):
                    potential_encounter = ((cur_key,
                                            cur_val.get_level_values(1)[0]),
                                           (inner_key,
                                            inner_val.get_level_values(1)[j]))
                    targets.append(potential_encounter)
        multiindex = cur_val.delete(0)
        cur_val = multiindex
        i += 1

print(targets)
