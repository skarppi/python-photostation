import requests.cookies
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import pickle
import time
from urlparse import urlparse
from pprint import pprint, pformat
from error import SynologyException

class SynologySession(object):

    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

        self.headers = {}
        self.info = {
                'SYNO.API.Info': {
                    'path': 'query.php'
                }
            }
        self.info = self.query('SYNO.API.Info', {
            'method': 'query', 
            'query': 'all'
            })

    def query(self, api, data):
        data.setdefault('api', api)
        data.setdefault('version', 1)

        headers=self.headers.copy()

        if "original" in data:
            data = MultipartEncoder(fields=data)
            headers['Content-Type'] = data.content_type

        r = self.session.post(self.url + self.info[api]['path'], data=data, headers=headers)

        #print('request: ' + r.url + ' with data ' + pformat(data))

        return self.validate(api, data, r)

    def validate(self, api, request, response):
        if response.status_code is not 200:
            print('{} response with code {} and body {}'.format(api, response.status_code, response.text))
            raise SynologyException('The API request cannot been made')

        rsp = response.json()

        if not rsp['success']:
            print('{} response with code {} and body {} to query {}'.format(api, response.status_code, pformat(rsp), pformat(request)))
            raise SynologyException(rsp['error']['code'])

        if 'data' in rsp:
            return rsp['data']
        else:
            return rsp

class SynologyAuthSession(SynologySession):

    def __init__(self, url):
        components = urlparse(url)
        self.username = components.username

        # sanitized url
        url = url.replace(self.username + ':' + components.password + '@', '')

        super(SynologyAuthSession, self).__init__(url)

        self.authenticate(self.username, components.password)

    def authenticate(self, username, password):
        cookiefile = './cookies-{}.txt'.format(username)
        if self.load_cookies(cookiefile):
            self.headers = {
                'X-SYNO-TOKEN': self.session.cookies.get_dict()['PHPSESSID']
            }

            if self.authenticated():
                return

        self.login_query(username, password)
        self.save_cookies(cookiefile)

        self.headers = {
            'X-SYNO-TOKEN': self.session.cookies.get_dict()['PHPSESSID']
        }

    def authenticated(self):
        print('check authentication status')
        check = self.query('SYNO.PhotoStation.Auth', { 'method': 'checkauth' })
        return check['permission']['manage']

    def login_query(self, username, password):
        print('login request for user ' + username)
        
        api = 'SYNO.PhotoStation.Auth'
        params = {
            'api': api,
            'version': 1,
            'method': 'login',
            'username': username,
            'password': password,
            'remember_me': True
            }

        r = self.session.get(self.url + self.info[api]['path'], params=params)

        params['password'] = '******'
        data = self.validate('SYNO.PhotoStation.Auth', params, r)
        pprint('login response ' + pformat(data) + ' with headers ' + pformat(r.headers))

    def save_cookies(self, cookiefile):
        if not os.path.isdir(os.path.dirname(cookiefile)):
            return False
        print('save cookies to file ' + cookiefile)
        with open(cookiefile, 'w') as f:
            f.truncate()
            pickle.dump(self.session.cookies._cookies, f)


    def load_cookies(self, cookiefile):
        if not os.path.isfile(cookiefile):
            return False

        print('load cookies from file ' + cookiefile)
        with open(cookiefile) as f:
            cookies = pickle.load(f)
            if cookies:
                jar = requests.cookies.RequestsCookieJar()
                jar._cookies = cookies
                self.session.cookies = jar

                for cookie in jar:
                    if cookie.name == 'PHPSESSID':
                        pprint('session is valid until ' + str(cookie.expires) + ' minus 6 hours, now ' + str(int(time.time())))
                        return (cookie.expires - 3600 * 6)  > time.time()

                return False
            else:
                return False
