from apiclient import errors
from bs4 import BeautifulSoup as bs4
from email import encoders
from email.message import Message
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.discovery import build
import argparse
import base64
import logging
import mimetypes
import os
import pandas as pd
import paramiko as pmk
import pickle
import pymysql
import pyotp
import re
import requests
import sys
import time
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# logging.basicConfig(level=logging.DEBUG)  # Dev debugging


def file_transfer(device,src_dir,dst_dir):
	'''Takes a Paramiko session, file source location, and destination. 
Purpose: SSHs the file there and the closes session.
Returns: Nothing  
'''
	sftp = device.open_sftp()
	sftp.put(src_dir, dst_dir)
	sftp.close()


def gmailAuth(pickle_boi,credential,SCOPES):
    ''' Takes name of the pickle.token, name of the credential file, scopes needed if authenticating
Purpose: Returns service authentication for Google
Returns: Google Service Object
'''
    print("[+] Grabbing GMAIL login cred")

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(pickle_boi):
        with open(pickle_boi, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credential, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(pickle_boi, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    print(service)
    if not service:
        print("[!!!] Unable to return credentials!")
        sys.exit(12)
    print("[+] Returning credentials")

    return service


def console(cust,user,passwd,token):
    ''' Takes client's short name, user to stack, password for stack, 2FA for stack.
Purpose: Grabs the login session from a client
Returns: Session for client
'''

    if (re.search(r"\d+\.\d+\.\d+\.\d+",str(cust))):
        print("[+] IP Detected")
        client = cust
    else:
        print("[+] Looking up name")
        conn = pymysql.connect(
            host="---",
            user='---',
            passwd='---',
            db="webapp",
            port=3306)
        query = "select ssh_IP,ssh_port,web_IP,web_port from --- where --- = \"{}\";".format(cust)    
        logging.debug("Query: {}".format(query))
        data = pd.read_sql(query, conn)
        logging.debug("Raw Data: {}".format(data.values[0][2]))
        try:
            client = "{}:{}".format(data[0][2],data[0][3])
        except:
            client = "{}:{}".format(data.values[0][2],data.values[0][3])
        
    target_url = "https://{}/perl/---".format(client)
    response = requests.get(target_url, verify=False)
    if not "verification_code" in str(bs4(response.content,features="html.parser")):
        data_dict = {
        "userid": user,
        "passcode": passwd,
        "Login": "submit"}
    else:
        print("[!] TOTP required...")
        totp=pyotp.TOTP(token)
        logging.debug("[*] Current TOTP: {}".format(totp.now())) 
        data_dict = {
            "userid": user,
            "passcode": passwd,
            "verification_code": totp.now(),
            "Login": "submit"}

    session = requests.Session()
    response = session.post(target_url, data=data_dict, verify=False)
    if 'invalid' in str(bs4(response.content,features="html.parser")):
        print('[!] Issue logging into Stack.\n[!] Please check credentials')
        exit(0)
    elif '---' in str(response.content):
        print('[!] Issue logging into Stack.\n[!] Please enroll in {}'.format(client))
        exit(0)
    else:
        print("[+] Logged into {}".format(client))
        pass

    logging.debug(bs4(response.content,features="html.parser"))
    return session


                                                                                                                                                                                                                                              
def Connect_To_Sensor (Munit, RemoteIP, RemotePort, Username, Password):
        ''' Takes Munit session, Ip of sensor, Port of sensor, --- username, --- password
Purpose: Connect to sensor
Returns: Paramiko session for sensor
''' 
        try:
                munit_Transport = munit.get_transport()                               
                Sensor_Chan = munit_Transport.open_channel(                                                                                      
                        "direct-tcpip",                                                                                                           
                        (RemoteIP, RemotePort),                                                                                              
                        ('127.0.0.1', 0),                                                                                                     
                        timeout=10)                                                                                                     
                                                                                                                          
                Sensor = pmk.SSHClient()                                                                                            
                Sensor.set_missing_host_key_policy(pmk.AutoAddPolicy())                                                                        
                Sensor.connect(                                                                                                                   
                        RemoteIP,                                                                                                                 
                        port = RemotePort,                                                                                                       
                        username = Username,                                                                                                          
                        password = Password,                                                                                                         
                        sock = Sensor_Chan,                                                                                                    
                        timeout=10                                                                                                                
                )                                                                                                             
                # print (Sensor)                                                                                                          
                return Sensor                                                                                                  
                                                                                                         
        except Exception: raise    


def munit(ip, port, ssh_user, ssh_pass):
	''' Takes IP address, port, SSH Username, SSH Password (IF 2FA IS SET UP FOR CLIENT, THIS METHOD WILL NOT WORK UNLESS USER IS ---)
Purpose: Connect to client's munit
Returns: munit connection
'''
	Remote = pmk.SSHClient ()
	Remote.load_system_host_keys ()
	Remote.set_missing_host_key_policy (pmk.WarningPolicy())
	try:
		Remote.connect(
			ip,
			port,
			username=ssh_user,
			password=ssh_pass,
			timeout=10
                        )
		return Remote
	except Exception: raise


def sensor_cmd(ssh_session, cmd, root, root_pass,TIMEOUT):
        ''' Takes SSH session for target, command, if root is required (TRUE / FALSE), root password if TRUE, Int for time till timeout
Purpose: Sends a command and then returns response
Returns: Array that contains all the lines of the command's output
'''
        print("[+] Command being sent: " + str(cmd))
        stdin, stdout, stderr = ssh_session.exec_command(cmd , get_pty=True,timeout=TIMEOUT)
        # if stdin:
        # print(stdin.readlines())
        # if stdout:
        # print(stdout.read())
        # if stderr:
        # print(stderr.read())
        if root:
            time.sleep(2) # some enviroment maybe need this.
            print("[+] Command away. Waiting for response")
            stdin.write(root_pass + '\r\n')
            stdin.flush()
        ips = stdout.readlines()
        return ips


def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Turn on debugging",
        default=False)
    parser.add_argument(
        "-c",
        "--client",
        dest="client",
        help="IP address of the client")
    parser.add_argument( 
        "-C", 
        "--Client", 
        dest="Client", 
        help="Short name of the client")
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Silence Slack alerting",
        default=False)
    parser.add_argument(
        "-p",
        "--port",
        dest="port", 
        help="Port")
    parser.add_argument( 
        "-s", 
        "--sensor", 
        dest="sensor", 
        help="Sensor for core remover")
    parser.add_argument( 
        "-x", 
        "--extra", 
        dest="extra",
        action="store_true",
        help="Extra flag for extended options",
        default=False)
    options = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    return options


