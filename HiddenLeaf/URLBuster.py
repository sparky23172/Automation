# Name: URLBuster.py
# Version: 4.0
# Date: 01/05/2022


# Basic
import argparse
import logging
import time 
import re
import sys
import datetime
import os 

# Specialized
from bs4 import BeautifulSoup as bs4
import socket
import selenium
from selenium import webdriver 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

full_information = {}
NO_RESOLVES = []
NO_PORTS = []
STAGE_2 = []

DEBUG = False

# Pass a hostname through commandline
def main():
    options = get_arg()
    logging.info("Starting URLBuster")
    URLs = grab_URLs(options.file)
    init(URLs,options.ports,options.email,options.password)
    create_xlsx(full_information,options.markdown,options.rip)
    logging.info("Finished URLBuster")


def pakkun(url,who):
    f = open('stats/Pakkun_{}.txt'.format(who),'a')
    f.write("{}\n".format(url))
    f.close()
    if who == "No":
        NO_RESOLVES.append(url)
    elif who == "Scan":
        NO_PORTS.append(url)
    elif who == "Stage2":
        STAGE_2.append(url)


def grab_URLs(file):
    """ Takes a file
    Grabs all the URLs from the file and returns them in a list
    """
    logging.debug("Grabbing URLs from {}".format(file))
    with open(file) as f:
        urls = f.readlines()
    return urls

