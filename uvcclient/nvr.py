#!/usr/bin/env python
#
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


import json
import logging
import pprint
import os
import sys
import zlib


# Python3 compatibility
try:
    import httplib
except ImportError:
    from http import client as httplib
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class Invalid(Exception):
    pass


class NotAuthorized(Exception):
    pass


class NvrError(Exception):
    pass


class UVCRemote(object):
    """Remote control client for Ubiquiti Unifi Video NVR."""
    CHANNEL_NAMES = ['high', 'medium', 'low']

    def __init__(self, host, port, apikey, path='/'):
        self._host = host
        self._port = port
        self._path = path
        if path != '/':
            raise Invalid('Path not supported yet')
        self._apikey = apikey
        self._log = logging.getLogger('UVC(%s:%s)' % (host, port))
        self._bootstrap = self._get_bootstrap()
        version = '.'.join(str(x) for x in self.server_version)
        self._log.debug('Server version is %s' % version)

    @property
    def server_version(self):
        return tuple(
            int(x) for x in self._bootstrap['systemInfo']['version'].split('.')
        )

    @property
    def camera_identifier(self):
        if self.server_version >= (3, 2, 0):
            return 'id'
        else:
            return 'uuid'

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

    def _uvc_request(self, *args, **kwargs):
        try:
            return self._uvc_request_safe(*args, **kwargs)
        except OSError:
            raise NvrError('Failed to contact NVR')
        except httplib.HTTPException as ex:
            raise NvrError('Error connecting to camera: %s' % str(ex))

    def _uvc_request_safe(self, path, method='GET', data=None,
                          mimetype='application/json'):
        conn = httplib.HTTPConnection(self._host, self._port)
        if '?' in path:
            url = '%s&apiKey=%s' % (path, self._apikey)
        else:
            url = '%s?apiKey=%s' % (path, self._apikey)

        headers = {
            'Content-Type': mimetype,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
        }
        self._log.debug('%s %s headers=%s data=%s' % (
            method, url, headers, repr(data)))
        conn.request(method, url, data, headers)
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        self._log.debug('%s %s Result: %s %s' % (method, url, resp.status,
                                                 resp.reason))
        if resp.status in (401, 403):
            raise NotAuthorized('NVR reported authorization failure')
        if resp.status / 100 != 2:
            raise NvrError('Request failed: %s' % resp.status)

        data = resp.read()
        if (headers.get('content-encoding') == 'gzip' or
                headers.get('Content-Encoding') == 'gzip'):
            data = zlib.decompress(data, 32 + zlib.MAX_WBITS)
        return json.loads(data.decode())

    def _get_bootstrap(self):
        return self._uvc_request('/api/2.0/bootstrap')['data'][0]

    def dump(self, uuid):
        """Dump information for a camera by UUID."""
        data = self._uvc_request('/api/2.0/camera/%s' % uuid)
        pprint.pprint(data)

    def set_recordmode(self, uuid, mode, chan=None):
        """Set the recording mode for a camera by UUID.

        :param uuid: Camera UUID
        :param mode: One of none, full, or motion
        :param chan: One of the values from CHANNEL_NAMES
        :returns: True if successful, False or None otherwise
        """

        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        settings = data['data'][0]['recordingSettings']
        mode = mode.lower()
        if mode == 'none':
            settings['fullTimeRecordEnabled'] = False
            settings['motionRecordEnabled'] = False
        elif mode == 'full':
            settings['fullTimeRecordEnabled'] = True
            settings['motionRecordEnabled'] = False
        elif mode == 'motion':
            settings['fullTimeRecordEnabled'] = False
            settings['motionRecordEnabled'] = True
        else:
            raise Invalid('Unknown mode')

        if chan:
            settings['channel'] = self.CHANNEL_NAMES.index(chan)
            changed = data['data'][0]['recordingSettings']

        data = self._uvc_request(url, 'PUT', json.dumps(data['data'][0]))
        updated = data['data'][0]['recordingSettings']
        return settings == updated

    def get_recordmode(self, uuid):
        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        recmodes = data['data'][0]['recordingSettings']
        if recmodes['fullTimeRecordEnabled']:
            return 'full'
        elif recmodes['motionRecordEnabled']:
            return 'motion'
        else:
            return 'none'

    def get_picture_settings(self, uuid):
        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        return data['data'][0]['ispSettings']

    def set_picture_settings(self, uuid, settings):
        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        for key in settings:
            dtype = type(data['data'][0]['ispSettings'][key])
            try:
                data['data'][0]['ispSettings'][key] = dtype(settings[key])
            except ValueError:
                raise Invalid('Setting `%s\' requires %s not %s' % (
                    key, dtype.__name__, type(settings[key]).__name__))
        data = self._uvc_request(url, 'PUT', json.dumps(data['data'][0]))
        return data['data'][0]['ispSettings']

    def prune_zones(self, uuid):
        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        data['data'][0]['zones'] = [data['data'][0]['zones'][0]]
        self._uvc_request(url, 'PUT', json.dumps(data['data'][0]))

    def list_zones(self, uuid):
        url = '/api/2.0/camera/%s' % uuid
        data = self._uvc_request(url)
        return data['data'][0]['zones']

    def index(self):
        """Return an index of available cameras.

        :returns: A list of dictionaries with keys of name, uuid
        """
        cams = self._uvc_request('/api/2.0/camera')['data']
        return [{'name': x['name'],
                 'uuid': x['uuid'],
                 'state': x['state'],
                 'managed': x['managed'],
                 'id': x['_id'],
             } for x in cams]

    def name_to_uuid(self, name):
        """Attempt to convert a camera name to its UUID.

        :param name: Camera name
        :returns: The UUID of the first camera with the same name if found,
                  otherwise None. On v3.2.0 and later, returns id.
        """
        cameras = self.index()
        if self.server_version >= (3, 2, 0):
            cams_by_name = {x['name']: x['id'] for x in cameras}
        else:
            cams_by_name = {x['name']: x['uuid'] for x in cameras}
        return cams_by_name.get(name)

    def get_camera(self, uuid):
        return self._uvc_request('/api/2.0/camera/%s' % uuid)['data'][0]

    def get_snapshot(self, uuid):
        url = '/api/2.0/snapshot/camera/%s?force=true&apiKey=%s' % (
            uuid, self._apikey)
        print(url)
        resp = self._safe_request('GET', url)
        if resp.status != 200:
            raise NvrError('Snapshot returned %i' % resp.status)
        return resp.read()


def get_auth_from_env():
    """Attempt to get UVC NVR connection information from the environment.

    Supports either a combined variable called UVC formatted like:

        UVC="http://192.168.1.1:7080/?apiKey=XXXXXXXX"

    or individual ones like:

        UVC_HOST=192.168.1.1
        UVC_PORT=7080
        UVC_APIKEY=XXXXXXXXXX

    :returns: A tuple like (host, port, apikey, path)
    """

    combined = os.getenv('UVC')
    if combined:
        # http://192.168.1.1:7080/apikey
        result = urlparse.urlparse(combined)
        if ':' in result.netloc:
            host, port = result.netloc.split(':', 1)
            port = int(port)
        else:
            host = result.netloc
            port = 7080
        apikey = urlparse.parse_qs(result.query)['apiKey'][0]
        path = result.path
    else:
        host = os.getenv('UVC_HOST')
        port = int(os.getenv('UVC_PORT', 7080))
        apikey = os.getenv('UVC_APIKEY')
        path = '/'
    return host, port, apikey, path
