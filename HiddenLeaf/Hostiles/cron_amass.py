# Name: cron_amass.py
# Version: 1.0
# Date: 02/01/2022

# Basic
import datetime
import logging

# Specialized
import subprocess


URL = "login.com"
HOME = "~"
PORTS = "66,80,81,443,445,457,1080,1100,1241,1352,1433,1434,1521,1944,2301,3128,3306,4000,4001,4002,4100,4433,5000,5432,5800,5801,5802,6346,6347,7001,7002,8008,8080,8443,8888,30821"


def main():

    logging.info("Starting Matt cronjob")
    today = datetime.datetime.now()
    right_meow = today.strftime("%Y-%m-%d_%H:%M")
    one_results = subprocess.check_output('amass enum -config "{0}/autoscan/amass_config.ini" -df "{0}/autoscan/domains.txt" -blf {0}/autoscan/domains_blacklisted.txt'.format(HOME), shell=True).decode("utf-8").split("\n")
    print(one_results)
    two_results = subprocess.check_output('amass track -df "{0}/autoscan/domains.txt" | grep "Found:" | grep -oE "(([a-zA-Z](-?[a-zA-Z0-9])*)\.)+[a-zA-Z]{1}" | httpx -silent -ports {2} -o "{0}/autoscan/httpx_output/httpx_output_{1}"'.format(HOME,"{2,}",right_meow,PORTS), shell=True).decode("utf-8").split("\n")
    print(two_results)
    three_results = subprocess.check_output('nuclei "{0}/autoscan/httpx_output/httpx_output_{1}" -o "{0}/autoscan/nuclei_output/nuclei_output_{1}" | grep -v "[info]" | notify -provider-config "{0}/autoscan/notify_discord.yaml"'.format(HOME,right_meow), shell=True).decode("utf-8").split("\n")
    print(three_results)


if __name__ == "__main__":
    main()
