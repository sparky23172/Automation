# Name: Sai.py
# Version: 1.1
# Date: 02/02/2022

# Basic
import datetime
import logging
import time
import os

# Specialized
import subprocess
import Kakashi


# Find the current directory
HOME = os.getcwd()


def stage2Check(file_location):
    ''' This function checks the new urls found from amass and checks it against stage2 to possibly add more urls '''

    file_location = file_location.strip("\"")

    f = open(file_location, "r")
    lines = f.readlines()
    f.close()

    count = 0

    for line in lines:
        logging.debug("Line: {} - raw".format(line))
        if line.strip() != "":
            line = line.strip("http")
            logging.debug("Line: {} - without http".format(line))
            line = line.strip("s")
            logging.debug("Line: {} - without s".format(line))
            line = line.strip("://")
            logging.debug("Line: {} - without ://".format(line))

            if line.strip() not in open("{}/stats/Pakkun_Stage2.txt".format(HOME)).read():
                count += 1
                logging.debug("Line: {} - not in stage2. Adding to Kakashi.pakkun_Stage2.txt".format(line))
                f = open("{}/stats/Pakkun_Stage2.txt".format(HOME), "a+")
                f.write(line.strip() + "\n")
                f.close()

    logging.info("Sai added {} new urls to Stage2".format(count))
    return count


def attac():
    ''' This function will run an auto amass enum, httpx anything new, and then run nuclei against the results of httpx. It will return the nuclei_file location '''

    today = datetime.datetime.now()
    right_meow = today.strftime("%m_%d_%y")
    
    start = Kakashi.stopwatch(None)
    tic = time.perf_counter()
    who = "new domains"
    
    # Step 1: Get the list of domains
    # init_enum = "amass enum -config \"{0}/Anbu/Sais_tools/amass_config.ini\" -df \"{0}/Anbu/Sais_tools/domains.txt\" -blf {0}/Anbu/Sais_tools/domains_blacklisted.txt".format(HOME)
    # logging.debug("Running: {}".format(init_enum))
    # Kakashi.pakkun("Starting amass with Sai", "Anbu", "Sai")
    # one_results = subprocess.check_output('amass enum -config "{0}/Anbu/Sais_tools/amass_config.ini" -df "{0}/Anbu/Sais_tools/domains.txt" -blf {0}/Anbu/Sais_tools/domains_blacklisted.txt'.format(HOME), shell=True).decode("utf-8").split("\n")
    # Kakashi.pakkun("Finished running amass with Sai", "Anbu", "Sai")
    # answer = "total results?: {}".format(len(one_results))
    # logging.debug(one_results)

    # end = Kakashi.stopwatch(None)
    # toc = time.perf_counter()
    # f = open("Kakashi_L33t_Numb3r5.csv", "a+")
    # f.write("{},{},{},{},{:0.2f} Seconds,{}\n".format("Anbu-Sai", who, start, end, (toc - tic), answer))
    # f.close()

    # # Step 2: Get list of new domains and run it through httpx
    # start = Kakashi.stopwatch(None)
    # tic = time.perf_counter()

    # httpx_file = "\"{}/Anbu/Sais_tools/httpx_output/httpx_output_{}\"".format(HOME, right_meow)
    # init_track = "amass track -df \"{0}/Anbu/Sais_tools/domains.txt\" | grep \"Found:\" | grep -oE \"(([a-zA-Z](-?[a-zA-Z0-9])*)\.)+[a-zA-Z]{3}\" | httpx -silent -ports {1} -o {2}".format(HOME,Kakashi.HTTP_PORTS,httpx_file,"{2,}")
    # logging.debug("Running: {}".format(init_track))
    # Kakashi.pakkun("Starting running httpx with Sai", "Anbu", "Sai")
    # two_results = subprocess.check_output("{}".format(init_track), shell=True).decode("utf-8").split("\n")
    # Kakashi.pakkun("Finished running httpx with Sai", "Anbu", "Sai")
    # logging.debug("Stage 2 results: {}".format(two_results))

    # answer = "total results?: {}".format(len(two_results))
    # end = Kakashi.stopwatch(None)
    # toc = time.perf_counter()
    # f = open("Kakashi_L33t_Numb3r5.csv", "a+")
    # f.write("{},{},{},{},{:0.2f} Seconds,{}\n".format("Anbu-Sai", who, start, end, (toc - tic), answer))
    # f.close()

    # two_results = ["https://www.goodrx.com"]

    # logging.debug("Results: {}".format(two_results))
    # logging.debug("Results: {}".format(two_results[0]))

    # # Testing
    

    # # Step 2.5: Upload the httpx results to Kakashi.pakkun_Stage2
    # if not two_results[0]:
    #     logging.warning("No results from httpx")
    #     Kakashi.pakkun("Sai did not find anything new to add to Stage2", "Anbu", "Sai")
    #     return None
    # else:
    #     new_stage_2 = stage2Check(httpx_file)
    #     Kakashi.pakkun("Sai added {} new urls to Stage2".format(new_stage_2), "Anbu", "Sai")

    # Step 3: Run the new domains through nuclei
    start = Kakashi.stopwatch(None)
    tic = time.perf_counter()

    nuclei_file = "\"{0}/Anbu/Sais_tools/nuclei_output/nuclei_output_{1}\"".format(HOME,right_meow)
    init_nuclei = "nuclei -l \"{0}/Anbu/Sais_tools/httpx_output/httpx_output_{1}\" -o {2} -nc".format(HOME,right_meow, nuclei_file)
    logging.debug("Running: {}".format(init_nuclei))
    Kakashi.pakkun("Starting nuclei with Sai", "Anbu", "Sai")
    three_results = subprocess.check_output("{}".format(init_nuclei), shell=True).decode("utf-8").split("\n")
    Kakashi.pakkun("Finished running nuclei with Sai", "Anbu", "Sai")
    logging.debug(three_results)

    answer = "total results?: {}".format(len(three_results))
    end = Kakashi.stopwatch(None)
    toc = time.perf_counter()
    f = open("Kakashi_L33t_Numb3r5.csv", "a+")
    f.write("{},{},{},{},{:0.2f} Seconds,{}\n".format("Anbu-Sai", who, start, end, (toc - tic), answer))
    f.close()         

    return nuclei_file


