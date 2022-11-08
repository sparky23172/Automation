# Name: Hokage.py
# Version: 1.2
# Date: 01/23/2022

# Basic
import subprocess
import argparse
import datetime
import logging
import shutil
import time 
import sys
import re
import os 


PAKKUN = os.path.exists("slack-bot")
SELF = "Hokage"

NO_FILE = os.path.exists("stats/Pakkun_No.txt")
SCAN_FILE = os.path.exists("stats/Pakkun_Scan.txt")
STAGE2_FILE = os.path.exists("stats/Pakkun_Stage2.txt")
ERROR_FILE = os.path.exists("stats/Pakkun_OoS.txt")

NINJA_LIST = "Kakashi|D7Buster"

# Pass a hostname through commandline
def main():
    options = get_arg()
    logging.info("Waking up the Hokage of the Hidden Leaf Village")

    results = subprocess.check_output("ps afx | grep -Pi '{}' | grep python3".format(NINJA_LIST), shell=True).decode("utf-8").split("\n")
    if len(results) > 2:
        logging.info("Someone from the leaf village is out on a mission. Letting them complete their mission first.")
        pakkun("Hokage did not run. Someone is currently on a mission", options.whoami, options.task)
        sys.exit()
    else:
        logging.info("Hokage did not run into any ninjas out on a mission")
        pakkun("Hokage did not run into any ninjas out on a mission", options.whoami, options.task)

    if options.task == "No":
        result = check_no_results()

    elif options.task == "Scan":
        result = check_scan_results()

    elif options.task == "Stage2":
        stage2_result = check_stage2_results()

    elif options.task == "Weekly":
        no_result = check_no_results()
        scan_result = check_scan_results()
        stage2_result = check_stage2_results()

        result = (no_result + scan_result + stage2_result)

    elif options.task == "Startup":
        startup()
        logging.info("The Hokage has completed startup")
        pakkun("The Hokage has completed startup", options.whoami, options.task)
        sys.exit(0)

    else:
        logging.fatal("Option: {} is not a valid option".format(options.task))
        sys.exit(0)


    pakkun("Hokage has completed the initial task for {}".format(options.task), options.whoami, options.task)

    mad_stats = get_stats(result,options.task)
    pakkun("Hokage grabbed the stats from this weeks mission", options.whoami, options.task)
    
    logging.debug("Mad stats: {}".format(mad_stats))

    logging.info("Hokage is getting ready for the next set of missions")
    pakkun("Hokage is getting ready for the next set of missions", options.whoami, options.task)
    clean_up(options.task)

    logging.info("The Hokage has completed its tasks: {}".format(options.task))
    pakkun("The Hokage has completed its tasks: {}".format(options.task), options.whoami, options.task)
    sys.exit(0)


def startup():
    logging.info("Hokage is preforming initial start up")
    pakkun("Hokage is preforming initial start up", SELF, "Startup")

    crontab = """
0   9         * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Kakashi.py -d -m -t No 
0   11        * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Hokage.py -d -t No

30  11        * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Kakashi.py -d -m -t Scan
0   12        * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Hokage.py -d -t Scan

0   2         * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Kakashi.py -d -m -t Stage2
0   20        * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Hokage.py -d -t Stage2

05  2         * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Kakashi.py -d -m -t Stage3

0   0,9,12,18 * * 1-5 cd ~/Downloads/HiddenLeaf; python3 Kakashi.py -d -m -t Anbu-Sai

"""
    f = open("crontab.txt", "w")
    f.write(crontab)
    f.close()

    logging.info("Hokage has installed crontab. Please run crontab -e to add the following crontab")


