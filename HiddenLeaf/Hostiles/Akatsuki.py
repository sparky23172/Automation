# Name: Akatsuki.py
# Version: 1.1
# Date: 02/02/2022

# Basic
from urllib.parse import urljoin
import logging
import time 
import re

# Specialized
import Team_Seven.Naruto as Naruto
from selenium import webdriver 
from Kakashi import pakkun
import subprocess
import selenium
import Kakashi

EMAIL = ""
PASSW = ""

SEARCHED = []
IGNORE_LIST = []


def check_jinchuriki(email, passw):
    global EMAIL
    EMAIL = email
    global PASSW
    PASSW = passw

    results = {}
    logging.info("Checking for Jinchuriki")
    f = open("stats/Jinchuriki.txt", "r")
    targets = f.readlines()
    f.close()
    length = len(targets)
    logging.info("Found {} targets".format(length))
    targets = list(set(targets))
    length = len(targets)
    logging.info("Found {} targets".format(length))
    for target in targets:
        start = Kakashi.stopwatch(None)
        tic = time.perf_counter()

        target = target.strip()
        who = target.split(" - ")[0]
        why = target.split(" - ")[1]
        if target == "":
            continue
        logging.info("Checking {} against targeted nuclei templates".format(who, why))
        results = nuclei_target(who)

        for x in results:
            if "---" in x:
                logging.info("--- found in the Jinchuriki. Checking for Access")
                answer = Jinchuriki_Stage_2(who,"---")                
            else:
                logging.debug("No Jinchuriki found on {} via {}".format(who,x))
                answer = "No Jinchuriki found on {} via {}".format(who,x)
        end = Kakashi.stopwatch(None)
        toc = time.perf_counter()

        f = open("Kakashi_L33t_Numb3r5.csv", "a+")
        f.write("{},{},{},{},{:0.2f} Seconds,{}\n".format("Akatsuki", who, start, end, (toc - tic), answer))
        f.close()                

        results = nuclei_target(who)


def Jinchuriki_Stage_2(hyped_url, template):
    results = ""
    if template == "---":
        test_uris = [""]

        for test_uri in test_uris:
            try:
                # Checking with "javascript" enabled
                firefox = webdriver.FirefoxOptions()
                firefox.headless = True
                driver = webdriver.Firefox(options=firefox)
                driver.get(hyped_url + test_uri)
                time.sleep(5)

                redirect = driver.current_url
                driver, _, source = Naruto.delta_log(driver,results, EMAIL, PASSW)
                logging.debug("[Delta] {} returned:\n\n{}".format(hyped_url, source))
                if "Authorization Failed." in source:
                    logging.debug("Unauthenticated Access... Continuing.")
                    driver.quit()
                    continue
                else:
                    logging.info("Access Detected on {}! ".format(hyped_url + test_uri))
                    results += "Access Detected on {}! ".format(hyped_url + test_uri)
                driver.quit()

            except selenium.common.exceptions.WebDriverException as e: 
                logging.debug("WebDriverException: {}".format(e))
                if "Alert Text" in str(e):
                    results += "Pop up prompt for {}: {}".format(hyped_url + test_uri,e)
                driver.quit()
                return("???",results)

        if "Access Detected" in results:
            logging.info("You got it son! {} is vulnerable: {}".format(hyped_url,results))
            pakkun("Vulnerablity found! Check Kakashi_L33t_Numb3r5.csv for Access Detected","Akatsuki","Stage3_Checks")
            return("Vulnerable",results)
        else:
            logging.info("No access detected on {}".format(hyped_url))
            return("No Access Detected",results)


def spider(driver, scope):
    urls_found = []
    url = driver.current_url
    logging.info("Starting spider on {}\n\n".format(url))

    href_links = re.findall('(?:href=("|\'))(.*?)("|\')',driver.page_source.lower())
    logging.debug("href_links: {}".format(href_links))
    for _,link,_ in href_links:
        linkz = urljoin(url,link)
        if linkz in urls_found:
            continue
        if scope not in linkz:
            continue

        if "#" in linkz:	# #r refers to original page so avoid duplicate page again and again
            linkz = linkz.split("#")[0]
        
        if linkz not in urls_found and linkz not in SEARCHED and linkz not in IGNORE_LIST:
            if scope in linkz:
                urls_found.append(linkz)
            SEARCHED.append(linkz)

        logging.debug("Links: {}".format(linkz))
    
    # logging.debug("Found {} links".format(len(links)))
    logging.info("All links: {}\n\n".format(urls_found))
    for x in urls_found:
        logging.debug("\tLink: {}".format(x))

    return href_links


def ffuf(command):
    logging.info("Running \"ffuf {}\"".format(command))
    results = subprocess.check_output("ffuf {}".format(command), shell=True).decode("utf-8").split("\n")
    logging.debug("ffuf results: {}".format(results))
    return results


def nuclei_target(url):
    logging.info("Running Nuclei scan on {}".format(url))
    results = subprocess.check_output("nuclei -t templates -u {} -headless -silent -nc".format(url), shell=True).decode("utf-8").split("\n")
    if "" in results:
        results.remove("")
    logging.debug("Nuclei results: {}\nLength: {}".format(results, len(results)))
    return results


def nuclei_open(url):
    logging.info("Running Nuclei scan on {}".format(url))
    results = subprocess.check_output("nuclei -u {} -silent -nc".format(url), shell=True).decode("utf-8").split("\n")
    if "" in results:
        results.remove("")
    logging.debug("Nuclei results: {}\nLength: {}".format(results, len(results)))
    return results


def gobuster(url):
    logging.info("Running Gobuster scan on {}".format(url))
    results = subprocess.check_output("gobuster {}".format(url), shell=True).decode("utf-8").split("\n")
    logging.debug("Gobuster results: {}".format(results))
    return results

