import requests
import json
from timeit import default_timer as timer
import logging

# Set to True to run offline.  There are a set of print statements below that output the mock data
# when online.  The results can be copied and pasted into the lines that hardcode the mock data.
_offline = False
tempo_list = {}

def LoadJira():
    if not  _offline:  # if _offline then the mock data has already been set

        # SUBKEY==================
        keylist = ",".join(v['subkey'] for k, v in tempo_list.items() if v['subkey'] is not None)
        if len(keylist) > 0:
            jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
                       'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
                       'issuetype,parent,status,customfield_10008&maxResults=500'
            url = jira_url.format(keylist)
            # print('url:', url)

            r = requests.get(url, auth=GetAuth())
            json_return = json.loads(r.text)
            json_return = json_return['issues']

            for v in json_return:
                for k, v2 in tempo_list.items():
                    if v2['subkey'] == v['key']:
                        v2['subsummary'] = v['fields']['summary']
                        v2['substatus'] = v['fields']['status']['name']
                        if 'parent' in v['fields']:
                            v2['storykey'] = v['fields']['parent']['key']

        # STORYKEY==================
        keylist = ",".join(v['storykey'] for k, v in tempo_list.items() if v['storykey'] is not None)
        if len(keylist) > 0:
            jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
                   'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
                   'issuetype,parent,status,customfield_10008&maxResults=500'
            url = jira_url.format(keylist)
            # print('url:', url)

            r = requests.get(url, auth=GetAuth())
            json_return = json.loads(r.text)
            json_return = json_return['issues']

            for v in json_return:
                for k, v2 in tempo_list.items():
                    if v2['storykey'] == v['key']:
                        v2['storysummary'] = v['fields']['summary']
                        v2['storystatus'] = v['fields']['status']['name']
                        if v['fields']['customfield_10008']:
                            v2['epickey'] = v['fields']['customfield_10008']

        # EPICKEY==================
        keylist = ",".join(v['epickey'] for k, v in tempo_list.items() if v['epickey'] is not None)
        if len(keylist) > 0:
            jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
                       'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
                       'issuetype,parent,status,customfield_10008&maxResults=500'
            url = jira_url.format(keylist)
            # print('url:', url)

            r = requests.get(url, auth=GetAuth())
            json_return = json.loads(r.text)
            json_return = json_return['issues']

            for v in json_return:
                for k, v2 in tempo_list.items():
                    if v2['epickey'] == v['key']:
                        v2['epicsummary'] = v['fields']['summary']
                        v2['epicstatus'] = v['fields']['status']['name']

    return


# Aggregates Tempo and JIRA data for presentation
def HrsGet(projectKey, fromDate, toDate):
    global tempo_list

    logging.basicConfig(level=logging.DEBUG)
    time_start = timer()

    if  _offline:
        SetMockData()
    else:
        tempo_list = {}
        # --Tempo url doesn't allow for limiting the fields returned
        tempo_url = 'https://levelsbeyond.atlassian.net/rest/tempo-timesheets/3/worklogs?' + \
                    'dateFrom={0}&dateTo={1}&projectKey={2}'
        url = tempo_url.format(fromDate, toDate, projectKey)
        logging.debug('tempo_url: {0}'.format(url))

        r = requests.get(url, auth=GetAuth())
        logging.debug('return status: {0}'.format(r.status_code))

        if r.status_code == 200:
            json_return = json.loads(r.text)
            logging.debug('length:{0}'.format(len(json_return)))
            if len(json_return) > 0:
                logging.debug('first row: {0}'.format(json_return[1]))

            # create clean Tempo list
            for entry in json_return:
                # todo - load the key info into the correct parent

                tempo_list[entry['id']] = {'id': entry['id'],
                                           'tempocomment': entry['comment'],
                                           'tempotime': entry['timeSpentSeconds'],
                                           'parentissuetype': entry['issue']['issueType']['name'],
                                           'subkey': None,
                                           'subsummary': None,
                                           'subtime': 0,
                                           'substatus': None,
                                           'storykey': None,
                                           'storysummary': None,
                                           'storytime': 0,
                                           'storystatus': None,
                                           'epickey': None,
                                           'epicsummary': None,
                                           'epictime': 0,
                                           'epicstatus': None}

                if entry['issue']['issueType']['name'] == 'Time Tracking Task' or \
                                entry['issue']['issueType']['name'] == 'Bug' or \
                                entry['issue']['issueType']['name'] == 'Story':
                    tempo_list[entry['id']]['storykey'] = entry['issue']['key']

                elif entry['issue']['issueType']['name'] == 'Work Task' or \
                                entry['issue']['issueType']['name'] == 'Story Bug':
                    tempo_list[entry['id']]['subkey'] = entry['issue']['key']


    time_current = timer()
    logging.debug('Tempo done - start:{0}, current:{1}, duration:{2}'.format(time_start, time_current,
                                                                             time_current - time_start))
    LoadJira()

    total_hours = 0
    for k, entry in tempo_list.items():
        print('entry')
        print(entry)
    #     entry[k]['subtime'] = sum([v['tempotime'] for k2, v in tempo_list.items() if v['subkey'] == entry['subkey']])
    #     entry[k]['storytime'] = sum([v['tempotime'] for k2, v in tempo_list.items() if v['storytime'] == entry['storytime']])
        print('epickey', entry['epickey'])
        entry['epictime'] = sum([v['tempotime'] for _ , v in tempo_list.items() if v['epickey'] == entry['epickey']])
        total_hours += entry['tempotime']

    time_current = timer()
    logging.debug(
        'Final - start:{0}, current:{1}, duration:{2}'.format(time_start, time_current, time_current - time_start))


    # output mock data from real data to be copied into code. Uncomment line below,
    # run a search, copy results and paste where mock data is set after the _debug test.
    # print('tempo_list')
    # print(tempo_list)

    # Debug print loops
    # print('tempo_list')
    # for k, v in tempo_list.items():
    #     print(k,v)

    return_list = []
    for k,v in tempo_list.items():
        return_list.append(v)

    return [return_list, total_hours]


