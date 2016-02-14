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


class CameraConnectError(Exception):
    pass


class UVCCameraClient(object):
    def __init__(self, host, username, password, port=80):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._cookie = None
        self._log = logging.getLogger('UVCCamera(%s)' % self._host)

    def _safe_request(self, *args, **kwargs):
        try:
            conn = httplib.HTTPConnection(self._host, self._port)
            conn.request(*args, **kwargs)
            return conn.getresponse()
        except OSError:
            raise CameraConnectionError('Unable to contact camera')
        except httplib.HTTPException as ex:
            raise CameraConnectionError('Error connecting to camera: %s' % (
                str(ex)))

    def login(self):
        resp = self._safe_request('GET', '/')
        headers = dict(resp.getheaders())
        self._cookie = headers['Set-Cookie']
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
        resp = self._safe_request('POST', '/login.cgi', data, headers)
        if resp.status != 200:
            raise Exception('Failed to login: %s' % resp.reason)

    def _cfgwrite(self, setting, value):
        headers = {'Cookie': self._cookie}
        resp = self._safe_request(
            'GET', '/cfgwrite.cgi?%s=%s' % (setting, value),
            headers=headers)
        self._log.debug('Setting %s=%s: %s %s' % (setting, value,
                                                  resp.status,
                                                  resp.reason))
        return resp.status == 200

    def set_led(self, enabled):
        return self._cfgwrite('led.front.status', int(enabled))

    def get_snapshot(self):
        conn = httplib.HTTPConnection(self._host, self._port)
        headers = {'Cookie': self._cookie}
        resp = self._safe_request('GET', '/snapshot.cgi',
                                  headers=headers)
        return resp.read()
