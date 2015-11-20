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
import optparse
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

    def _uvc_request(self, path, method='GET', data=None,
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
        if resp.status / 100 != 2:
            return

        data = resp.read()
        if (headers.get('content-encoding') == 'gzip' or
                headers.get('Content-Encoding') == 'gzip'):
            data = zlib.decompress(data, 32 + zlib.MAX_WBITS)
        return json.loads(data.decode())

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

    def index(self):
        """Return an index of available cameras.

        :returns: A list of dictionaries with keys of name, uuid
        """
        cams = self._uvc_request('/api/2.0/camera')['data']
        return [{'name': x['name'],
                 'uuid': x['uuid'],
                 'state': x['state'],
                 'managed': x['managed'],
             } for x in cams]

    def name_to_uuid(self, name):
        """Attempt to convert a camera name to its UUID.

        :param name: Camera name
        :returns: The UUID of the first camera with the same name if found,
                  otherwise None
        """
        cameras = self.index()
        cams_by_name = {x['name']: x['uuid'] for x in cameras}
        return cams_by_name.get(name)


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


def main():
    host, port, apikey, path = get_auth_from_env()

    parser = optparse.OptionParser()
    parser.add_option('-H', '--host', default=host,
                      help='UVC Hostname')
    parser.add_option('-P', '--port', default=port, type=int,
                      help='UVC Port')
    parser.add_option('-K', '--apikey', default=apikey,
                      help='UVC API Key')
    parser.add_option('-v', '--verbose', action='store_true', default=False)
    parser.add_option('-d', '--dump', action='store_true', default=False)
    parser.add_option('-u', '--uuid', default=None, help='Camera UUID')
    parser.add_option('--name', default=None, help='Camera name')
    parser.add_option('-l', '--list', action='store_true', default=False)
    parser.add_option('--recordmode', default=None,
                      help='Recording mode (none,full,motion)')
    parser.add_option('--recordchannel', default=None,
                      help='Recording channel (high,medium,low)')
    parser.add_option('-p', '--get-picture-settings', action='store_true',
                      default=False,
                      help='Return picture settings as a string')
    parser.add_option('--set-picture-settings',
                      default=None,
                      help=('Set picture settings with a string like that '
                            'returned from --get-picture-settings'))
    opts, args = parser.parse_args()

    if not all([host, port, apikey]):
        print('Host, port, and apikey are required')
        return

    if opts.verbose:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    client = UVCRemote(opts.host, opts.port, opts.apikey)

    if opts.name:
        opts.uuid = client.name_to_uuid(opts.name)
        if not opts.uuid:
            print('`%s\' is not a valid name' % opts.name)
            return

    if opts.dump:
        client.dump(opts.uuid)
    elif opts.list:
        for cam in client.index():
            if not cam['managed']:
                status = 'new'
            elif cam['state'] == 'FIRMWARE_OUTDATED':
                status = 'outdated'
            elif cam['state'] == 'UPGRADING':
                status = 'upgrading'
            elif cam['state'] == 'DISCONNECTED':
                status = 'offline'
            elif cam['state'] == 'CONNECTED':
                status = 'online'
            else:
                status = 'unknown:%s' % cam['state']
            print('%s: %-24.24s [%10s]' % (cam['uuid'], cam['name'], status))
    elif opts.recordmode:
        if not opts.uuid:
            print('Name or UUID is required')
            return 1

        r = client.set_recordmode(opts.uuid, opts.recordmode,
                                  opts.recordchannel)
        if r is True:
            return 0
        else:
            return 1
    elif opts.get_picture_settings:
        settings = client.get_picture_settings(opts.uuid)
        print(','.join(['%s=%s' % (k, v) for k, v in settings.items()]))
        return 0
    elif opts.set_picture_settings:
        settings = {}
        try:
            for setting in opts.set_picture_settings.split(','):
                k, v = setting.split('=')
                settings[k] = v
        except ValueError:
            print('Invalid picture setting string format')
            return 1
        try:
            result = client.set_picture_settings(opts.uuid, settings)
        except Invalid as e:
            print('Invalid value: %s' % e)
            return 1
        for k in settings:
            if type(result[k])(settings[k]) != result[k]:
                print('Rejected: %s' % k)
        return 0
