import requests


class JIRAhandler():
    _JiraSession = None
    _JiraBaseUrl = None

    def __init__(self, JiraBaseUrl):
        self._JiraSession = requests.session()  # NOT a Flask session
        self._JiraBaseUrl = JiraBaseUrl
        self._JiraSession.auth = None

    # authenticate the specified auth against JIRA
    def auth(self, s, auth):
        self._JiraSession.auth = auth

        r = self._JiraSession.get(self._JiraBaseUrl + '/rest/auth/1/session')
        if r.status_code != 200:
            self._JiraSession.auth = None
            s['isAuthenticated'] = False
        else:
            s['isAuthenticated'] = True
        return r.status_code == 200

    def isAuth(self):
        return self._JiraSession.auth != None

    def logout(self, s):
        self._JiraSession.auth = None
        s['isAuthenticated'] = False



