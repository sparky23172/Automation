# Name: Team_Seven/Sakura.py
# Version: 1.0
# Date: 01/24/2022



import logging
import socket

def check_resolves(url):
    """ Takes a URL
    Checks to see if the URL resolves to an IP address.
    Returns Yes, No, RIP (for timeouts trying to connect which means something could be there), or the error
    """
    logging.debug("Checking to see if {} resolves".format(url))
    ## Check to see if there is a protocol in the url passed
    if "https://" in url:
        url = url.replace("https://","")
    elif "http://" in url:
        url = url.replace("http://","")

    if "/" in url:
        url = url.split("/")[0]

    ## Check to see if there is a port in the url passed
    if ":" in url:
        logging.debug(url)
        temp_url = url.split(":")
        url = temp_url[0]

    try:
        socket.gethostbyname(url)
        return "Resolved"
    except socket.gaierror as e:
        try:
            logging.info("{} doesn't have an IP assosiated with it... Testing if there is anything on 443 just in case".format(url))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((url, 443))
            s.close()
        except socket.timeout as e:
            logging.error("Timeout Occurred: {}".format(e))
            return "Resolved"
        except socket.gaierror as e:
            logging.error("Still can't find: {}".format(e))
            return "Not Resolved"
        except Exception as e:
            if "Connection Refused" in str(e):
                logging.error("{} is refusing connections".format(url))
                return "Refused"
            logging.error("Error?: {}".format(e))
            return e
