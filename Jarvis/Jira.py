# Name: JiraCRON.py

from openpyxl import load_workbook
from jira import JIRA
import pandas as pd

from datetime import datetime, timezone
import argparse
import logging
import time
import sys
import os
import re


now = datetime.now(timezone.utc)
rightMeow = now.strftime('%m/%d/%Y')
fileRightMeow = now.strftime('%m-%d-%Y')

def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    # CLI Version
    parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    # File version
    parser.add_argument("-H","--Head",dest="Head", help="If the program should be ran headless. Argument will turn headless mode off",default=False, action="store_true")
    parser.add_argument("-u","--url",dest="url", help="URL to be scanned")
    parser.add_argument("-l","--location",dest="location", default="Jarvis_Brain.xlsx", help="Location of the excel file")
    parser.add_argument("-v","--version",dest="version", default="1", help="XLSX version")
    parser.add_argument("-D","--Directory",dest="directory", help="Name of the output directory. If none is provided, name will be whatever the URL is with _ instead of . in the name")

    options = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
        global DEBUG
        DEBUG = True
    else:
        logging.basicConfig(level=logging.INFO)
    return options


def XML_locate(loc):
    ls = os.listdir(loc)
    logging.debug(ls)
    xml = ""
    for file in ls:
        if ".xlsx" in file:
            xml = loc + file

    if xml:
        logging.info("Found a file with XML named \"{}\"".format(xml))
    else:
        pwd = os.getcwd()
        logging.error("No file with xml located at {0}! Please add an xml file to {0} or add the path with argument -l".format(pwd))
        sys.exit(1)

    return xml


