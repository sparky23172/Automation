from burp import IBurpExtender, IScannerCheck, IScanIssue
import re
import random
from array import array
import os
import json

FINDINGS = {}


class BurpExtender(IBurpExtender, IScannerCheck):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("[Skynet]")
        callbacks.registerScannerCheck(self)
        callbacks.issueAlert("[Skynet] Skynet has been launched!")
        print("[Skynet] Skynet extension loaded.")
        self._whoami()

        return


    def _whoami(self):
        print("[Skynet] Grabbing startup info...\n")
        curPath = os.path.expanduser('~')
        lsdir = os.listdir(curPath)
        if 'exploit.db' in lsdir:
            print("Found exploit.db\nPrinting contents...\n")
            with open(curPath + '/exploit.db', 'r') as f:
                lines = f.read()
                # print(lines)
                alerts = json.loads(lines)
                global FINDINGS
                FINDINGS = alerts
                print(alerts,"\n")
                for x,y in alerts.items():
                    print("{}\n{}\n".format(x,y))
        return


    def _get_matches(self, response, match):
        matches = []
        for res in match:
            print(res)
            # Check to see if res is a list
            if isinstance(res, list):
                for r in res:
                    start = 0
                    reslen = len(response)
                    matchlen = len(r)
                    while start < reslen:
                        start = self._helpers.indexOf(response, r, False, start, reslen)
                        if start == -1:
                            break
                        if str(array('i', [start, start + matchlen])) not in str(matches):
                            matches.append(array('i', [start, start + matchlen]))
                        start += matchlen        
                break
            start = 0
            reslen = len(response)
            matchlen = len(res)
            while start < reslen:
                start = self._helpers.indexOf(response, res, False, start, reslen)
                if start == -1:
                    break
                if str(array('i', [start, start + matchlen])) not in str(matches):
                    matches.append(array('i', [start, start + matchlen]))
                start += matchlen
        print(matches)
        return matches

    def getResponseHeadersAndBody(self, content):
        response = content.getResponse()
        response_data = self._helpers.analyzeResponse(response)
        headers = list(response_data.getHeaders())
        body = response[response_data.getBodyOffset():].tostring()
        return headers, body

    def doPassiveScan(self, baseRequestResponse):
        issues = []
        headers, body = self.getResponseHeadersAndBody(baseRequestResponse)
        headers = str(headers)
        issueName = "[WOPR] Failed to get alerts"
        severity = "Information" 
        confidence = "Certain" 
        issueBackground = "Unable to get alerts from exploit.db"
        issueDetail = "Unable to get alerts from exploit.db"
        print("Starting passive scan...")

        for title,finding in FINDINGS.items():
            print("Finding: " + title)
            method = finding["passiveMethod"]["method"]
            print("Search Method: {}".format(method))
            if method == "regex":
                pattern = finding["passiveMethod"]["pattern"]
                caseSensitive = finding["passiveMethod"]["caseSensitive"]
                print("Header: {}".format(headers))
                if caseSensitive == "True":
                    match = re.findall(pattern, headers)
                    match2 = re.findall(pattern, body)
                    match.append(match2)
                else:
                    match = re.findall(pattern, headers, flags=re.IGNORECASE)
                    match2 = re.findall(pattern, body, flags=re.IGNORECASE)
                    match.append(match2)
                print(str(match))
                if match:
                    print("Found match for: {}".format(match))
                    self._callbacks.issueAlert("Found a match off of {} for {}. Check Issue Activity!".format(title, pattern))
                    matches = self._get_matches(baseRequestResponse.getResponse(), match)
                    issueName = finding["issueName"]
                    severity = finding["severity"]
                    confidence = finding["confidence"]
                    issueBackground = finding["issueBackground"]
                    issueDetail = finding["issueDetail"]
                    # report the issue
                    issues.append( UUIDScanIssue(
                        baseRequestResponse.getHttpService(),
                        self._helpers.analyzeRequest(baseRequestResponse).getUrl(),
                        [self._callbacks.applyMarkers(baseRequestResponse, None, matches)],
                        issueName, 
                        severity, 
                        confidence, 
                        issueBackground, 
                        issueDetail
                    ))

        if not issues:
            issues = None 
        return issues
    
    def doActiveScan(self, baseRequestResponse, insertionPoint):
        pass

    def consolidateDuplicateIssues(self, existingIssue, newIssue):
        if existingIssue.getIssueName() == newIssue.getIssueName():
            return -1
        return 0


class UUIDScanIssue(IScanIssue):
    def __init__(self, httpService, url, httpMessages, issueName, severity, confidence, issueBackground, issueDetail):
        self._httpService = httpService
        self._url = url
        self._httpMessages = httpMessages
        self._issueName = issueName
        self._severity = severity
        self._confidence = confidence
        self._issueBackground = issueBackground
        self._issueDetail = issueDetail

    def getUrl(self):
        return self._url

    def getIssueName(self):
        return self._issueName

    def getIssueType(self):
        return 134217728

    def getSeverity(self):
        return self._severity

    def getConfidence(self):
        return self._confidence

    def getIssueBackground(self):
        return self._issueBackground

    def getIssueDetail(self):
        return self._issueDetail

    def getRemediationBackground(self):
        pass

    def getRemediationDetail(self):
        pass

    def getHttpMessages(self):
         return self._httpMessages

    def getHttpService(self):
        return self._httpService

