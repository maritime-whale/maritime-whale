# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Fetches vessel data from unread emails in specifically configured Gmail inbox.

from googleapiclient.discovery import build
from apiclient import errors
from gmail_auth import *
from log import *

import pandas as pd
import datetime
import os.path
import base64

def _get_attachments(logfile, service, user_id, msg_id):
    """Extracts and stores email attachments from specific Gmail message."""
    try:
        message = service.users().messages().get(userId=user_id,
                                                 id=msg_id).execute()
    except errors.HttpError as error:
        log(logfile, "An error occurred: " + str(error))
        exit(1)
    except:
        log(ERR_LOGFILE, "An unexpected error occured.")
        exit(1)
    filenames = []
    for part in message["payload"]["parts"]:
        if part["filename"]:
            if "data" in part["body"]:
                data = part["body"]["data"]
            else:
                att_id = part["body"]["attachmentId"]
                att = service.users().messages().attachments().get(
                      userId=user_id, messageId=msg_id,id=att_id).execute()
                data = att["data"]
            payload = base64.urlsafe_b64decode(data.encode("UTF-8"))
            new_file = part["filename"]
            if not new_file.endswith(".csv"):
                continue
            filepath = "../temp/temp.csv"
            with open(filepath, "wb") as f:
                f.write(payload)
            df = pd.read_csv(filepath)
            new_file = None
            try:
                new_file = pd.to_datetime(df["DATETIME (UTC)"][0])
            except:
                continue
            filenames.append(new_file)
            filepath = os.path.join("../temp/",
                                    new_file.strftime("%Y-%m-%d.csv"))
            os.rename("../temp/temp.csv", filepath)
    return filenames

def fetch_latest_reports(logfile, mode):
    """Retrieves latest 'unread' attachments from the Gmail inbox."""
    creds = gmail_auth(logfile, mode)
    # call the Gmail API
    days = []
    service = build("gmail", "v1", credentials=creds)
    raw = service.users().messages().list(userId="me",
                                          labelIds=["UNREAD",
                                                    "INBOX"]).execute()
    if raw["resultSizeEstimate"] > 0:
        unread = [msg["id"] for msg in raw["messages"]]
        for msg_id in unread:
            days += _get_attachments(logfile, service, "me", msg_id)
            service.users().messages().modify(userId="me", id=msg_id,
                                              body={"removeLabelIds":
                                              ["UNREAD"]}).execute()
    return days