def init(urls,ports,email,password):
    """ Takes a list of URLs
    Starts 
    """
    portz = [443,80]
    counter = 1

    rip_rate = os.path.exists("slack-bot")

    logging.debug("Starting to check URLs")
    
    if not os.path.exists("stats/Pakkun_No.txt"):
        f = open('stats/Pakkun_No.txt', 'w')
        f.close()
    if not os.path.exists("stats/Pakkun_Scan.txt"):
        f = open('stats/Pakkun_Scan.txt', 'w')
        f.close()
    if not os.path.exists("stats/Pakkun_Stage2.txt"):
        f = open('stats/Pakkun_Stage2.txt', 'w')
        f.close()

    for url in urls:
        if DEBUG:
            f = open('Debug_Logs.txt', 'w')
            f.write("{}\n".format(full_information))
            f.write("Last URL to be seen: {}\n".format(url))
            f.close()

        if rip_rate:
            if rip_rate == True:
                os.system("./slack-bot -w URL -x Home -m 'Progress: {}/{} {:.0%}'".format(counter,len(urls), (counter/len(urls))))
                rip_rate = .20
            elif counter/len(urls) > rip_rate:
                os.system("./slack-bot -w URL -x Home -m 'Progress: {}/{} {:.0%}'".format(counter,len(urls), (counter/len(urls))))
                rip_rate += .20

        url = url.strip()
        logging.debug("Starting URLBuster on {} ({}/{})".format(url,counter,len(urls)))
        counter += 1
        today = datetime.datetime.now()
        now_now = today.strftime("%m/%d/%y")
        now_now_2 = today.strftime("%m/%d/%y %H:%M:%S")
        logging.debug("Today: {}".format(now_now))
        try:
            if not url:
                continue
            full_information[url] = {}

            resolve_result,new_url,port = check_resolves(url)
            logging.debug("Resolve Result: {}".format(resolve_result))
            
            portz = [443,80]
            if ports:
                portz.append(int(ports))
            if port and port not in portz:
                portz.insert(0,int(port))

            full_information[url]["Resolves"] = resolve_result
            if resolve_result != "Resolved":
                full_information[url]["Resolves"] = resolve_result
                full_information[url]["SSO"] = "No"
                full_information[url]["Access"] = "No"
                full_information[url]["Redirected"] = "No"
                full_information[url]["Scope"] = "URL in scope"
                full_information[url]["Notes"] = "URL did not resolve to anything"
                full_information[url]["Date"] = now_now
                full_information[url]["Datez"] = now_now_2

                pakkun(new_url,"No")
                continue

            logging.debug("Checking to see if 80 or 443 are open for: {}".format(new_url))
            port_result = check_port(new_url,portz)
            logging.debug("Rip?")
            logging.debug(port_result)
            if port_result == "No":
                full_information[url]["SSO"] = "No"
                full_information[url]["Access"] = "No"
                full_information[url]["Redirected"] = "No"
                full_information[url]["Scope"] = "URL in scope"
                full_information[url]["Notes"] = "Nothing came back..."
                full_information[url]["Date"] = now_now
                full_information[url]["Datez"] = now_now_2
                
                pakkun(new_url,"Scan")
                continue
            elif port_result == "Riperino":
                full_information[url]["SSO"] = "No"
                full_information[url]["Access"] = "No"
                full_information[url]["Redirected"] = "No"
                full_information[url]["Scope"] = "URL in scope"
                full_information[url]["Notes"] = "Nothing is open on ports {}".format(portz)
                full_information[url]["Date"] = now_now
                full_information[url]["Datez"] = now_now_2
                
                pakkun(new_url,"Scan")
                continue
            elif port_result == "Yeet":
                full_information[url]["SSO"] = "No"
                full_information[url]["Access"] = "No"
                full_information[url]["Redirected"] = "No"
                full_information[url]["Scope"] = "URL in scope"
                full_information[url]["Notes"] = "Connection refused"
                full_information[url]["Date"] = now_now
                full_information[url]["Datez"] = now_now_2
                
                pakkun(new_url,"Scan")
                continue

            full_url = port_result + new_url

            logging.debug("Checking to see if 80 or 443 are open for: {}".format(full_url))
            pakkun(new_url,"Stage2")

            check_sso(full_url, url,email ,password, now_now, now_now_2)
            print("Out")
            if DEBUG:
                f = open('Debug_Logs.txt', 'w')
                f.write("{}\n".format(full_information))
                f.write("Made it through: {}\n".format(url))
                f.close()

        except TypeError as e:
            full_information[url]["Resolves"] = "No"
            full_information[url]["SSO"] = "No"
            full_information[url]["Access"] = "No"
            full_information[url]["Redirected"] = "No"
            full_information[url]["Scope"] = "URL in scope"
            full_information[url]["Notes"] = e  
            full_information[url]["Date"] = now_now
            full_information[url]["Datez"] = now_now_2
            logging.error("Error: {}".format(e))
            if DEBUG:
                f = open('Debug_Logs.txt', 'w')
                f.write("{}\n".format(full_information))
                f.write("Error on: {}\n".format(url))
                f.close()
            continue
    
        if full_information[url]["Notes"] == None:
            full_information[url]["Notes"] = "Nothing"

        if DEBUG:
            try:
                for x,y in full_information.items():
                    logging.debug("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(x,y["Date"],y["Resolves"],y["SSO"],y["Access"],y["Redirected"],y["Scope"],str(y["Notes"]).strip()))
            except KeyError:
                logging.fatal("Unable to parse: {}. Please check".format(url))
                sys.exit(0)


def check_resolves(url):
    """ Takes a URL
    Checks to see if the URL resolves to an IP address.
    Returns Yes, No, RIP (for timeouts trying to connect which means something could be there), or the error
    """
    logging.debug("Checking to see if {} resolves".format(url))
    ## Check to see if there is a directory in the url passed
    ports = None

    if "/" in url:
        url = url.split("/")[0]

    ## Check to see if there is a port in the url passed
    if ":" in url:
        logging.debug(url)
        temp_url = url.split(":")
        url = temp_url[0]
        ports = temp_url[1]

    ## Check to see if there is a protocol in the url passed
    if "https://" in url:
        url = url.replace("https://","")
    elif "http://" in url:
        url = url.replace("http://","")

    try:
        socket.gethostbyname(url)
        return "Resolved",url,ports
    except socket.gaierror as e:
        try:
            logging.info("{} doesn't have an IP assosiated with it... Testing if there is anything on 443 just in case".format(url))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((url, 443))
            s.close()
        except socket.timeout as e:
            logging.error("Timeout Occurred: {}".format(e))
            return "Resolved",url,ports
        except socket.gaierror as e:
            logging.error("Still can't find: {}".format(e))
            return "Not Resolved",url,ports
        except Exception as e:
            logging.error("Error?: {}".format(e))
            return e,url,ports


# Check to see if the url is open on port 443
def check_port(url,ports):
    """ Takes a URL
    Checks to see if the URL is open on port 443 or 80.
    Returns https:// if it is open on 443, http:// if it is open on 80, and No if it times out on both.
    """      
    yeet = False
    logging.info("Checking for ports 443 and 80")
    for x in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((url, x))
            s.close()
            if str(443) in str(x):
                return "https://"
            else:
                return "http://"
        except socket.timeout as e:
            logging.debug("Timed out for port {}".format(x))
            continue
        except ConnectionRefusedError as e:
            logging.debug("It said fuck no for port {}".format(x))
            yeet = True
            continue
        except Exception as e:
            logging.error("Error?: {}".format(e))
            return e
    if yeet:
        return("Yeet")
    else:
        return("Riperino")


def check_sso(url, base_url, email, password, now_now, now_now_2):
    """ Takes a URL with protocol

    """
    logging.info("Launching Browser to verify information")
    full_information[base_url]["Date"] = now_now
    full_information[base_url]["Datez"] = now_now_2
    try:
        firefox = webdriver.FirefoxOptions()
        firefox.headless = True
        driver = webdriver.Firefox(options=firefox)
        driver.get(url)
        time.sleep(5)
        redirect = driver.current_url

        # Default notes set to None so that in case nothing is found, it won't be a sad panda
        full_information[base_url]["Notes"] = None

        logging.debug("Base URL: {} vs Final URL: {}".format(url,redirect))

        if "loginPage" in redirect or "loginPage.com" in redirect:
            # I am in the SSO page.
            full_information[base_url]["SSO"] = "Yes"
            logging.info("Login detected")

            # Typing in email address after finding it
            search_box = driver.find_element_by_name("loginUID")
            search_box.send_keys(email)
            driver.find_element_by_id("submitButton").click()

            # Typing in password after finding it
            search_box = driver.find_element_by_name("loginPwd")
            search_box.send_keys(password)

            # Waiting 2 seconds so that it will let me click        
            logging.debug("Waiting 2 seconds")
            time.sleep(2)

            logging.debug("Going down a rabbit hole")
            # Clicking button
            driver.set_page_load_timeout(5)
            try:
                driver.find_element_by_id("submitButton").click()
            except TimeoutException:
                logging.debug("Ded af")
                
            logging.debug("Out of the rabbit hole")

            # Waiting 5 seconds so I can get redirected around
            time.sleep(5)
            logging.debug("Done waiting 5 seconds")
            # Checking where I am after I logged in
            redirect = driver.current_url
            logging.debug("Final URL: {}".format(redirect))
                
            # What is on the page?
            past_login = str(driver.page_source)

            # Checking to see if I am still on the login page
            if "loginPage" in redirect:
                # Check for 2FA
                mfa = re.search("Verification required to continue.",past_login)
                
                # I confirmed that I am on 2FA
                if mfa:
                    logging.info("2FA required on SSO page")
                    full_information[base_url]["Access"] = "No"
                    full_information[base_url]["Notes"] = "2FA on SSO"
                
                # I don't know what I am on but I am here...
                else:
                    logging.info("Something happened?")
                    full_information[base_url]["Access"] = "No"
                    full_information[base_url]["Notes"] = "Stuck on SSO page"
                
                if ".login.com" in redirect:
                    full_information[base_url]["Scope"] = "Yes"
                else:
                    full_information[base_url]["Scope"] = "No"

                full_information[base_url]["Redirected"] = redirect

            # I am somewhere that is not an expected logon page
            else:
                full_information[base_url]["Access"] = "Yes"
                full_information[base_url]["Notes"] = "This is where the login redirected me to"

        # I am not on the SSO page
        else:
            logging.info("Not on SSO page")
            full_information[base_url]["SSO"] = "No"
            full_information[base_url]["Access"] = "Yes"

        if url not in redirect:
            logging.info("Redirected to: {}".format(redirect))
            full_information[base_url]["Redirected"] = "Redirect to: " + redirect
        else:
            logging.info("Not redirected")
            full_information[base_url]["Redirected"] = redirect           

        if ".login.com" in redirect:
            full_information[base_url]["Scope"] = "URL in scope"
        else:
            full_information[base_url]["Scope"] = "URL out of scope"

        page_source = str(bs4(str(driver.page_source), "html.parser"))

        # Check to see if Missing auth is seen
        missing_auth = re.search("---",page_source, re.IGNORECASE)

        # Checking for that amazing error page that I love seeing on every url that resolves!
        error_page = re.search("---",page_source, re.IGNORECASE)
        
        # Checking for the random string page
        rip_page = re.search("---",page_source, re.IGNORECASE)
        
        # Checking for the random string page
        rip_app = re.search("---",page_source, re.IGNORECASE)

        # Checking for soap error page
        soap_err = re.search("---",page_source, re.IGNORECASE)

        logging.info("Checking for known pages")
        logging.debug("{}".format(page_source))
        logging.debug("Missing Auth: {}\nlogin Error: {}\nRIP page: {}\nSOAP page:{}".format(missing_auth,error_page,rip_page,rip_app,soap_err))
        if missing_auth:
            full_information[base_url]["Notes"] = "Missing Authentication Token"
            logging.info("Missing Authentication Token")
        if error_page:
            full_information[base_url]["Notes"] = "login Error Page"
            logging.info("login Error Page")
        if rip_page:
            full_information[base_url]["Notes"] = "\"---\" page"
            logging.info("\"---\" page")
        if rip_app:
            full_information[base_url]["Notes"] = "\"---\" page"
            logging.info("\"---\" page")
        if soap_err:
            full_information[base_url]["Notes"] = "SOAP error page"
            logging.info("SOAP error page page")
        
        # Closing the browser
        driver.close()

    except KeyError as e:
        logging.error("KeyError: {}".format(e))
        driver.quit()
        return "No"

    except selenium.common.exceptions.WebDriverException as e: 
        logging.debug("WebDriverException: {}".format(e))
        full_information[base_url]["SSO"] = "No"
        full_information[base_url]["Access"] = "No"
        full_information[base_url]["Redirected"] = "No"
        full_information[base_url]["Scope"] = "URL in scope"
        full_information[base_url]["Notes"] = e
        full_information[base_url]["Date"] = now_now
        full_information[base_url]["Datez"] = now_now_2
        driver.close()

    except Exception as e:
        logging.error("Error rip: {}".format(e))
        driver.quit()
        return "No"


def create_xlsx(full_information, md, rip):
    if not rip:
        if md:
            logging.info("Writing Markdown Table")
            f = open('Results.md', 'w')
            f.write("| Base URL | Date Last Tested | Resolves | SSO | Access | Redirect | Scope | Notes |\n")
            f.write("|----------|------------------|----------|-----|--------|----------|-------|-------|\n")
            for x,y in full_information.items():
                logging.info("URL: {}\t\tInformation: {}".format(x,y))
                f.write("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(x,y["Date"],y["Resolves"],y["SSO"],y["Access"],str(y["Redirected"]).strip(),y["Scope"],str(y["Notes"]).strip()))
            f.close()
            logging.info("Finished writing Markdown Table")
        else:
            logging.info("Writing CSV")
            f = open('Results.csv', 'w')
            f.write("Base URL,Date Last Tested,Resolves,SSO,Access,Redirect,Scope\n")
            for x,y in full_information.items():
                logging.info("URL: {}\t\tInformation: {}".format(x,y))
                f.write("{},{},{},{},{},{},{},{}\n".format(x,y["Date"],y["Resolves"],y["SSO"],y["Access"],str(y["Redirected"]).strip(),y["Scope"],str(y["Notes"]).strip()))
            f.close()
            logging.info("Finished writing CSV")
        f = open('Log.md', 'a+')
        for x,y in full_information.items():
            logging.info("URL: {}\t\tInformation: {}".format(x,y))
            f.write("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(x,y["Datez"],y["Resolves"],y["SSO"],y["Access"],str(y["Redirected"]).strip(),y["Scope"],str(y["Notes"]).strip()))
        f.close()
        
    else:
        print("\n\n| Base URL | Date Last Tested | Resolves | SSO | Access | Redirect | Scope | Notes |\n")
        print("    |----------|------------------|----------|-----|--------|----------|-------|-------|\n")
        for x,y in full_information.items():
            print("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(x,y["Date"],y["Resolves"],y["SSO"],y["Access"],str(y["Redirected"]).strip(),y["Scope"],str(y["Notes"]).strip()))
        logging.info("Nothing saved")


# This version needs is for single URLs
def get_arg2():
    parser = argparse.ArgumentParser(description='URLBuster')
    # Add a file as an argument
    parser.add_argument('hostname', help='Hostname to check')
    parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    parser.add_argument("-m","--markdown",dest="markdown",action="store_true",help="Outputs Obsidian instead of csv",default=False)
    parser.add_argument("-p","--ports",dest="ports",help="Extra port to check",default=False)
    parser.add_argument("-x","--nothing", dest="rip", action="store_true", help="Do not save results", default=False)
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    return args


# This version needs is for list and more complex URLs
def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    # CLI Version
    parser.add_argument("-m","--markdown",dest="markdown",action="store_true",help="Outputs Obsidian instead of csv",default=False)
    parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    parser.add_argument("-p","--ports",dest="ports",help="Extra port to check",default=False)
    parser.add_argument("-x","--nothing", dest="rip", action="store_true", help="Do not save results", default=False)
    # File version
    parser.add_argument("-f","--file",dest="file", help="Name of the file with the URLs")
    parser.add_argument("-e","--email",dest="email", help="Email to log in with on SSO")
    parser.add_argument("-P","--Password",dest="password", help="Password to log in with on SSO")
    
    options = parser.parse_args()
    if not options.file:
        options.file = "urls.txt"
    if not options.email:
        options.email = "---"
    if not options.password:
        options.password = "---"
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
        global DEBUG
        DEBUG = True
    else:
        logging.basicConfig(level=logging.INFO)
    return options


if __name__ == "__main__":
    main()
