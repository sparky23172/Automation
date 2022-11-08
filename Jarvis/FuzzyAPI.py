# Name: FuzzyAPI_Headers.py
# Version: 1.0
# Date: 11/07/2022

from cmath import log
import requests
from bs4 import BeautifulSoup as bs4
import argparse
import json
import logging
import sys
import time
import re
import datetime
import os


proxies = {'http': 'http://localhost:8080','https': 'http://localhost:8080',}

XXS_LIST = "xss.txt"
TYPE_CHECK_LIST = ""
SQLI_LIST = "SQL.txt"
XPATH_LIST = "xpath.txt"
SENSITIVE_LIST = ""

TOKEN = "test_value"
AUTH = "token"
FILE_NAME = ""



def stopwatch(arg):
    """ Takes an argument and returns the current time in the format you want
    "Date":
        ("%m/%d/%y")
    "Time":
        ("%H:%M:%S")
    "File":
        ("%m_%d_%y")
    None or anything else:
        ("%m/%d/%y %H:%M:%S")
    """
    today = datetime.datetime.now()
    if arg == None:
        right_meow = today.strftime("%m/%d/%y %H:%M:%S")
    elif arg == "Date":
        right_meow = today.strftime("%m/%d/%y")
    elif arg == "Time":
        right_meow = today.strftime("%H:%M:%S")
    elif arg == "File":
        right_meow = today.strftime("%m_%d_%y")
    else:
        right_meow = today.strftime("%m/%d/%y %H:%M:%S")

    return right_meow


def get_path(d, key):
    logging.debug("Getting path for {}".format(key))
    logging.debug("Thing to check: {}".format(d))
    # sys.exit()

    for k, v in d.items():
        if k == key:
            yield [k]
        elif isinstance(v, dict):
            for result in get_path(v, key):
                yield [k] + result
        elif isinstance(v, list):
            for d2 in v:
                for result in get_path(d2, key):
                    yield [k] + result
        elif isinstance(v, str):
            yield [k]

def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from recursive_items(value)
        elif type(value) is str:
            yield (key, value)
        elif type(value) is list:
            logging.debug("List found. This will break if I report it back for now")
        else:
            yield (key, value)

def hostile_attack(host,header,body, method):
    s = requests.session()

    if method == "GET":
        logging.info("Sending GET Request for {}".format(host))
        # r = s.get(url=host,headers=header, proxies=proxies, timeout=45, verify=False)
    elif method == "POST":
        logging.info("Sending POST Request for {}".format(host))
        # r = s.post(url=host,headers=header ,body=body, proxies=proxies, timeout=45, verify=False)

    logging.info("Insert Attack Line here!")

    logging.debug("Content: {}\n\n".format(bs4(r.content, "html.parser").prettify()))
    logging.debug("Status Code: {}\n\n".format(r.status_code))
    status = r.status_code
    length = len(r.content)

    return status, length

def checks(obj):
    logging.debug("Checking if {} is {}".format(obj,"list"))
    if isinstance(obj,list):
        if len(obj) > 1:
            logging.debug("Object is larger than 1")
        else:
            logging.debug("Object is 1. Checking for dict")
            if isinstance(obj[0],dict):
                logging.debug("Object is dict")
                return "dict"
            else:
                logging.debug("Object is not dict")
                return "list"
        return "list"
    if isinstance(obj,dict):
        logging.debug("Object is dict")
        return "dict"


def log_file(why,url,date,start,stop,total,status,payload,param,attac,length):

    if why == "init":
        if not os.path.isfile(FILE_NAME):
            logging.info("Creating new file")
            f = open(FILE_NAME, "a+")
            f.write("URL,Day,Start Time,End Time,Total Time,Status Code,Response Length,Attacked Parameter,Attack Style #,Payload\n")
        else:
            logging.info("Not creating new file, file already exists")
            return
    elif why == "log":
        payload = payload.replace(",", "-comma-")
        payload = payload.replace("\n", "")
        payload = payload.replace("\t", "    ")
        payload = payload.replace("\"", "-doublequote-")
        payload = payload.replace("\'", "-singlequote-")
        param = param.replace(",", "-comma-")

        f = open(FILE_NAME, "a+")
        f.write("{},{},{} CST,{} CST,{:0.2f},{},{},{},{},{}\n".format(url,date,start,stop,total,status,length,param,attac,payload))
    else:
        logging.info("No reason provided for log_file()")
    f.close()



