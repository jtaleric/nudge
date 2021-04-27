"""
Copyright 2021 Joe Talerico

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import smtplib
import logger as log
import jira
import os

# JIRA Connection Setup
server=os.environ['JIRA_Server']
username=os.environ['JIRA_User']
password=os.environ['JIRA_Pass']

# Queries, Tab delimited
queries=os.environ['JIRA_Queries'].split('  ')

# EMAIL Nudges
smtpServer=os.environ['EMAIL_Server']
smtpFrom=os.environ['EMAIL_From']
smtpTo=os.environ['EMAIL_To']

options = { 'server': server }
conn = jira.JIRA(options, basic_auth=(username, password))

issues=[]
nudges=[]
nudgeMessage=[]

sendEmail=False

if len(queries) < 1:
    log.logger.error("No JIRA queries provided.")
    exit(1)

for query in queries:
    if query == "":
        continue
    log.logger.info("Running query: %s" % (query))
    issues.append(conn.search_issues(jql_str=query,json_result=True))

if len(issues) > 0 :
    for issue in issues:
        for jira in issue['issues'] :
            nudges.append({
                "JIRA" : "{}".format(jira['key']),
                "OWNER" : "{}".format(jira['fields']['assignee']['displayName']),
                "LINK" : "{}/browse/{}".format(server,jira['key']),
                "UPDATED" : "{}".format(jira['fields']['updated'])
            })

log.logger.info("Number of nudges: {}".format(len(nudges)))

if len(nudges) > 0 :
    for nudge in nudges:
        nudgeMessage.append("{}\nHas not been updated since {}. Please {} provide an update {}\n".
                format(nudge['JIRA'],
                    nudge['UPDATED'].split('T')[0],
                    nudge['OWNER'],
                    nudge['LINK']))

    if sendEmail :
    	server = smtplib.SMTP(smtpServer)
    	msg = "Subject: OCP PerfScale JIRA Nudge\n\n"
    	msg += "Hello PerfScale Team,\nBelow are the current nudges, please address them today.\n\n"
    	msg += "{}".format("\n".join(nudgeMessage))
    	server.sendmail(smtpFrom, smtpTo, msg)
    	server.quit()
    	log.logger.info("Email Sent")