def clean_up(task):
    logging.info("Cleaning up")

    # What is this???
    # mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_No.txt"))))

    # In reverse order so it makes sense
    # os.path.getmtime("stats/Pakkun_No.txt")))) - This grabs the last time the file was modified in EPOCH time
    # time.ctime(                                - This converts the time to a time stamp
    # time.strptime(                             - This converts the time to a string
    # time.strftime("%m-%d-%Y",                  - This changes the string into a format that you choose
    
    history_directory = os.path.exists("stats/history")
    if not history_directory:
        os.mkdir("stats/history")
    else:
        logging.debug("History directory already exists")

    if task == "No":
        mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_No.txt"))))
        logging.debug("Pakkun_No Last Modified time: {}".format(mod_time))
        shutil.copyfile("stats/Pakkun_No.txt", "stats/history/Pakkun_No_{}.txt".format(mod_time))
        shutil.move("stats/Pakkun_Nope.txt", "stats/Pakkun_No.txt")
    elif task == "Scan":
        mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_Scan.txt"))))
        logging.debug("Pakkun_Scan Last Modified time: {}".format(mod_time))
        shutil.copyfile("stats/Pakkun_Scan.txt", "stats/history/Pakkun_Scan_{}.txt".format(mod_time))
        shutil.move("stats/Pakkun_To_Scan.txt", "stats/Pakkun_Scan.txt")
    elif task == "Stage2":
        mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_Stage2.txt"))))
        logging.debug("Pakkun_Stage2 Last Modified time: {}".format(mod_time))
        shutil.copyfile("stats/Pakkun_Stage2.txt", "stats/history/Pakkun_Stage2_{}.txt".format(mod_time))
        shutil.move("stats/Pakkun_Stable.txt", "stats/Pakkun_Stage2.txt")
    elif task == "Weekly":
        no_mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_No.txt"))))
        logging.debug("Pakkun_No Last Modified time: {}".format(no_mod_time))
        shutil.copyfile("stats/Pakkun_No.txt", "stats/history/Pakkun_No_{}.txt".format(no_mod_time))

        scan_mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_Scan.txt"))))
        logging.debug("Pakkun_Scan Last Modified time: {}".format(scan_mod_time))
        shutil.copyfile("stats/Pakkun_Scan.txt", "stats/history/Pakkun_Scan_{}.txt".format(scan_mod_time))
        
        stage2_mod_time = time.strftime("%m-%d-%Y", time.strptime(time.ctime(os.path.getmtime("stats/Pakkun_Stage2.txt"))))
        logging.debug("Pakkun_Stage2 Last Modified time: {}".format(stage2_mod_time))
        shutil.copyfile("stats/Pakkun_Stage2.txt", "stats/history/Pakkun_Stage2_{}.txt".format(stage2_mod_time))

        shutil.move("stats/Pakkun_Nope.txt", "stats/Pakkun_No.txt")
        shutil.move("stats/Pakkun_To_Scan.txt", "stats/Pakkun_Scan.txt")
        shutil.move("stats/Pakkun_Stable.txt", "stats/Pakkun_Stage2.txt")


def get_stats(le_stats,task):
    logging.info("Getting stats")
    Hokage = os.path.exists("stats/Hokage_Stats.json")
    today = datetime.datetime.now()
    right_meow = today.strftime("%m/%d/%y")

    if not Hokage:
        count = 1
    else:
        f = open('stats/Hokage_Stats.json', "r")
        file = f.readlines()
        f.close()
        logging.debug("File length: {}".format(len(file)))
        if len(file):
            count = len(file) + 1
        else:
            count = 1
    
    stats = {"date":right_meow,"resolve_stats":{},"scan_stats":{},"stage2_stats":{},"count":count,"TBA":""}
    
    logging.debug("{}".format(stats))

    logging.info("Stats: {}".format(le_stats))
    logging.info("Task: {}".format(task))
    if task == "No":
        stats["resolve_stats"] = {"new":le_stats[0],"old":le_stats[1],"total_new":le_stats[2],"total_old":le_stats[3]}
    elif task == "Scan":
        stats["scan_stats"] = {"new":le_stats[0],"old":le_stats[1],"total_new":le_stats[2],"total_old":le_stats[3]}
    elif task == "Stage2":
        stats["stage2_stats"] = {"new":le_stats[0],"old":le_stats[1],"total_new":le_stats[2],"total_old":le_stats[3]}
    elif task == "Weekly":
        stats["resolve_stats"] = {"new":le_stats[0],"old":le_stats[1],"total_new":le_stats[2],"total_old":le_stats[3]}
        stats["scan_stats"] = {"new":le_stats[4],"old":le_stats[5],"total_new":le_stats[6],"total_old":le_stats[7]}
        stats["stage2_stats"] = {"new":le_stats[8],"old":le_stats[9],"total_new":le_stats[10],"total_old":le_stats[11]}

    logging.debug("{}".format(stats))
    f = open('stats/Hokage_Stats.json', 'a+')
    f.write("{} - {}\n".format(count, stats))
    f.close()
    return stats


