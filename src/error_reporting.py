#!/usr/bin/env python3
# Copyright 2020 The Maritime Whale Authors. All rights reserved.
# Use of this source code is governed by an MIT-style license that can be
# found in the LICENSE.txt file.
#
# Sends a health report via specialized Gmail account.

from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.message import Message
from apiclient import errors
from email import encoders
from gmail_auth import *

import mimetypes
import shutil
import base64
import os

ERR_LOGFILE = "../logs/report_err.log"
OUT_LOGFILE = "../logs/report_out.log"
VMR_EMAIL_ADDRESS = "vmr.riwhale@gmail.com"

def create_message_with_attachment(sender, to, subject, message_text, file):
    """Sends a message and a payload via Gmail.

    Args:
        sender: Email address of sender string.
        to: Email address of recipient string.
        subject: Subject line string.
        message_text: Message body string.
        file:

    Returns:
        Dictionary containing raw byte encoding of message.
    """
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    msg = MIMEText(message_text)
    message.attach(msg)
    content_type, encoding = mimetypes.guess_type(file)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        fp = open(file, "rb")
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == "image":
        fp = open(file, "rb")
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == "audio":
        fp = open(file, "rb")
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, "rb")
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    encoders.encode_base64(msg)
    filename = os.path.basename(file)
    msg.add_header("Content-Disposition", "attachment", filename=filename)
    message.attach(msg)
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

def _send_message(service, user_id, message):
    """Sends health message via Gmail."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
    except errors.HttpError as error:
        log(ERR_LOGFILE, "An error occurred: " + str(error))
        exit(1)
    except:
        log(ERR_LOGFILE, "An unexpected error occured.")
        exit(1)
    log(OUT_LOGFILE, "Health message sent successfully.")
    return message

# TODO: finish (simple) health status logic
def _get_webapp_health_status():
    """To be implemented..."""
    # grab the most recent 6 logfiles:
    # vmr_out.log, vmr_err.log, sync_out.log, sync_err.log,
    # report_err.log, and YYYY_MM_DD_HH_mm_ss.log
    # logs = sorted([f.name for f in os.scandir("../logs/")
    #               if f.is_file()], reverse=True)[:6]
    # print(logs)
    return "UNKNOWN"

def main():
    creds = gmail_auth(ERR_LOGFILE, "norm")
    service = build("gmail", "v1", credentials=creds)
    log(OUT_LOGFILE, "Google OAuth successful.")
    zip = "../temp/webapp_logs"
    shutil.make_archive(zip, "zip", "../logs/")
    # send the health report email to self and use email filtering to
    # auto-forward health report to dev team (better privacy)
    msg = create_message_with_attachment(VMR_EMAIL_ADDRESS, VMR_EMAIL_ADDRESS,
                                         "Maritime Whale Web App Health Report",
                                         "Status: " +
                                         _get_webapp_health_status(),
                                         zip + ".zip")
    if msg:
        _send_message(service, "me", msg)

if __name__ == "__main__":
    main()
