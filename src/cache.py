import pandas as pd

def create_csv_cache(data_frames, id):
    pd.concat(data_frames).to_csv("../cache/" + id + ".csv", mode="w", index=False)

def create_xlsx_cache(data_frames, id):
    pd.concat(data_frames).to_excel("../cache/" + id + ".xlsx", sheet_name=id,
                                    index=False)
