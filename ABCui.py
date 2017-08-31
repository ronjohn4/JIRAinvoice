#!/usr/bin/python
# -*- coding: UTF-8 -*-# enable debugging

# todo - add user authentication (against JIRA)
# todo - run from Apache (wsgi?)
# todo - link to Jira using an icon next to the Jira ID

from flask import Flask, render_template, flash, request, make_response
from ABCdata import HrsGet
import io
import csv
import logging
from datetime import datetime
import calendar

app = Flask('JIRAhrs')


logging.basicConfig(level=logging.DEBUG)

today = datetime.today()
last_search = {
    'startdate': '{0}-{1}-{2}'.format(today.year, today.month, '1'),
    'enddate': '{0}-{1}-{2}'.format(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
}
time_list = []
total_hours = 0

# secret_key is used for flash messages
app.config.update(dict(
    SECRET_KEY='development key'
))


@app.route('/issues/csv/', methods=['GET'])
def issuescsv():
    csv_list = []

    # same filter used on issues page to build the landing page
    epic_list = list({v['epickey']: v for v in time_list if v['epickey']
                      is not None}.values())
    story_list = list({v['storykey']: v for v in time_list if v['storykey']
                       is not None and v['epickey'] is None}.values())

    for v in epic_list:
        csv_list.append({'key': v['epickey'], 'status': v['epicstatus'], 'Hours': v['epictime'],
                         'Version': v['epicfixversion'], 'Summary': v['epicsummary'], 'issuetype': 'Epic'})

    for v in story_list:
        csv_list.append({'key': v['storykey'], 'status': v['storystatus'], 'Hours': v['storytime'],
                         'Version': v['storyfixversion'], 'Summary': v['storysummary'], 'issuetype': 'Story'})

    keys = csv_list[0].keys()
    output = io.StringIO()
    dict_writer = csv.DictWriter(output, keys)
    dict_writer.writeheader()
    dict_writer.writerows(csv_list)

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename={0}'. \
        format('WFDtime{0}.csv'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')))
    response.mimetype = 'text/csv'

    return response


@app.route('/')
@app.route('/issues/', methods=['GET', 'POST'])
def issues():
    global time_list
    global last_search
    global total_hours

    if request.method == 'POST':
        search = {'startdate': request.form["startdate"],
                  'enddate': request.form["enddate"]}
        logging.debug('search:' + str(search))

        last_search = search
        time_list, total_hours = HrsGet('ABC', search['startdate'], search['enddate'])

    # make unique on epickey
    epic_list = list({v['epickey']: v for v in time_list if v['epickey']
                      is not None}.values())
    story_list = list({v['storykey']: v for v in time_list if v['storykey']
                       is not None and v['epickey'] is None}.values())

    # sort for presentation
    epic_list = sorted(epic_list, key=lambda k: (k['epickey'] is None, k['epickey']))
    story_list = sorted(story_list, key=lambda k: (k['storykey'] is None, k['storykey']))

    return render_template('issues.html', epics=epic_list, stories=story_list,
                           search=last_search, total_hours=total_hours)


@app.route('/story/<id>')
def story(id=None):
    if id == 'None':
        id = None
    return render_template('story.html', time_list=[v for v in time_list if v['storykey'] == id])


@app.route('/epic/<id>')
def epic(id=None):
    if id == 'None':
        id = None
    return render_template('epic.html', time_list=[v for v in time_list if v['epickey'] == id])


if __name__ == '__main__':
    app.run(debug=True, port=5002)