def jiraPull( jira):
    leetSauce = {}
    weakSauce = []
    oldSauce = {}

    for issue in jira.search_issues('issuetype = Window AND project = CLIENT AND status != "Closed" ORDER BY created DESC'.format(), maxResults=1000):
        time2 = issue.fields.created
        report2 = datetime.strptime(time2, '%Y-%m-%dT%H:%M:%S.%f%z')
        strCreate = report2.strftime('%m/%d/%Y')
        daysUp = (now - report2).days

        logging.debug('\nAssigned: {}\n\tTicket Status: {}\n\tKey: {}\n\tSummary: {}\n\tFields Created: {}\n\tToday: {}\n\tDays Up: {}'\
        .format(issue.fields.assignee ,issue.fields.status, issue.key, issue.fields.summary, strCreate, rightMeow, daysUp))

        ticket = str(issue.fields.summary).strip()[:5]
        if not re.findall("(\d{5})",str(ticket)):
            ticket = str(issue.fields.summary).strip()
        else:
            ticket = str(issue.fields.summary).strip()[:5]

        oldSauce[issue.key] = {
            "ticket": ticket,
            "created": strCreate,
            "daysUp": daysUp,
            "Jira": "https://client.atlassian.net/browse/{}".format(str(issue.key))
            }

    logging.debug("Number of Tickets in retests: {}\n\n".format(len(oldSauce)))

    for x,y in oldSauce.items():
        logging.debug("ticket: {}\n\tDate Created: {}\n\tDays in retest: {}".format(y["ticket"], y["created"], y["daysUp"]))




    # sys.exit()

    for issue in jira.search_issues('issuetype = Epic AND project = CLIENT AND status in ("Retest Window", Blocked, Ready, "Testing / Drafting", Pre-Test, Delivery, "Sent to Tester For Fixes", "QA", "Final QA Fixes", "QA Approval Review", "QA Missing Dependencies") ORDER BY created DESC'.format(), maxResults=1000):
        logging.debug('\nAssigned: {}\n\tTicket Status: {}\n\tKey: {}\n\tSummary: {}\n\tFields Updated: {}\n\tSite Size: {}'\
        .format(issue.fields.assignee ,issue.fields.status, issue.key, issue.fields.summary, issue.fields.updated, issue.fields.customfield_10056))

        lead  = issue.fields.assignee
        status = issue.fields.status
        ticketNum = issue.fields.summary[0:5]
        desc = re.findall(r'^[\d\_\-\s]+(.+)', str(issue.fields.summary))
        if "CLIENT" not in issue.key:
            desc = "Not a CLIENT Project."
        else:
            logging.debug("desc: {}".format(desc))
            logging.debug("ticketNum: {}".format(ticketNum))
            if not desc:
                desc = re.findall(r'^[\d\_\-\s]+(.+)', str(issue.fields.summary))
            else:
                desc = desc[0]

        time = issue.fields.updated
        time2 = issue.fields.created

        report = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z')
        report2 = datetime.strptime(time2, '%Y-%m-%dT%H:%M:%S.%f%z')

        strCreate = report2.strftime('%m/%d/%Y')
        strUpdated = report.strftime('%m/%d/%Y')

        daysUp = (now - report2).days
        lastUp = (now - report).days

        logging.debug("Created: {}".format(strCreate))
        logging.debug("Last updated: {}".format(strUpdated))
        logging.debug("Right meow: {}".format(rightMeow))
        logging.debug("How long has it been up?: {}".format(daysUp))
        logging.debug("When was it last updated?: {}".format(lastUp))

        pO = ""
        if not issue.fields.customfield_10055:
            pO = "<p style='color:Red;font-weight:bold;'>No PO</p>"
        else:
            pO = issue.fields.customfield_10055
        logging.debug("PO Number: {}".format(pO))

        wU = ""
        size = str(issue.fields.customfield_10056).lower()
        size = size.replace("-", "")
        size = size.replace(" ", "")

        ids = "<p style='color:RoyalBlue;font-weight:bold;'>No IDS notification</p>"
        if str(issue.fields.customfield_10347) == None:
            ids = str(issue.fields.customfield_10347)

        if not issue.fields.customfield_10056:
            wU = "No size found!"
        elif size == "xsmall":
            wU = "1 - 40"
        elif size == "small":
            wU = "2 - 80"
        elif size == "smedium":
            wU = "2.5 - 100"
        elif size == "medium":
            wU = "3 - 120"
        elif size == "marge":
            wU = "3.5 - 140"
        elif size == "large":
            wU = "4 - 160"
        elif size == "xlarge":
            wU = "5 - 200"
        elif size == "xxlarge":
            wU = "6 - 240"
        else:
            wU = "Unknown Size - {}".format(size)

        tester = "Test & Report not created"
        for issuez in jira.search_issues('project = CLIENT AND issuetype = "Test & Report" AND parentEpic = "{}"'.format(str(issue.key)), maxResults=100):
            logging.debug('\nAssigned: {}\n\tTicket Status: {}\n\tParent: {}\n'.format(issuez.fields.assignee ,issuez.fields.status, issuez.fields.parent))
            if issuez.fields.assignee:
                tester = issuez.fields.assignee
                tester = str(tester).title()
            else:
                tester = "Test is unassigned!"

        leetSauce[issue.key] = {
            "assignee": str(lead),
            "tester": tester,
            "status": str(status),
            "ticketNum": str(ticketNum),
            "pO": str(pO),
            "size": size,
            "wU": str(wU),
            "daysUp": str(daysUp),
            "lastUp": str(lastUp),
            "created": str(strCreate),
            "updated": str(strUpdated),
            "summary": str(issue.fields.summary),
            "desc": str(desc),
            "ids": str(ids),
            # "priority": str(issue.fields.priority),
            # "description": str(issue.fields.description),
            "Jira": "https://client.atlassian.net/browse/{}".format(str(issue.key))
        }
        weakSauce.append(issue.key)
        # Dump for all fields
        for z in issue.raw['fields']:
            print("\t{}: {}".format(z, issue.raw['fields'][z]))
        # sys.exit()
        logging.debug("Info: {}".format(leetSauce[issue.key]))

    logging.debug("leetSauce: {}".format(weakSauce))

    logging.debug("Info: {}\n\n\n".format(leetSauce))

    for x,y in leetSauce.items():
        print("Key: {}".format(x))
        for z in y:
            print("\t{}: {}".format(z, y[z]))
        print("\n")



    # sys.exit(0)
    return leetSauce, oldSauce


