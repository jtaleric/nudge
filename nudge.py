import pprint
import logger as log
import jira
import os

server=os.environ['JIRA_Server']
username=os.environ['JIRA_User']
password=os.environ['JIRA_Pass']

queries=os.environ['JIRA_Queries'].split('  ')

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
        nudgeMessage.append("JIRA ({}) Has not been updated in over 3 days (laste updated){}, please {} provide an update - {}".
                            format(nudge['JIRA'],
                                   nudge['UPDATED'],
                                   nudge['OWNER'],
                                   nudge['LINK']))

print("\n".join(nudgeMessage))
