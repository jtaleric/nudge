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
from textwrap3 import wrap
import jira
import os
import argparse
import operator

parser= argparse.ArgumentParser(description="Tool to query and help nudge JIRA users")
parser.add_argument(
    "--report",
    default=False,
    type=bool,
    dest="report")
args = parser.parse_args()

# Team Name
teamName="Team"

# JIRA Connection Setup
server=os.environ['JIRA_Server']
username=os.environ['JIRA_User']
password=os.environ['JIRA_Pass']

# Queries, Tab delimited
queries=os.environ['JIRA_Queries'].split('  ')

# EMAIL Nudges
sendEmail=False

if sendEmail :
    smtpServer=os.environ['EMAIL_Server']
    smtpFrom=os.environ['EMAIL_From']
    smtpTo=os.environ['EMAIL_To']

options = { 'server': server }
conn = jira.JIRA(options, basic_auth=(username, password))

issues=[]
nudges=[]
nudgeMessage=[]

if len(queries) < 1:
    log.logger.error("No JIRA queries provided.")
    exit(1)

for query in queries:
    if query == "":
        continue
    log.logger.info("Running query: %s" % (query))
    issues.append(conn.search_issues(jql_str=query,json_result=True,maxResults=200))

if len(issues) > 0 :
    for issue in issues:
        for jira in issue['issues'] :
            if jira['fields']['assignee'] is None:
                owner = "No Owner"
            else :
                owner = jira['fields']['assignee']['displayName']
            nudges.append({
                "JIRA" : "{}".format(jira['key']),
                "OWNER" : "{}".format(owner),
                "CREATOR" : "{}".format(jira['fields']['creator']['displayName']),
                "STATUS" : "{}".format(jira['fields']['status']['name']),
                "LINK" : "{}/browse/{}".format(server,jira['key']),
                "UPDATED" : "{}".format(jira['fields']['updated']),
                "DESC" : "{}".format(jira['fields']['description']),
                "LABELS" : "{}".format(jira['fields']['labels']),
                "SUMM" : "{}".format(jira['fields']['summary']),
                "ID" : "{}".format(jira['id']),
                "COMMENTS" : conn.comments(jira['key'])
            })

nudges.sort(key=operator.itemgetter('OWNER'))

if not args.report :
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
    	    msg = "Subject: {} JIRA Nudge\n\n".format(teamName)
    	    msg += "Hello PerfScale Team,\nBelow are the current nudges, please address them today.\n\n"
    	    msg += "{}".format("\n".join(nudgeMessage))
    	    server.sendmail(smtpFrom, smtpTo, msg)
    	    server.quit()
    	    log.logger.info("Email Sent")
        else :
            for nudge in nudges:
                print("{} Needs to be updated by {}. Last update was {}. Link {}".
                    format(nudge['JIRA'],
                            nudge['OWNER'],
                            nudge['UPDATED'],
                            nudge['LINK']))
else:
    nudges.sort(key=operator.itemgetter('OWNER'))
    for nudge in nudges:
        if len(nudge['COMMENTS']) > 0 :
            latestCommentID = nudge['COMMENTS'].pop()
            latestComment = conn.comment(nudge['ID'],latestCommentID).body
        else:
            latestComment = "No comments"

        print("+{}+".format("="*100))
        print("{} - {} \nLabels: {}\nOwner: {}\nCreator: {}\nStatus: {}\nLink: {}\nLast Comment:\n{}\n\n".
              format(nudge['JIRA'],
                     nudge['SUMM'],
                     nudge['LABELS'],
                     nudge['OWNER'],
                     nudge['CREATOR'],
                     nudge['STATUS'],
                     nudge['LINK'],
                     "\n".join(wrap(latestComment,100))
             ))
        print("+{}+".format("="*100))
