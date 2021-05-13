from match_wind_data import *
from datetime import *
from meet_and_pass import *

import pandas as pd
import math
import sys

import plotly.figure_factory as ff
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
# %matplotlib inline

from process_maritime_data import *
from fetch_vessel_data import *
from dashboard import *
from cache import *
from plot import *

# ports = (ch, sv)
# for i in range(len(ports)):
#     df = pd.read_csv("../html/riwhale.github.io/master-" + ports[i] + ".csv")
#     df_max = pd.read_csv("../html/riwhale.github.io/master-" + ports[i] + "-max.csv")

sv_path = "../html/riwhale.github.io/master-sv.csv"
ch_path = "../html/riwhale.github.io/master-ch.csv"
ch_max = pd.read_csv("../html/riwhale.github.io/master-ch-max.csv")
sv_max = pd.read_csv("../html/riwhale.github.io/master-sv-max.csv")

ch = pd.read_csv(ch_path)
ch.loc[:, "Date/Time UTC"] = pd.to_datetime(ch.loc[:, "Date/Time UTC"])
sv = pd.read_csv(sv_path)

print("Charleston shape: ", ch.shape)
print("Charleston sans outages shape: ", ch.dropna().shape)
print("Savannah shape: ", sv.shape)

print(len(ch.MMSI.unique()))
print(len(sv.MMSI.unique()))

null_data = ch[ch.isnull().any(axis=1)]
null_data.shape
len(null_data)/len(ch)*100

null_data = sv[sv.isnull().any(axis=1)]
null_data.shape
len(null_data)/len(sv)*100