def auth_proccess(v):
    global TOKEN
    dev = True
    clean_request = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/plain, */*",

    }

    body = {}

    if dev:
        r = {"TOKEN":"TEST_API_TOKEN"}
        TOKEN = r["TOKEN"]
    else:
        # r = clean_request.get(url="",proxies=proxies, headers=headers, timeout=5, verify=False)
        logging.debug("\n\nContent:\n{}\n\n".format(bs4(r.content, "html.parser").prettify()))
        TOKEN = re.findall(r"TOKEN:\"(.+?)\"'", r.text)[0]


    v["header"]["token"] = TOKEN
    return v

def prep(info):
    print("\n\n[*] Preparing the requests for attack")

    logging.info("Checking for fuzzing files")
    if XXS_LIST:
        # open XXS_LIST
        logging.info("Found XSS list")
        with open(XXS_LIST) as f:
            xss = f.readlines()
        xss = [x.strip() for x in xss]
        logging.debug("XSS: {}".format(xss))
    else:
        logging.info("No XSS list found")
        xss = []

    if SQLI_LIST:
        # open SQLI_LIST
        logging.info("Found SQLi list")
        with open(SQLI_LIST) as f:
            sqli = f.readlines()
        sqli = [x.strip() for x in sqli]
        logging.debug("SQLi: {}".format(sqli))
    else:
        logging.info("No SQLi list found")
        sqli = []

    if XPATH_LIST:
        # open XPATH_LIST
        logging.info("Found XPATH list")
        with open(XPATH_LIST) as f:
            xpath = f.readlines()
        xpath = [x.strip() for x in xpath]
        logging.debug("XPATH: {}".format(xpath))
    else:
        logging.info("No XPATH list found")
        xpath = []

    if SENSITIVE_LIST:
        # open SENSITIVE_LIST
        logging.info("Found sensitive list")
        with open(SENSITIVE_LIST) as f:
            sensitive = f.readlines()
        sensitive = [x.strip() for x in sensitive]
        logging.debug("Sensitive: {}".format(sensitive))
    else:
        logging.info("No sensitive list found")
        sensitive = []

    attacks = [xss, sqli, xpath, sensitive]
    # logging.debug("Attacks: {}".format(attacks))

    for x in attacks:
        logging.debug("Attack: {}\n".format(x))

    date = stopwatch("Date")
    log_file("init","","","","","","","","","","")
    for k,v in info.items():

        logging.info("Step 1: Going through the request")

        logging.debug("URL (key): {}".format(k))
        logging.debug("Dump of all values (value): {}\n\n".format(v))
        logging.debug("Method: {}\n".format(v["method"]))
        logging.debug("Headers: {}\n".format(v["header"]))
        logging.debug("Body: {}\n".format(v["body"]))

        logging.info("Step 2: Checking to see if request works as is")
        # status, r_len = hostile_attack(k,v["header"],v["body"],v["method"])
        status = 200
        r_len = 600

        logging.debug("[2] Status: {}".format(status))
        if status != 200:
            logging.warning("[2] Status code not 200. Doing auth method")
            v = auth_proccess(v)
            logging.warning("Retrying request")
            # status, _ = hostile_attack(k,v["header"],v["body"],v["method"])
            if status != 200:
                logging.error("[2] Status code not 200 after auth... Ending program")
                sys.exit()

        logging.info("Step 3: Checking Body for json")
        if v["json"]:
            logging.info("[3] Body is json")
        else:
            logging.info("[3] Body is not json")

        logging.info("Step 4: Attack Headers")
        for x,y in v["header"].items():
            logging.debug("[4] Header: {}".format(x))

            attack_num = 0
            logging.debug("[4] Attack Number: {}".format(attack_num))

            for attac in attacks:
                for i in attac:
                    logging.debug("Header: {}".format(x))
                    logging.debug("Initial Value: {}".format(y))
                    logging.info("XSS Value: {}".format(i))
                    v["header"][x] = i
                    logging.debug("New Header: {}".format(v["header"]))
                    start = stopwatch("Time")
                    toc = time.perf_counter()
                    logging.info("Insert Attack Line here!")
                    # status, r_len = hostile_attack(k,v["header"],v["body"], v["method"])
                    if status == 401 and x != AUTH:
                        logging.info("Status code is 401! Reauth needed")
                        old_token = v["header"]["token"]
                        v = auth_proccess(v)
                        new_token = TOKEN
                        logging.debug("Updated token from {} to {}!\nTrying again".format(old_token,new_token))
                        logging.info("Insert Attack Line here!")
                        if status == 401 and x != AUTH:
                            logging.critical("Status code is 401 still! Exiting program")
                            sys.exit()
                        # time.sleep(2)
                        continue
                    stop = stopwatch("Time")
                    tic = time.perf_counter()

                    log_file("log",k,date,start,stop,(tic - toc),status,i,x,attack_num, r_len)
                attack_num += 1

                logging.info("Reverting {} to original value\n\n".format(x))
                v["header"][x] = y


        logging.debug("Step 5: Attack Body")



def parse_info(name):
    logging.info("Parsing info from {}".format(name))
    URLs = {}

    with open(name) as f:
        data = json.load(f)

    logging.debug("Data: {}".format(data))
    for x in data["item"]:
        for k,v in x.items():
            if k == "request":
                url = v['url']['raw']
                host = re.findall(r'https?://(.*?)/', url)[0]
                logging.debug("Host: {}".format(host))
                URLs[url] = {"URL":url,"method":"","header":{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36", "Host": host},"body":"", "json":False}

                for k1,v1 in v.items():

                    if k1 == "method":
                        logging.debug("Method: {}".format(v1))
                        method = v1
                        URLs[url]["method"] = method

                    if k1 == "body":
                        logging.debug("Body raw: {}".format(v1["raw"]))
                        body = v1["raw"]

                        URLs[url]["body"] = body
                        try:
                            test = json.loads(body)
                            URLs[url]["body"] = test
                        except json.decoder.JSONDecodeError:
                            logging.debug("Body is not JSON")
                            URLs[url]["json"] = False
                            continue

                        logging.debug("Body: {}".format(test))
                            # Print test type
                        test_json = type(test)
                        if test_json != dict:
                            logging.info("Body is not JSON")
                        else:
                            URLs[url]["json"] = True
                            logging.info("Body is JSON")
                        logging.debug("Body type: {}".format(type(test)))

                    if k1 == "header":
                        logging.debug("Header: {}".format(v1))
                        header = v1
                        for item in header:
                            logging.debug("Item Key: {}".format(item["key"]))
                            logging.debug("Item Value: {}".format(item["value"]))
                            URLs[url]["header"][item["key"]] = item["value"]

                    else:
                        pass



    for k,v in URLs.items():
        logging.debug("Key: {}".format(k))
        logging.debug("Value: {}".format(v))
        # logging.debug("Value: {}".format(v["header"]))


    return URLs

# This version needs is for list and more complex URLs
def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    # Prod
    # parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    parser.add_argument("-f","--file",dest="file",help="TPulls data from a Postman Collection",default="Test_Data.json")
    # Dev
    parser.add_argument("-d","--debug",dest="debug",action="store_false",help="Turn on debugging",default=True)


    options = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
        global DEBUG
        DEBUG = True
    else:
        logging.basicConfig(level=logging.INFO)
    return options


def main():
    options = get_arg()

    # Start
    print("[*] Starting\n\n")

    info = parse_info(options.file)

    file_date = stopwatch("File")
    global FILE_NAME
    FILE_NAME = "fuzzyAPI_{}.csv".format(file_date)

    prep(info)

    # logging.debug("Info: {}".format(info))

    # s = requests.session()
    # s.get(url="https://www.w3schools.com/python/",proxies=proxies, timeout=5, verify=False)
    # logging.debug("URLs: {}".format(URLs))


if __name__ == "__main__":
    main()
