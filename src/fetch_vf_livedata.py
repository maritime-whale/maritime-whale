# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
#

from log import *

import pandas as pd
import datetime
import requests
import shutil
import time
import json
import os

# TODO: Use logfile constants in a consistent fashion (i.e. using both STDERR
# and STDOUT, passed as argument in helpers vs using constant directly on all
# levels, etc)
ERR_LOGFILE = "../logs/livedata_err.log"
OUT_LOGFILE = "../logs/livedata_out.log"
UPLOAD_INTERVAL = 30 # number of cycles before upload
SECONDS = 60 # cycle duration in seconds

def _read_token(logfile, filename):
    # TODO: consider moving conf handling stuff to its own file? Maybe even
    # combine gmail_auth.py with other related functions
    # (call new file "config.py"); need to protect for errors when reading the
    # MapBox token as well (probably just reuse this function)
    token = None
    try:
        token = open("../conf/" + filename).read()
    except Exception as e:
        log(logfile, "Error reading " + filename + ":\n\n" + str(e))
    return token.strip()

def _fetch_vesselfinder_data_helper(logfile, userkey):
    """Interacts with the VesselFinder API via the LiveData method."""
    livedata = ("https://api.vesselfinder.com/livedata?" +
                "userkey=" + userkey + "&interval=1")
    response = requests.get(livedata)
    content = response.content
    # check that response to GET request is OK
    if response.status_code != 200:
        print("Unexpected response code: " + str(response.status_code))
        # log(logfile, "Unexpected response code: " + str(response.status_code))
        return
    # GET's response may be OK, but the VesselFinder API may have responded
    # with an error (most commonly "Too frequent requests!")
    if "X-API-ERROR" in response.headers:
        print("ERROR: " + response.headers["X-API-ERROR"])
        # log(logfile, "ERROR: " + response.headers["X-API-ERROR"])
        return
    decoded = json.loads(content.decode("utf-8").replace("'", '"'))
    rows = []
    try:
        for row in decoded:
            rows.append(pd.read_json(json.dumps(row, indent=4, sort_keys=True),
                        orient="index"))
    except Exception as e:
        print("Error: " + str(e))
        return
    if rows:
        df = pd.concat(rows)
        print(df)
        return df
    return # no rows (no vessel movement reported)

def _fetch_vesselfinder_data():
    """Query the AIS dataset at a regular interval (every one minute). Each API
    response provides the latest AIS dataset for all vessels in JSON format."""
    userkey = _read_token("", ".vf_token")
    if userkey is None:
        print("ERROR: INVALID USERKEY!")
        return
    livedata = _fetch_vesselfinder_data_helper("", userkey)
    if livedata is None:
        # TODO: LOG TO STDOUT IN ADDITION TO STDERR
        print("No data...")
    else:
        # date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        livedata.to_csv("../temp/stream.csv", mode="a", header=(not
                        os.path.exists("../temp/stream.csv")), index=False)
        # livedata.to_csv("../temp/" + date + ".csv", mode="a", header=(not
        #                 os.path.exists("../temp/" + date + ".csv")), index=False)

def _use_frozen_stream(logfile):
    print("Importing 'freeze.csv' (PARALLEL)...")
    print("Creating 'LiveData' plots... (PARALLEL)")
    print("Uploading 'LiveData' plots and files... (PARALLEL)")

def infinitely_fetch():
    cycle_duration = 0
    while True:
        # track any lag as the loop cycles by marking the start time
        elapsed = datetime.datetime.now().timestamp()
        if cycle_duration >= UPLOAD_INTERVAL * SECONDS:
            cycle_duration = 0
            if os.path.exists("../temp/stream.csv"):
                shutil.move("../temp/stream.csv", "../temp/freeze.csv")
                # USE MULTITHREADING; WILL THROW OFF SLEEP OTHERWISE
                # UNLESS the process ALWAYS takes less than 60 SECONDS
                # TODO: INVESTIGATE BOTH OF THE ABOVE OPTIONS
                _use_frozen_stream("")
            else:
                # NO NEW DATA SO NO NEED TO UPLOAD ANYTHING
                print("No new data in the last " + str(cycle_duration /
                      SECONDS) + " minutes...")
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        _fetch_vesselfinder_data()
        # elapsed is now NEGATIVE
        elapsed -= datetime.datetime.now().timestamp()
        if abs(elapsed) >= 60:
            print("WARNING! LOOP IS RUNNING SLOW! " + str(elapsed) +
                  " SECONDS ELAPSED BEFORE SLEEP!")
            cycle_duration += abs(elapsed)
            continue # avoid sleep
        cycle_duration += SECONDS
        # print(cycle_duration)
        # print(elapsed)
        time.sleep(SECONDS + elapsed) # add the NEGATIVE elapsed time

infinitely_fetch()
