#!/usr/bin/python
# -*- coding: UTF-8 -*-# enable debugging

# todo - link to Jira using an icon next to the Jira ID

from flask import Flask, render_template, request, make_response, redirect, url_for, session
import io
from functools import wraps
import csv
import logging
from datetime import datetime
import calendar
from JIRAhandler import JIRAhandlerinvoice


JIRA_BASE_URL = 'https://levelsbeyond.atlassian.net'

app = Flask('JIRAinvoice')
jira_handle = JIRAhandlerinvoice.JIRAhandlerinvoice(JIRA_BASE_URL)

# secret_key is used for flash messages
app.config.update(dict(
    SECRET_KEY='development key goes here, should be complex',
    JIRAroot=JIRA_BASE_URL
))


logging.basicConfig(level=logging.DEBUG)

today = datetime.today()
last_month = today.month-1 if today.month > 1 else 12
last_year = today.year-1 if last_month == 12 else today.year

last_search = {
    'startdate': '{0}-{1:0>2}-{2:0>2}'.format(last_year, last_month, '1'),
    'enddate': '{0}-{1:0>2}-{2:0>2}'.format(last_year, last_month, calendar.monthrange(last_year, last_month)[1])
}


time_list = []
total_hours = 0


# decorator used to secure Flask routes
def authenticated_resource(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if jira_handle.isAuth():
            return f(*args, **kwargs)
        else:
            session["wants_url"] = request.url
            return redirect(url_for('login'))
    return decorated


@app.route('/issues/csv/', methods=['GET'])
@authenticated_resource
def issuescsv():
    csv_list = []

    # same filter used on issues page to build the landing page
    epic_list = list({v['epickey']: v for v in time_list if v['epickey']
                      is not None}.values())
    story_list = list({v['storykey']: v for v in time_list if v['storykey']
                       is not None and v['epickey'] is None}.values())

    for v in epic_list:
        csv_list.append({'key': v['epickey'], 'status': v['epicstatus'],
                         'Hours': '{0:.2f}'.format(v['epictime']/3600),
                         'Version': v['epicfixversion'], 'Summary': v['epicsummary'], 'issuetype': 'Epic'})

    for v in story_list:
        csv_list.append({'key': v['storykey'], 'status': v['storystatus'],
                         'Hours': '{0:.2f}'.format(v['storytime']/3600),
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
@authenticated_resource
def issues():
    global time_list
    global last_search
    global total_hours

    if request.method == 'POST':
        search = {'startdate': request.form["startdate"],
                  'enddate': request.form["enddate"]}
        logging.debug('search:' + str(search))

        last_search = search
        time_list, total_hours = jira_handle.HrsGet('ABC', search['startdate'], search['enddate'])

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
@authenticated_resource
def story(id=None):
    if id == 'None':
        id = None
    return render_template('story.html', time_list=[v for v in time_list if v['storykey'] == id])


@app.route('/epic/<id>')
@authenticated_resource
def epic(id=None):
    if id == 'None':
        id = None
    return render_template('epic.html', time_list=[v for v in time_list if v['epickey'] == id])



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if jira_handle.auth(session, (request.form['username'], request.form['password'])):
            return redirect(url_for('issues'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    jira_handle.logout(session)
    return redirect(url_for('issues'))


if __name__ == '__main__':
    app.run(debug=True, port=5002)
