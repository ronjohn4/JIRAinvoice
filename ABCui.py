# todo - add user authentication (against JIRA)

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
    # todo - test for empty file, display an alert

    print('time_list - csv')
    print(time_list)

    keys = time_list[0].keys()

    output = io.StringIO()
    dict_writer = csv.DictWriter(output, keys)
    dict_writer.writeheader()
    dict_writer.writerows(time_list)

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

    display_list = []

    if request.method == 'POST':
        search = {'startdate': request.form["startdate"],
                  'enddate': request.form["enddate"]}
        logging.debug('search:' + str(search))

        last_search = search
        time_list, total_hours = HrsGet('ABC', search['startdate'], search['enddate'])

    # make unique on epickey
    print('display_list')
    print(display_list)
    display_list = list({v['epickey']: v for v in time_list}.values())

    # todo - reduce columns to epic only
    # or can just ignore other columns like it's doing now
    # saves data over the wire, this processing will be in the server

    # sort for presentation
    display_list = sorted(display_list, key=lambda k: (k['epickey'] is None, k['epickey']))
    # key = lambda x: (x is None, x)
    return render_template('issues.html', entries=display_list, search=last_search, total_hours=total_hours)


@app.route('/issues/<id>')
def issuesid(id=None):
    print('<id>', id)
    print(type(id))
    if id == 'None':
        id = None
    return render_template('issue.html', time_list=[v for v in time_list if v['epickey'] == id])


if __name__ == '__main__':
    app.run(debug=True, port=5002)
