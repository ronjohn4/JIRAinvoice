import requests
import json
from timeit import default_timer as timer
import logging
from mockdata import GetMockData

# todo - add user authentication (against JIRA)
# todo - link to Jira using an icon next to the Jira ID

# Set to True to run offline.
_offline = True
tempo_list = {}

s = requests.session()
s.auth = ('rjohnson', 'Miter9le')



def LoadJira():
    global tempo_list

    if _offline:  # if _offline then the mock data has already been set
        return

    # SUBKEY==================
    keylist = ",".join(v['subkey'] for k, v in tempo_list.items() if v['subkey'] is not None)
    if len(keylist) > 0:
        jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
                   'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
                   'issuetype,parent,status,customfield_1000,fixVersions8&maxResults=500'
        url = jira_url.format(keylist)
        # print('url:', url)

        r = s.get(url)
        json_return = json.loads(r.text)
        json_return = json_return['issues']

        for v in json_return:
            for k, v2 in tempo_list.items():
                if v2['subkey'] == v['key']:
                    v2['subsummary'] = v['fields']['summary']
                    v2['substatus'] = v['fields']['status']['name']
                    if 'parent' in v['fields']:
                        v2['storykey'] = v['fields']['parent']['key']
                    if 'fixVersions' in v['fields']:
                        v2['subfixversion'] = ",".join(v2['name'] for v2 in v['fields']['fixVersions'])


    # STORYKEY==================
    keylist = ",".join(v['storykey'] for k, v in tempo_list.items() if v['storykey'] is not None)
    if len(keylist) > 0:
        jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
               'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
               'issuetype,parent,status,customfield_10008,fixVersions&maxResults=500'
        url = jira_url.format(keylist)
        # print('url:', url)

        r = s.get(url)
        json_return = json.loads(r.text)
        json_return = json_return['issues']

        for v in json_return:
            for k, v2 in tempo_list.items():
                if v2['storykey'] == v['key']:
                    v2['storysummary'] = v['fields']['summary']
                    v2['storystatus'] = v['fields']['status']['name']
                    if 'customfield_10008' in v['fields']:
                        v2['epickey'] = v['fields']['customfield_10008']
                    if 'fixVersions' in v['fields']:
                        v2['storyfixversion'] = ",".join(v2['name'] for v2 in v['fields']['fixVersions'])


    # EPICKEY==================
    keylist = ",".join(v['epickey'] for k, v in tempo_list.items() if v['epickey'] is not None)
    if len(keylist) > 0:
        jira_url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?' + \
                   'jql=key%20in%20({0})&expand=names&fields=key,summary,' \
                   'issuetype,parent,status,customfield_10008,fixVersions&maxResults=500'
        url = jira_url.format(keylist)
        # print('url:', url)

        r = s.get(url)
        json_return = json.loads(r.text)
        json_return = json_return['issues']

        for v in json_return:
            for k, v2 in tempo_list.items():
                if v2['epickey'] == v['key']:
                    v2['epicsummary'] = v['fields']['summary']
                    v2['epicstatus'] = v['fields']['status']['name']
                    if 'fixVersions' in v['fields']:
                        v2['epicfixversion'] = ",".join(v2['name'] for v2 in v['fields']['fixVersions'])

    return


def LoadTempo(projectKey, fromDate, toDate):
    global tempo_list

    if  _offline:
        tempo_list = GetMockData()
    else:
        tempo_list = {}
        # --Tempo url doesn't allow for limiting the fields returned
        tempo_url = 'https://levelsbeyond.atlassian.net/rest/tempo-timesheets/3/worklogs?' + \
                    'dateFrom={0}&dateTo={1}&projectKey={2}'
        url = tempo_url.format(fromDate, toDate, projectKey)
        logging.debug('tempo_url: {0}'.format(url))

        r = s.get(url)

        logging.debug('return status: {0}'.format(r.status_code))

        if r.status_code == 200:
            json_return = json.loads(r.text)
            logging.debug('length:{0}'.format(len(json_return)))
            if len(json_return) > 0:
                logging.debug('first row: {0}'.format(json_return[1]))

            for entry in json_return:
                tempo_list[entry['id']] = {'id': entry['id'],
                                            'tempocomment': entry['comment'],
                                            'tempotime': entry['timeSpentSeconds'],
                                            'parentissuetype': entry['issue']['issueType']['name'],
                                            'subkey': None,
                                            'subsummary': None,
                                            'subtime': 0,
                                            'substatus': None,
                                            'subfixversion': None,
                                            'storykey': None,
                                            'storysummary': None,
                                            'storytime': 0,
                                            'storystatus': None,
                                            'storyfixversion': None,
                                            'epickey': None,
                                            'epicsummary': None,
                                            'epictime': 0,
                                            'epicstatus': None,
                                            'epicfixversion': None}

                if entry['issue']['issueType']['name'] == 'Time Tracking Task' or \
                                entry['issue']['issueType']['name'] == 'Bug' or \
                                entry['issue']['issueType']['name'] == 'Story':
                    tempo_list[entry['id']]['storykey'] = entry['issue']['key']

                elif entry['issue']['issueType']['name'] == 'Work Task' or \
                                entry['issue']['issueType']['name'] == 'Story Bug':
                    tempo_list[entry['id']]['subkey'] = entry['issue']['key']

    return



# Aggregates Tempo and JIRA data for presentation
def HrsGet(projectKey, fromDate, toDate):
    global tempo_list

    logging.basicConfig(level=logging.DEBUG)
    time_start = timer()

    LoadTempo(projectKey, fromDate, toDate)

    time_current = timer()
    logging.debug('Tempo done - start:{0}, current:{1}, duration:{2}'.format(time_start, time_current,
                                                                             time_current - time_start))

    LoadJira()

    time_current = timer()
    logging.debug('Jira done - start:{0}, current:{1}, duration:{2}'.format(time_start, time_current,
                                                                             time_current - time_start))

    total_hours = 0
    for k, entry in tempo_list.items():
        entry['epictime'] = sum([v['tempotime'] for _, v in tempo_list.items() if v['epickey'] == entry['epickey']])
        entry['subtime'] = sum([v['tempotime'] for _ , v in tempo_list.items() if v['subkey'] == entry['subkey']])
        entry['storytime'] = sum([v['tempotime'] for _ , v in tempo_list.items() if v['storykey'] == entry['storykey']])
        total_hours += entry['tempotime']

    time_current = timer()
    logging.debug('Final - start:{0}, current:{1}, duration:{2}'.format(time_start, time_current,
                                                                        time_current - time_start))

    # output mock data from real data to be copied into code. Uncomment line below,
    # run a search, copy results and paste into the routine SetMockData().
    # print('tempo_list Mock Data')
    # for k, v in tempo_list.items():
    #     print('tempo_list[{0}] =  {1}'.format(k,v))

    return_list = []
    for k,v in tempo_list.items():
        return_list.append(v)

    return [return_list, total_hours]
