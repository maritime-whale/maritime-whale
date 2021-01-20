#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.

import pandas as pd

def create_csv_cache(data_frames, id):
    pd.concat(data_frames).to_csv("../cache/" + id + ".csv", mode="w", index=False)

def create_xlsx_cache(data_frames, id):
    pd.concat(data_frames).to_excel("../cache/" + id + ".xlsx", sheet_name=id,
                                    index=False)
