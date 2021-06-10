#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Downloads raw VMR's for 2020-2021 season and creates one master file.

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import datetime
import glob
import sys
import os

from func_timeout import func_timeout, FunctionTimedOut
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from log import *
from googleapiclient.discovery import build
from apiclient import errors
import base64

import os.path
import pickle


# LIMIT = 45 # authorization time limit (in seconds)
# # if modifying these scopes, delete the file .token.pickle.
# SCOPES = [
#     "https://www.googleapis.com/auth/gmail.readonly",
#     "https://www.googleapis.com/auth/gmail.modify",
#     "https://www.googleapis.com/auth/gmail.compose"
# ]
#
# def _get_attachments(logfile, service, user_id, msg_id):
#     """Extracts and stores email attachments from specific Gmail message."""
#     try:
#         message = service.users().messages().get(userId=user_id,
#                                                  id=msg_id).execute()
#     except errors.HttpError as error:
#         log(logfile, "An error occurred: " + str(error))
#         exit(1)
#     except:
#         log(ERR_LOGFILE, "An unexpected error occured.")
#         exit(1)
#     filenames = []
#     for part in message["payload"]["parts"]:
#         if part["filename"]:
#             if "data" in part["body"]:
#                 data = part["body"]["data"]
#             else:
#                 att_id = part["body"]["attachmentId"]
#                 att = service.users().messages().attachments().get(
#                       userId=user_id, messageId=msg_id,id=att_id).execute()
#                 data = att["data"]
#             payload = base64.urlsafe_b64decode(data.encode("UTF-8"))
#             new_file = part["filename"]
#             if not new_file.endswith(".csv"):
#                 continue
#             filepath = "../temp/temp.csv"
#             with open(filepath, "wb") as f:
#                 f.write(payload)
#             df = pd.read_csv(filepath)
#             new_file = None
#             try:
#                 new_file = pd.to_datetime(df["DATETIME (UTC)"][0])
#             except:
#                 continue
#             filenames.append(new_file)
#             filepath = os.path.join("../temp/",
#                                     new_file.strftime("%Y-%m-%d.csv"))
#             os.rename("../temp/temp.csv", filepath)
#     return filenames
#
# def gmail_auth(logfile):
#     """Handles Gmail authorization via Gmail API."""
#     creds = None
#     # the file .token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time
#     pickled_token = "../conf/.token.pickle"
#     if os.path.exists(pickled_token):
#         with open(pickled_token, "rb") as token:
#             creds = pickle.load(token)
#     # if there are no (valid) credentials available, let the user log in
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             req_ret = None
#             try:
#                 req_ret = func_timeout(LIMIT, Request)
#             except FunctionTimedOut:
#                 log(p, "Request was not completed within " + str(LIMIT) +
#                              " seconds.")
#                 exit(1)
#             except:
#                 log(logfile, "Something unexpected happened when trying to " +
#                              "refresh Google credentials.")
#                 exit(1)
#             creds.refresh(req_ret)
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("../conf/" +
#                                                              "credentials.json",
#                                                              SCOPES)
#             creds = None
#             try:
#                 creds = func_timeout(LIMIT, flow.run_local_server)
#             except FunctionTimedOut:
#                 log(logfile, "Authorization was not completed within " +
#                               str(LIMIT) + " seconds.")
#                 exit(1)
#             except:
#                 log(logfile, "Something unexpected happened when trying to " +
#                              "load Google credentials.")
#                 exit(1)
#         # save the credentials for the next run
#         with open(pickled_token, "wb") as token:
#             pickle.dump(creds, token)
#     return creds
#
# def fetch_latest_reports(logfile):
#     """Retrieves latest 'unread' attachments from the Gmail inbox."""
#     creds = gmail_auth(logfile)
#     # call the Gmail API
#     days = []
#     service = build("gmail", "v1", credentials=creds)
#     raw = service.users().messages().list(userId="me",
#                                           labelIds=["UNREAD",
#                                                     "INBOX"]).execute()
#     if raw["resultSizeEstimate"] > 0:
#         unread = [msg["id"] for msg in raw["messages"]]
#         for msg_id in unread:
#             days += _get_attachments(logfile, service, "me", msg_id)
#             service.users().messages().modify(userId="me", id=msg_id,
#                                               body={"removeLabelIds":
#                                               ["UNREAD"]}).execute()
#     return days
#
# def main():
#     """Checks for new data. If a cache already exists then ignore it. Any unseen
#     data is processed and cached. Stores a simplified and an unsimplified
#     version of the data. Indicates whether backend files are up-to-date."""
#     days = fetch_latest_reports("../logs/raw_vmr.log")
#     if not days:
#         return False
#     res = []
#     # dates = (day.strftime("%Y_%m_%d") for day in days)
#     # date_strs = (day.strftime("%B %d %Y") for day in days)
#     for filename in [day.strftime("../temp/%Y-%m-%d.csv") for day in days]:
#         # print("check")
#         res.append(pd.read_csv(filename))
#         # print("again")
#     pd.concat(res).to_csv("../temp/raw_vmrs.csv")
#     print(pd.concat(res).shape)
#
# if __name__ == "__main__":
#     main()

res = []
dirs = sorted([f.name for f in os.scandir("../temp/")])
for subdir in dirs:
    path = os.path.join(os.getcwd(), "../temp/", subdir)
    if path.endswith(".csv"):
        res.append(pd.read_csv(path))
pd.concat(res).to_csv("../temp/raw_vmrs.csv")
# pd.concat(res).to_excel("../temp/raw_vmrs.xlsx")

pd.read_csv("../temp/raw_vmrs.csv").to_excel("../temp/raw_vmrs.xlsx")
