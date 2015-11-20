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

import logging
import optparse

from uvcclient import nvr
from uvcclient import camera


def do_led(camera_info, enabled):
    cam_client = camera.UVCCameraClient(camera_info['host'],
                                        camera_info['username'],
                                        'ubnt')  # FIXME
    cam_client.login()
    print enabled
    cam_client.set_led(enabled)


def main():
    host, port, apikey, path = nvr.get_auth_from_env()

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
    parser.add_option('--set-led', default=None, metavar='ENABLED',
                      help='Enable/Disable front LED (on,off)')
    opts, args = parser.parse_args()

    if not all([host, port, apikey]):
        print('Host, port, and apikey are required')
        return

    if opts.verbose:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    client = nvr.UVCRemote(opts.host, opts.port, opts.apikey)

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
    elif opts.set_led is not None:
        camera = client.get_camera(opts.uuid)
        if not camera:
            print 'No such camera'
            return 1
        if 'Micro' not in camera['model']:
            print 'Only micro cameras support LED status'
            return 2
        do_led(camera, opts.set_led.lower() == 'on')
