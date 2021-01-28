# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Cache file creation.

import pandas as pd

def create_cache(data_frames, filename, extension):
    """Writes a cache file with the specified data, filename, and extension.

    Args:
        data_frames: List of DataFrames.

        filename: Cache file name.

        extension: Desired file type (csv, xlsx, etc.)

    Returns:
        Concatenated data from data_frames written as specified file type.
    """
    cache_ext = extension.lower()
    if cache_ext in ["csv", "xlsx", "all"]:
        res = pd.concat(data_frames)
        if cache_ext == "csv":
            res.to_csv("../cache/" + filename + ".csv", mode="w", index=False)
        if cache_ext == "xlsx":
            res.to_excel("../cache/" + filename + ".xlsx", sheet_name=filename,
                         index=False)
        if cache_ext == "all":
            res.to_csv("../cache/" + filename + ".csv", mode="w", index=False)
            res.to_excel("../cache/" + filename + ".xlsx", sheet_name=filename,
                         index=False)
    else:
        print("Error: Specified cache file type support not yet implemented...")
