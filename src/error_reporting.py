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

def create_message_with_attachment(
    sender, to, subject, message_text, file):
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

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        # WON'T SEE THIS IN HEALTH REPORT (SENT BEFORE THIS IS WRITTEN)
        log(OUT_LOGFILE, "Health message sent successfully.")
        return message
    except errors.HttpError as error:
        log(ERR_LOGFILE, "An error occurred: " + str(error))
        exit(1)

def get_webapp_health_status():
    # grab the most recent 6 logfiles:
    # vmr_out.log, vmr_err.log, sync_out.log, sync_err.log,
    # report_err.log, and YYYY_MM_DD_HH_mm_ss.log
    # logs = sorted([f.name for f in os.scandir("../logs/")
    #               if f.is_file()], reverse=True)[:6]
    # print(logs)
    return "UNKNOWN"

def main():
    creds = gmail_auth(ERR_LOGFILE)
    service = build("gmail", "v1", credentials=creds)
    log(OUT_LOGFILE, "Google OAuth successfully.")
    my_email = "vmr.riwhale@gmail.com"
    zip = "../temp/webapp_logs"
    shutil.make_archive(zip, "zip", "../logs/")
    msg = create_message_with_attachment(my_email, my_email,
                                         "Maritime Whale Webapp Health Report",
                                         "Status: " + get_webapp_health_status(),
                                         zip + ".zip")
    if msg:
        send_message(service, "me", msg)

main()
