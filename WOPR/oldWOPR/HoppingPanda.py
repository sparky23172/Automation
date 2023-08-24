#!/usr/bin/env python3

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from googleapiclient import discovery
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from apiclient import errors
import mimetypes
import argparse
import logging

import pickle
import base64
import pandas as pd
import time
import json
import sys
import os
import re



LIFE = True
DEBUG = False
SCOPES = [
    'https://mail.google.com/']
user = ''
cookies = None
service = ''
TIMEOUT = 10

DATE = time.strftime("%m-%d-%Y")

def gmailAuth():
    logging.debug("[+] Grabbing GMAIL login cred")

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickley'):
        with open('token.pickley', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickley', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    # print (service)
    if not service:
        logging.critical("Nope!")
        sys.exit(12)
    logging.debug("[+] Returning credentials")
    global SERVICE
    SERVICE = service


def alexEmail(subject):
        # dev = True
        dev = False

        email = '''<html><head>Hello! This is Jarvis! Here is what I found!</head><body>
        Request recieved to check the status all Tickets for the morning meeting!<br><br>'''

        # open the file and read it
        with open('morning_Alex_{}.txt'.format(DATE), 'r') as file:
                data = file.read().replace('\n', '<br>')
                data = data.replace('\t', '&emsp;')
                email += data

        email += '''<br><br>Thanks,<br> Jarvis</body></html>'''

        body = email
        # print(body)
        message = MIMEText(body, 'html')
        if dev:
                people = [""]
        else:
                people = [
                                ""
                        ]

        message['to'] = ','.join(people)
        message['from'] = user
        message['subject'] = subject
        logging.debug("[+] Sending email")
        print(message)
        logging.debug(base64.urlsafe_b64encode(message.as_bytes()))
        payload = ({'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()})

        try:
                message = (SERVICE.users().messages().send(userId=user, body=payload)
                                .execute())
                print('Message Id: %s' % message['id'])
        except errors.HttpError as error:
                print('An error occurred: %s' % error)
                return True



def get_arg():
        """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
        parser = argparse.ArgumentParser()
        # CLI Version
        # parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
        parser.add_argument("-d","--debug",dest="debug",action="store_false",help="Turn on debugging",default=True)
    # File version
        parser.add_argument("-w","--why",dest="why", help="This is why the program is being called.")

        parser.add_argument("-u","--url",dest="url", help="URL to be scanned")
        parser.add_argument("-l","--location",dest="location", default="Jarvis_Brain.xlsx", help="Location of the excel file")
        parser.add_argument("-v","--version",dest="version", default="1", help="XLSX version")
        parser.add_argument("-D","--Directory",dest="directory", help="Name of the output directory. If none is provided, name will be whatever the URL is with _ instead of . in the name")

        options = parser.parse_args()
        if options.debug:
                logging.basicConfig(level=logging.DEBUG)
                global DEBUG
                DEBUG = True
        else:
                logging.basicConfig(level=logging.INFO)
        return options


def main(options):
        logging.info("[*] Grabbing Arguments")

        # "Cronjob" portion
        logging.info("[+] Entering HoppingPandas")
        gmailAuth()

        if options.why == "Alex":
                alexEmail("[Jarvis] Group Morning Sync Email for {}".format(DATE))

        logging.info("[+] Exiting HoppingPandas\n")


if __name__ == "__main__":
        options = get_arg()
        main(options)
