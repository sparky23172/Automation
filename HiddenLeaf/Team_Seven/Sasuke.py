# Name: Team_Seven/Sasuke.py
# Version: 1.0
# Date: 01/24/2022


import logging
import nmap
import os
import shutil
import datetime
import Team_Seven.Sakura as Sakura


def stopwatch(arg):
    """ Takes nothing
    Returns current time
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


def check_open_ports(url, HTTP_PORTS):
    scanner = nmap.PortScanner()
    stats = {}
    prelude = Sakura.check_resolves(url)
    if prelude == "Not Resolved":
        return "Not Resolved"
    logging.info("Handing off from Sakura to Sasuke")

    try:
        if not os.path.exists("results"):
            os.mkdir("results")
            logging.debug("Sasuke made a folder for all the results")
        else:
            logging.debug("Directory results already exists")
        
        
        logging.debug("Sasuke is making a folder for the results")
        # Make a directory for the url
        if not os.path.exists("results/{}".format(url)):
            os.mkdir("results/{}".format(url))
            logging.debug("Sasuke made a folder for the results")
        else:
            logging.debug("Directory results/{} already exists".format(url))

        logging.debug("Scanning {}".format(url))

        file = "{}-{}.gnmap".format(stopwatch("File"),url)

        # NMAP command
        results = scanner.scan(hosts=url, arguments='-sT -T3 -oG {}'.format(file), ports=HTTP_PORTS)
        logging.debug("Scan of {} completed".format(url))
        # Blind copy for the history
        shutil.copyfile("{}".format(file), "results/{}/{}".format(url,file))

        # Blind results
        logging.debug("Results of scan: {}".format(results))
        # Extract command
        command = results['nmap']['command_line']
        # Extract scan time
        scan_time = results['nmap']['scanstats']['elapsed']
        # Extract up hosts results
        uphosts = int(results['nmap']['scanstats']['uphosts'])
        ip = ""
        
        for k, v in results['scan'].items():
            logging.info("IP of {}: {}".format(url,k))
            ip = k
        
        # Writing for logs
        stats[ip] = {}
        # What was used to scan
        stats[ip]["command"] = command
        # Scan time
        stats[ip]["time"] = scan_time
        # Default open state
        stats[ip]["open"] = False
        # If host is "up"
        stats[ip]["hosts_up"] = uphosts

        if uphosts > 0:
            try:
                for k, v in results['scan'][ip]["tcp"].items():
                    
                    # Ports stats
                    logging.info("\tPort: {}".format(k))
                    logging.info("\tState: {}".format(v["state"]))
                    logging.info("\tReason: {}".format(v["reason"]))
                    
                    # Check if port is open
                    stats[ip][k] = {}
                    if results['scan'][ip]["tcp"][k]["state"].lower() == "open":
                        stats[ip]["open"] = True
                        logging.info("[!] {} has an open port at {}".format(ip,k))
                    
                    # State of the port
                    stats[ip][k]["State"] = v["state"]
                    
                    # Why it is that state
                    stats[ip][k]["State"] = v["reason"]
                    logging.debug("Open state: {}".format(stats[ip]["open"]))    
                    
                    # Save to good target directory
                    if stats[ip]["open"] == True:
                        if not os.path.exists("up_targets"):
                            os.mkdir("up_targets")
                            logging.debug("Sasuke made a folder for all the up_targets")
                        else:
                            logging.debug("Directory up_targets already exists")

                        if not os.path.exists("up_targets/{}".format(url)):
                            os.mkdir("up_targets/{}".format(url))
                        else:
                            logging.debug("Directory up_targets/{} already exists".format(url))
                        shutil.copyfile("{}".format(file), "up_targets/{}/{}".format(url,file))
                        os.remove(file) 
                        return ["Up",stats]
                else:
                    os.remove(file) 
                    return ["Down",stats]
            except KeyError:
                logging.info("\tNo TCP ports found")
                os.remove(file) 
                return ["Down",stats]
        else:
            logging.info("\tNo up hosts found")
            os.remove(file) 
            return ["Down",stats]
    except Exception as e:
        os.remove(file) 
        return [e,stats]