def check_no_results():
    init = os.path.exists("stats/Pakkun_No.txt")
    done = os.path.exists("stats/Pakkun_Nope.txt")
    new = 0
    old = 0

    if init and done:
        f = open("stats/Pakkun_No.txt", "r")
        init_lines = f.readlines()
        f.close()
        f = open("stats/Pakkun_Nope.txt", "r")
        done_lines = f.readlines()
        f.close()

        logging.debug("Before unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        init_lines = list(set(init_lines))
        done_lines = list(set(done_lines))

        logging.debug("After unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        for x in done_lines:
            if not x:
                continue
            test = x.strip()
            test = test.replace("*", "")
            test = test.lower()
            found = False
            for y in init_lines:
                if not y:
                    continue
                test2 = y.strip()
                test2 = test2.replace("*", "")
                test2 = test2.lower()
                # logging.debug("Comparing {} to {}".format(test, test2))
                compare = re.findall(test, test2)
                if compare:
                    found = True
            
            if found:
                logging.debug("Found on both lists {}".format(test))
                old += 1
            else:
                logging.info("Only found on new list: {}".format(test))
                new += 1
    
    return (new, old, len(init_lines), len(done_lines))


def check_scan_results():
    init = os.path.exists("stats/Pakkun_Scan.txt")
    done = os.path.exists("stats/Pakkun_To_Scan.txt")
    new = 0
    old = 0

    if init and done:
        f = open("stats/Pakkun_Scan.txt", "r")
        init_lines = f.readlines()
        f.close()
        f = open("stats/Pakkun_To_Scan.txt", "r")
        done_lines = f.readlines()
        f.close()

        logging.debug("Before unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        init_lines = list(set(init_lines))
        done_lines = list(set(done_lines))

        logging.debug("After unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        for x in done_lines:
            if not x:
                continue
            test = x.strip()
            test = test.replace("*", "")
            test = test.lower()
            found = False
            for y in init_lines:
                if not y:
                    continue
                test2 = y.strip()
                test2 = test2.replace("*", "")
                test2 = test2.lower()
                # logging.debug("Comparing {} to {}".format(test, test2))
                compare = re.findall(test, test2)
                if compare:
                    found = True
            
            if found:
                logging.debug("Found on both lists {}".format(test))
                old += 1
            else:
                logging.info("Only found on new list: {}".format(test))
                new += 1
    
    return (new, old, len(init_lines), len(done_lines))


def check_stage2_results():
    init = os.path.exists("stats/Pakkun_Stage2.txt")
    done = os.path.exists("stats/Pakkun_Stable.txt")

    new = 0
    old = 0

    if init and done:
        f = open("stats/Pakkun_No.txt", "r")
        init_lines = f.readlines()
        f.close()
        f = open("stats/Pakkun_Nope.txt", "r")
        done_lines = f.readlines()
        f.close()

        logging.debug("Before unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        init_lines = list(set(init_lines))
        done_lines = list(set(done_lines))

        logging.debug("After unique sort: Init - {} vs Done - {}".format(len(init_lines), len(done_lines)))

        for x in done_lines:
            if not x:
                continue
            test = x.strip()
            test = test.replace("*", "")
            test = test.lower()
            found = False
            for y in init_lines:
                if not y:
                    continue
                test2 = y.strip()
                test2 = test2.replace("*", "")
                test2 = test2.lower()
                # logging.debug("Comparing {} to {}".format(test, test2))
                compare = re.findall(test, test2)
                if compare:
                    found = True
            
            if found:
                logging.debug("Found on both lists {}".format(test))
                old += 1
            else:
                logging.info("Only found on new list: {}".format(test))
                new += 1
    
    return (new, old, len(init_lines), len(done_lines))


def pakkun(message, whoami, location):
    logging.debug("Pakkun debugger \nmessage: {}, whoami: {}, location: {}".format(message,whoami,location))
    os.system("./slack-bot -m '{}' -w {} -x {} ".format(message,whoami,location))


# This version needs is for list and more complex URLs
def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    # CLI Version
    parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    parser.add_argument("-w","--whoami", dest="whoami", help="Who to report as", default="Home")
    parser.add_argument("-t","--task", dest="task", help="Which task to run", default="Not called by Kakashi")
    parser.add_argument("-f","--fang", dest="fang",action="store_false", help="Use arg to turn url rotation function off", default=True)
    # File version
    
    options = parser.parse_args()
    if not options.fang:
        global FANG
        FANG = False
        logging.info("Fang mode is off")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
        global DEBUG
        DEBUG = True
    else:
        logging.basicConfig(level=logging.INFO)
    return options


if __name__ == "__main__":
    main()