def rawStats(loc, leetSauce):
    if ".xlsx" not in loc:
        logging.warning("No file with xlsx found")
        loc = XML_locate(loc)

    tic = time.perf_counter()

    logging.debug("Duck tracker started")
    logging.debug("Initial Location: {}".format(loc))

    test = pd.DataFrame(leetSauce).T
    logging.debug("Test:\n{}".format(test))

    logging.debug("Dataframe: {}".format(type(test)))

    writer = pd.ExcelWriter(loc)
    test.to_excel(writer, sheet_name=fileRightMeow, index=False)
    writer.save()

    return


def morningMessage(leetSauce, oldSauce):
    pwd = os.listdir()
    logging.debug("pwd: {}".format(pwd))
    if "morning_{}.txt".format(fileRightMeow) in pwd:
        os.replace("morning_{}.txt".format(fileRightMeow), "messages/morning_{}.txt".format(fileRightMeow + "_old"))
    else:
        logging.info("No old morning message found! Can proceed!")

    with open("morning_{}.txt".format(fileRightMeow), "w") as f:
        f.write("Good morning!!!\n\n")
        f.write("Here is a list of tickets that are currently marked as blocked:\n\n")
        for x,y in leetSauce.items():
            logging.debug("Key: {}".format(x))
            logging.debug("Values: {}".format(y))
            if y["status"] == "Blocked":
                f.write("ticket #: {}\n".format(y["ticketNum"]))
                f.write("\tTester: {}\n".format(y["tester"]))
                f.write("\tDate ticket was injested into Jira: {}\n".format(y["created"]))
                f.write("\tLast updated on Jira: {}\n".format(y["updated"]))
                f.write("\tDays since ticket was injested into system: {}\n".format(y["daysUp"]))
                f.write("\tLast update to Jira: {}\n".format(y["lastUp"]))
                f.write("\tJira Link: {}\n\n\n".format(y["Jira"]))

    pretests = {}
    noPO = {}
    noPOPending = {}
    over100 = {}
    blocked = {}
    mine = {}
    noUpdate = {}

    trackedTesters = ["Alexander Thines"]

    soonRetest = {}
    pastRetest = {}

    # logging.debug("ticket: {}\n\tDate Created: {}\n\tDays in retest: {}".format(y["ticket"], y["created"], y["daysUp"]))
    for x,y in oldSauce.items():
        if (int(y["daysUp"]) >= 100) and (int(y["daysUp"]) <= 119):
            soonRetest[x] = y
        if int(y["daysUp"]) >= 120:
            pastRetest[x] = y

    for x,y in leetSauce.items():
        if y["status"] == "Blocked":
            blocked[x] = y
        if y["status"] == "Pre-Test":
            pretests[x] = y
        if (y["pO"] == "No PO") and (y["status"] != "Delivery"):
            noPO[x] = y
        if (y["pO"] == "No PO") and (y["status"] == "Delivery"):
            logging.debug("[*] Debug: {}".format(y))
            # time.sleep(3)
            noPOPending[x] = y
        if int(y["daysUp"]) >= 100 and y["status"] != "Delivery":
            over100[x] = y
        for z in trackedTesters:
            if y["tester"] == z and y["status"] != "Delivery":
                mine[x] = y
        if int(y["lastUp"]) >= 7 and y["status"] != "Delivery":
            noUpdate[x] = y

    pretestData = ""
    noPOData = ""
    noPOPendingData = ""
    over100Data = ""
    blockedData = ""
    mineData = ""
    noUpdateData = ""

    soonRetestData = ""
    pastRetestData = ""

    retestTableIndex = """
    <table>
    <tr>
    <th>ticket #</th>
    <th>Date test went into Delivery</th>
    <th>How long test has been in delivery</th>
    </tr>
    """

    soonRetestData += retestTableIndex
    for x,y in soonRetest.items():
        soonRetestData += """
        <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticket"], y["created"], y["daysUp"],y["Jira"])
    soonRetestData += "</table>"

    pastRetestData += retestTableIndex
    for x,y in pastRetest.items():
        pastRetestData += """
        <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticket"], y["created"], y["daysUp"],y["Jira"])
    pastRetestData += "</table>"


    tableIndex = """
    <table>
    <tr>
    <th>ticket #</th>
    <th>Tester</th>
    <th>Status</th>
    <th>PO Number</th>
    <th>IDS Notification Date</th>
    <th>Days alive</th>
    <th>Last Update on Jira</th>
    <th>Link</th>
    </tr>
    """

    pretestData += tableIndex
    for x,y in pretests.items():
        pretestData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    pretestData += "</table>"

    noPOData += tableIndex
    for x,y in noPO.items():
        noPOData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    noPOData += "</table>"

    noPOPendingData += tableIndex
    for x,y in noPOPending.items():
        noPOPendingData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    noPOPendingData += "</table>"

    over100Data += tableIndex
    for x,y in over100.items():
        over100Data += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    over100Data += "</table>"

    blockedData += tableIndex
    for x,y in blocked.items():
        blockedData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    blockedData += "</table>"

    mineData += tableIndex
    for x,y in mine.items():
        mineData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    mineData += "</table>"

    noUpdateData += tableIndex
    for x,y in noUpdate.items():
        noUpdateData += """<tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(y["ticketNum"], y["tester"], y["status"], y["pO"], y["ids"], y["daysUp"], y["lastUp"], y["Jira"])
    noUpdateData += "</table>"


    with open("morning_Alex_{}.txt".format(fileRightMeow), "w") as f:
        f.write("What is good, Mr. Raccoon? Here is your 2 second brief:\n\nPre-Tests: {}\nNo PO Numbers and not in Delivery: {}\nNo PO Numbers and in Delivery: {}\nRetest 100 > X > 120: {}\nRetest X >= 120: {}\nOver 100 days old: {}\nBlocked: {}\nMine: {}\nNo Update in 7 days: {}\n\n\n".format(len(pretests), len(noPO), len(noPOPending), len(soonRetest), len(pastRetest), len(over100), len(blocked), len(mine), len(noUpdate)))
        f.write("Longer Briefing:\n\n")

        if len(pretests) == 0:
            f.write("\n\n\nThere are currently tickets in Pre-Tests\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently in Pre-test (Spoiler Alert: There are {}):\n{}".format(len(pretests), pretestData))

        if len(noPO) == 0:
            f.write("\n\n\nThere are currently no tickets without PO Numbers outside of Delivery\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently without PO numbers and not in Delivery (Spoiler Alert: There are {}):\n{}".format(len(noPO), noPOData))

        if len(noPOPending) == 0:
            f.write("\n\n\nThere are currently no tickets without PO Numbers in Delivery\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently without PO numbers and in Delivery (Spoiler Alert: There are {}):\n{}".format(len(noPOPending), noPOPendingData))

        if len(blocked) == 0:
            f.write("\n\n\nThere are currently no tickets blocked\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently blocked (Spoiler Alert: There are {}):\n{}".format(len(blocked), blockedData))

        if len(over100) == 0:
            f.write("\n\n\nThere are currently no tickets over 100 days old\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently over 100 days old (Spoiler Alert: There are {}):\n{}".format(len(over100), over100Data))

        if len(soonRetest) == 0:
            f.write("\n\n\nThere are currently no tickets between 100 days to 120 days in retest window\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently between 100 days to 120 days in retest window (Spoiler Alert: There are {}):\n{}".format(len(soonRetest), soonRetestData))

        if len(pastRetest) == 0:
            f.write("\n\n\nThere are currently no tickets at or over 120 in retest window\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently at or over 120 in retest window (Spoiler Alert: There are {}):\n{}".format(len(pastRetest), pastRetestData))

        if len(mine) == 0:
            f.write("\n\n\nThere are currently no tickets assigned to you\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently assigned to you (Spoiler Alert: There are {}):\n{}".format(len(mine), mineData))

        if len(noUpdate) == 0:
            f.write("\n\n\nThere are currently no tickets that have not been updated in 7 days\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that have not been updated in over a week (Spoiler Alert: There are {}):\n{}".format(len(noUpdate), noUpdateData))

    with open("morning_Alex_{}.html".format(fileRightMeow), "w") as f:
        f.write("What is good, Mr. Raccoon? Here is your 2 second brief:\n\nPre-Tests: {}\nNo PO Numbers and not in Delivery: {}\nNo PO Numbers and in Delivery: {}\nRetest 100 > X > 120: {}\nRetest X >= 120: {}\nOver 100 days old: {}\nBlocked: {}\nMine: {}\nNo Update in 7 days: {}\n\n\n".format(len(pretests), len(noPO), len(noPOPending), len(soonRetest), len(pastRetest), len(over100), len(blocked), len(mine), len(noUpdate)))
        f.write("Longer Briefing:\n\n")

        if len(pretests) == 0:
            f.write("\n\n\nThere are currently tickets in Pre-Tests\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently in Pre-test (Spoiler Alert: There are {}):\n{}".format(len(pretests), pretestData))

        if len(noPO) == 0:
            f.write("\n\n\nThere are currently no tickets without PO Numbers outside of Delivery\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently without PO numbers and not in Delivery (Spoiler Alert: There are {}):\n{}".format(len(noPO), noPOData))

        if len(noPOPending) == 0:
            f.write("\n\n\nThere are currently no tickets without PO Numbers in Delivery\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently without PO numbers and in Delivery (Spoiler Alert: There are {}):\n{}".format(len(noPOPending), noPOPendingData))

        if len(blocked) == 0:
            f.write("\n\n\nThere are currently no tickets blocked\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently blocked (Spoiler Alert: There are {}):\n{}".format(len(blocked), blockedData))

        if len(over100) == 0:
            f.write("\n\n\nThere are currently no tickets over 100 days old\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently over 100 days old (Spoiler Alert: There are {}):\n{}".format(len(over100), over100Data))

        if len(soonRetest) == 0:
            f.write("\n\n\nThere are currently no tickets between 100 days to 120 days in retest window\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently between 100 days to 120 days in retest window (Spoiler Alert: There are {}):\n{}".format(len(soonRetest), soonRetestData))

        if len(pastRetest) == 0:
            f.write("\n\n\nThere are currently no tickets at or over 120 in retest window\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently at or over 120 in retest window (Spoiler Alert: There are {}):\n{}".format(len(pastRetest), pastRetestData))

        if len(mine) == 0:
            f.write("\n\n\nThere are currently no tickets assigned to you\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that are currently assigned to you (Spoiler Alert: There are {}):\n{}".format(len(mine), mineData))

        if len(noUpdate) == 0:
            f.write("\n\n\nThere are currently no tickets that have not been updated in 7 days\n\n")
        else:
            f.write("\n\n\nHere is a list of tickets that have not been updated in over a week (Spoiler Alert: There are {}):\n{}".format(len(noUpdate), noUpdateData))



def main():
    print("Hello from Jarvis!")
    tic = time.perf_counter()
    options = get_arg()

    uz = "" # User
    tokz = "" # API Token 
    jira = JIRA("https:/client.atlassian.net/", basic_auth=(uz, tokz))

    logging.debug("Teams: {}".format(teams))
    for x,y in teams.items():
        logging.debug("Team member: {}".format(x))
        logging.debug("Team member: {}".format(y))


    logging.debug("Connecting to JIRA")
    logging.debug("Connection: {}".format(jira))

    # leetSauce = {"nothing":"at all"}
    leetSauce, oldSauce = jiraPull(jira)

    # Time for the tracker of ducks!
    # rawStats(options.location, leetSauce)

    morningMessage(leetSauce, oldSauce)

    toc = time.perf_counter()

    print(f"Completed program in {toc - tic:0.2f} seconds")


if __name__ == "__main__":
    main()
