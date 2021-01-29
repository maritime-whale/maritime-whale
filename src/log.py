# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Handles log writing.

def log(filename, msg):
    """Append message to specified logfile"""
    f = open(filename, "a")
    f.write(msg + "\n")
    f.close()
