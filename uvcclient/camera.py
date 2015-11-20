#   Copyright 2015 Dan Smith (dsmith+uvc@danplanet.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

# Python3 compatibility
try:
    import httplib
except ImportError:
    from http import client as httplib
try:
    import urlparse
    import urllib
except ImportError:
    import urllib.parse as urlparse


class UVCCameraClient(object):
    def __init__(self, host, username, password, port=80):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._cookie = None
        self._log = logging.getLogger('UVCCamera(%s)' % self._host)

    def login(self):
        conn = httplib.HTTPConnection(self._host, self._port)
        conn.request('GET', '/')
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        self._cookie = headers['set-cookie']
        session = self._cookie.split('=')[1].split(';')[0]

        try:
            urlencode = urllib.urlencode
        except NameError:
            urlencode = urlparse.urlencode

        data = urlencode({'username': self._username,
                          'password': self._password,
                          'AIROS_SESSIONID': session})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "*",
                   'Cookie': self._cookie}
        conn = httplib.HTTPConnection(self._host, self._port)
        req = conn.request('POST', '/login.cgi', data, headers)
        resp = conn.getresponse()
        if resp.status != 200:
            raise Exception('Failed to login: %s' % resp.reason)

    def _cfgwrite(self, setting, value):
        conn = httplib.HTTPConnection(self._host, self._port)
        headers = {'Cookie': self._cookie}
        conn.request('GET', '/cfgwrite.cgi?%s=%s' % (setting, value),
                     headers=headers)
        resp = conn.getresponse()
        self._log.debug('Setting %s=%s: %s %s' % (setting, value,
                                                  resp.status,
                                                  resp.reason))
        return resp.status == 200

    def set_led(self, enabled):
        return self._cfgwrite('led.front.status', int(enabled))
