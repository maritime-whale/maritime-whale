#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Make frequently utilized constants accessible to other modules within src.

# thresholds and tolerances
MEET_PASS_TIME_TOL = 1 # hours
WIND_TIME_TOL = 3 # hours
OUTAGE_THRESHOLD = 0.65 # ratio
LAT_THRESHOLD = 32.033 # charleston >= 32.033, savannah < 32.033

# conversions
MPS_TO_MPH = 2.237 # meters per sec to miles per hour
M_TO_FT = 3.28 # meters to feet