def gmail_email(subject,body,recipients,me,service):
        ''' Takes email subject, body of email, list of recipients, email of sender, gmail service
Purpose: Sends an email through gmail
Returns: Nothing
'''
        print(service)
        message = MIMEText(body,"html")          
        message['to'] = ','.join(recipients) 
        message['from'] = me         
        message['subject'] = subject        
        # print (message)  
        raw = base64.urlsafe_b64encode(message.as_bytes())                                                             
        raw = raw.decode()                                                                                                                
        payload = ({'raw': raw})                                                                                                                     
        message = (service.users().messages().send(userId=me, body=payload)                                                                  
                  .execute())                                                                                                                    
        success = message['id']                                                                                                                       
        print ('[+] Message sent to ' + str(recipients))                                                                                               


def gmail_xlsx_email(subject,body,recipients,me,service,file_name):
    ''' Takes Email subject, body, list of recipients, email of sender, gmail service, name of file
Purpose: Sends email with attachment
Returns: Nothing
'''
    print(service)
    message = MIMEMultipart() 
    message['to'] = ','.join(recipients) 
    message['from'] = me
    message['subject'] = subject 
    message.attach(MIMEText(body,"html"))
    file_dir = "/home/---/WOPR/" 
    path = os.path.join(file_dir, file_name) 
    content_type, encoding = mimetypes.guess_type(path) 
    my_mimetype, encoding = mimetypes.guess_type(path) 
    if my_mimetype is None or encoding is not None: 
        my_mimetype = 'application/octet-stream' 
    main_type, sub_type = my_mimetype.split('/', 1)# split only at the first '/' 
    part = MIMEBase('application', "vnd.ms-excel") 
    part.set_payload(open(path, "rb").read()) 
    encoders.encode_base64(part) 
    part.add_header('Content-Disposition', 'attachment', filename=file_name) 
    message.attach(part) 
    message_as_bytes = message.as_bytes() # the message should converted from string to bytes. 
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes) #encode in base64 (printable letters coding) 
    raw = message_as_base64.decode()  # need to JSON serializable (no idea what does it means) 
    payload = {'raw': raw} 
    try: 
        message = ( 
            service.users().messages().send( 
                userId=me, 
                body=payload).execute()) 
        success = message['id'] 
        print ('[+] Message sent to ' + str(recipients)) 
        # return message 
    except errors.HttpError as error: 
        print ('An error occurred: %s' % error) 

