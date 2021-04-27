# nudge - JIRA tool to help get nudge people

## JIRA Setup
```
export JIRA_Server="http://my-JIRA-Server"
export JIRA_User="MyUserName"
export JIRA_Pass="MyJIRAPass"

export JIRA_Queries=""
```

`JIRA_Queries` can be one more many queries to execute. For example:

`project in (PERFSCALE) AND updated <= -3d AND sprint in closedSprints() AND sprint in openSprints() AND status not in (Closed, Done) AND labels in (managed-services, perfscale-managed-services)`

The important part of the query is the `updated <= -3d`, this will return cards that have not been updated the last 3 days.

## Email Reminder setup
```
export EMAIL_Server=""
export EMAIL_From="" # Who the email bot should pretend to be
export EMAIL_To="" # What list / set of people the bot should send to.
```

This should be pretty simple to understand.
