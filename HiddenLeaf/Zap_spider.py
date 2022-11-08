#!/usr/bin/env python
import time
import logging
from zapv2 import ZAPv2

logging.basicConfig(level=logging.DEBUG)
ip = "login.com"
# The URL of the application to be tested
target = 'https://{}'.format(ip)
# Change to match the API key set in ZAP, or use None if the API key is disabled
apiKey = 'supdudes'
sessionName = "1SpookyCats"
contextName = "spooky_little_cats"
# Scope?
contextIncludeURL = []
contextExcludeURL = ['https://{}/socket.io/'.format(ip)]
urls = []

# By default ZAP API client will connect to port 8080
zap = ZAPv2(apikey=apiKey)


core = zap.core
logging.debug('Create ZAP session: ' + sessionName + ' -> ' + core.new_session(name=sessionName, overwrite=True))

context = zap.context
logging.debug('Create ZAP context: ' + contextName + ' -> ' + context.new_context(contextname=contextName))

for url in contextIncludeURL:
        logging.debug(url + ' -> ' +
                context.include_in_context(contextname=contextName,
                                           regex=url))

for url in contextExcludeURL:
        logging.debug(url + ' -> ' +
                context.exclude_from_context(contextname=contextName,
                                           regex=url))

# Use the line below if ZAP is not listening on port 8080, for example, if listening on port 8090
# zap = ZAPv2(apikey=apiKey, proxies={'http': 'http://127.0.0.1:8090', 'https': 'http://127.0.0.1:8090'})
print('Ajax Spider target {}'.format(target))
scanID = zap.ajaxSpider.scan(url=target)
# scanID = zap.ajaxSpider.scan(target)
logging.debug("Ajax Spider scan ID: " + scanID)

timeout = time.time() + 60*5   # 2 minutes from now
# Loop until the ajax spider has finished or the timeout has exceeded
when = 0
while zap.ajaxSpider.status == 'running':
    if time.time() > timeout:
        print("Timeout Occurred")
        break
    print('Ajax Spider status: {}\t\t{} seconds have passed'.format(zap.ajaxSpider.status, when))
    when += 10
    time.sleep(10)

print('Ajax Spider completed')
fill = zap.ajaxSpider.full_results
ajaxResults = zap.ajaxSpider.results(start=0, count=10)


# print(ajaxResults)
# print(fill)
# print("Variable type for {}: {}".format("fill",str(type(fill))))
# logging.debug('Spider Scan ID: ' + str(fill))

logging.debug('Spider Scan ID: ' + str(fill))

count = len(fill['inScope'])
logging.debug("Count: {}".format(len(fill['inScope'])))

i = 0
while i != count:
    # logging.debug("{}".format(fill['inScope'][i]['url']))
    if fill['inScope'][i]['url'] not in urls:
        logging.debug("New URL found: {}".format(fill['inScope'][i]['url']))
    urls.append(fill['inScope'][i]['url'])
    i += 1

urls = list(set(urls))
logging.debug("URLs: {}".format(urls))

# If required perform additional operations with the Ajax Spider results

# TODO: Start scanning the application to find vulnerabilities