def GetAuth():
    return ('rjohnson', 'Miter9le')


def SetMockData():
    global tempo_list

    tempo_list = {}
    tempo_list[120463] =  {'id': 120463, 'tempocomment': "Spent time working on the automation environment while .71 was down this AM with issues.  For some reason the dashboard suite keeps failing and I think its because of the version of node that is running on it.  The same goes for the system suite.  When I run locally on v6.9.5, all the tests pass which mean the dashboard suite is fixed.  I've also witnessed Veena running the System automation suite locally with no failures but the second either one of the tests get on the mac executor, it fails.  I ran one last time after updating the node version in Jenkins (which I think is what I did) but it failed so when I have time later this afternoon I'm going to have to look into the console logs to see what is going on.", 'tempotime': 4500, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-80', 'storysummary': 'Dev Environment Maint', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120698] =  {'id': 120698, 'tempocomment': 'Working with Robert to get Staging to start using his Vantage development server, which is running the latest update pack.', 'tempotime': 1800, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-79', 'storysummary': 'Client Support', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120699] =  {'id': 120699, 'tempocomment': "Several formal & informal discussions w/ team - discussed upcoming planning items, sync'd up with Rich, spoke with Ron about closing the sprint, and other assorted topics.", 'tempotime': 5400, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-78', 'storysummary': 'Planning Meeting', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120701] =  {'id': 120701, 'tempocomment': "I'm now able to save metadata, after battling our <custom-metadata> directive (which was intended for the Distribution Grid, not for other parts of the HTML app, and which doesn't have the most robust/general API). Still need to write unit tests.", 'tempotime': 13500, 'parentissuetype': 'Work Task', 'subkey': 'ABC-8223', 'subsummary': 'Wire up metadata section', 'subtime': 0, 'substatus': 'Testing Complete', 'storykey': 'ABC-8218', 'storysummary': 'Series Seasons/Volumes Properties (Flex to HTML) - Edit View', 'storytime': 0, 'storystatus': 'Testing Complete', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120901] =  {'id': 120901, 'tempocomment': "Stand up and Robert's call", 'tempotime': 3600, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-78', 'storysummary': 'Planning Meeting', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120942] =  {'id': 120942, 'tempocomment': 'ABC standup', 'tempotime': 2700, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-77', 'storysummary': 'Project Management', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120950] =  {'id': 120950, 'tempocomment': 'ABC review hours then July invoice', 'tempotime': 10800, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-77', 'storysummary': 'Project Management', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120951] =  {'id': 120951, 'tempocomment': 'ABC - review sprint status and cycle sprints', 'tempotime': 7200, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-77', 'storysummary': 'Project Management', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120952] =  {'id': 120952, 'tempocomment': 'ABC - add PDI epic and stories, track questions for Robert', 'tempotime': 7200, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-77', 'storysummary': 'Project Management', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120408] =  {'id': 120408, 'tempocomment': 'Standup and call with Robert', 'tempotime': 3600, 'parentissuetype': 'Time Tracking Task', 'subkey': None, 'subsummary': None, 'subtime': 0, 'substatus': None, 'storykey': 'ABC-78', 'storysummary': 'Planning Meeting', 'storytime': 0, 'storystatus': 'Ready for Development', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120409] =  {'id': 120409, 'tempocomment': 'Testing with Veena\n', 'tempotime': 900, 'parentissuetype': 'Story Bug', 'subkey': 'ABC-8310', 'subsummary': 'Users without permissions can edit Networks ', 'subtime': 0, 'substatus': 'Testing Complete', 'storykey': 'ABC-8195', 'storysummary': 'Networks Properties (Flex to HTML) - Search View', 'storytime': 0, 'storystatus': 'Testing Complete', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120887] =  {'id': 120887, 'tempocomment': 'Verified that everything looks accurate', 'tempotime': 2700, 'parentissuetype': 'Work Task', 'subkey': 'ABC-8192', 'subsummary': 'UI Styling', 'subtime': 0, 'substatus': 'Testing Complete', 'storykey': 'ABC-7726', 'storysummary': 'Add custom metadata screen per selected season/volume in subscriptions', 'storytime': 0, 'storystatus': 'Testing Complete', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
    tempo_list[120888] =  {'id': 120888, 'tempocomment': 'Tested to ensure that all the metadata fields populate correctly', 'tempotime': 3600, 'parentissuetype': 'Story Bug', 'subkey': 'ABC-8296', 'subsummary': 'Some metadata items do not have text fields ', 'subtime': 0, 'substatus': 'Testing Complete', 'storykey': 'ABC-7726', 'storysummary': 'Add custom metadata screen per selected season/volume in subscriptions', 'storytime': 0, 'storystatus': 'Testing Complete', 'epickey': None, 'epicsummary': None, 'epictime': 0, 'epicstatus': None}
