# Name: Anbu.py
# Version: 1.0
# Date: 02/01/2022

# Basic
import logging

# Specialized
import Anbu.Sai as Sai


def handler(who):
    ''' Checks to see who among the Anbu is being called '''
    logging.info("Calling the Anbu squad. Looking for {}".format(who.strip("Anbu-")))
    if "Sai" in who:
        logging.info("Sai is here!")
        stats = Sai.main()
        return stats