def report(nuclei_file, whoami, file):
    ''' This function will take the nuclei_file (either LOCATION or the raw results), who is giving it the results, and if it is a file or not. Then it reports the results '''
    
    # Step 4: Process the results to report back
    # check to see if the nuclei_file is a file to read or if it is the raw results

    if file:
        nuclei_file = nuclei_file.strip("\"")

    if file:
        f = open(nuclei_file, "r")
        nuclei_results = f.readlines()
        f.close()
    else:
        nuclei_results = nuclei_file

    stats = {"info":0,"low":0,"medium":0,"high":0, "critical":0 ,"other":0}

    for line in nuclei_results:
        if "[info]" in line:
            stats["info"] += 1
        elif "[low]" in line:
            stats["low"] += 1
        elif "[medium]" in line:
            stats["medium"] += 1
        elif "[high]" in line:
            stats["high"] += 1
        elif "[critical]" in line:
            stats["critical"] += 1
        else:
            stats["other"] += 1
    
    if stats["medium"] != 0 or stats["high"] != 0 or stats["critical"] != 0:
        logging.info("Anbu-Sai found something that needs to be looked at")
        logging.info("Anbu-Sai found {} info, {} low, {} medium, {} high, {} critical, {} other".format(stats["info"], stats["low"], stats["medium"], stats["high"], stats["critical"], stats["other"]))
        Kakashi.pakkun("Anbu-Sai found {} info, {} low, {} medium, {} high, {} critical, {} other".format(stats["info"], stats["low"], stats["medium"], stats["high"], stats["critical"], stats["other"]), "Anbu", whoami)

    return stats


def prep():
    ''' This function will prepare the environment for the Anbu-Sai tool '''

    logging.debug("Sai is currently at: {}".format(HOME))

    if not os.path.exists("{}/Anbu/Sais_tools/httpx_output".format(HOME)):
        os.mkdir("{}/Anbu/Sais_tools/httpx_output".format(HOME))
        logging.debug("Sai made a folder for httpx_output")
    else:
        logging.debug("Directory {}/Anbu/Sais_tools/httpx_output already exists".format(HOME))

    if not os.path.exists("{}/Anbu/Sais_tools/nuclei_output".format(HOME)):
        os.mkdir("{}/Anbu/Sais_tools/nuclei_output".format(HOME))
        logging.debug("Sai made a folder for nuclei_output")
    else:
        logging.debug("Directory {}/Anbu/Sais_tools/nuclei_output already exists".format(HOME))


def main():
    ''' This is the main function for Sai'''
    logging.info("Starting Sai")
    
    logging.debug("Sai is about to start prep")
    prep()
    
    logging.debug("Sai has finished prep and is starting attac")
    name = attac()

    if not name:
        return "No new results found"
    
    logging.debug("Sai has finished attac and is starting report")
    stats = report(name, "Sai", "File")

    logging.info("Finished Sai")
    return stats

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
