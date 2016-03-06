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

import getpass
import logging
import optparse
import sys

from uvcclient import nvr
from uvcclient import camera
from uvcclient import store

INFO_STORE = store.get_info_store()


def do_led(camera_info, enabled):
    password = INFO_STORE.get_camera_password(camera_info['uuid']) or 'ubnt'
    cam_client = camera.UVCCameraClient(camera_info['host'],
                                        camera_info['username'],
                                        password)
    cam_client.login()
    cam_client.set_led(enabled)


def do_snapshot(client, camera_info):
    password = INFO_STORE.get_camera_password(camera_info['uuid']) or 'ubnt'
    cam_client = camera.UVCCameraClient(camera_info['host'],
                                        camera_info['username'],
                                        password)
    try:
        cam_client.login()
        return cam_client.get_snapshot()
    except (camera.CameraAuthError, camera.CameraConnectError):
        # Fall back to proxy through the NVR
        return client.get_snapshot(camera_info['uuid'])


def do_set_password(opts):
    print('This will store the administrator password for a camera ')
    print('for later use. It will be stored on disk obscured, but ')
    print('NOT ENCRYPTED! If this is not okay, cancel now.')
    print('')
    password1 = getpass.getpass('Password: ')
    password2 = getpass.getpass('Confirm: ')
    if password1 != password2:
        print('Passwords do not match')
        return
    INFO_STORE.set_camera_password(opts.connection_id, password1)
    print('Password set')


def main():
    host, port, apikey, path, connect_with_id = nvr.get_auth_from_env()

    parser = optparse.OptionParser()
    parser.add_option('-H', '--host', default=host,
                      help='UVC Hostname')
    parser.add_option('-P', '--port', default=port, type=int,
                      help='UVC Port')
    parser.add_option('-K', '--apikey', default=apikey,
                      help='UVC API Key')
    parser.add_option('-c', '--connect_with_id', action="store_true", default=connect_with_id,
                      help='Connect with _id instead of uuid')
    parser.add_option('-v', '--verbose', action='store_true', default=False)
    parser.add_option('-d', '--dump', action='store_true', default=False)
    parser.add_option('-u', '--uuid', default=None, help='Camera UUID')
    parser.add_option('-i', '--id', default=None, help='Camera connection id')
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
    parser.add_option('--get-snapshot', default=None, action='store_true',
                      help='Get a snapshot image and write to stdout')
    parser.add_option('--prune-zones', default=None, action='store_true',
                      help='Prune all but the first motion zone')
    parser.add_option('--list-zones', default=None, action='store_true',
                      help='List motion zones')
    parser.add_option('--set-password', default=None, action='store_true',
                      help='Store camera password')
    opts, args = parser.parse_args()

    if not all([host, port, apikey]):
        print('Host, port, and apikey are required')
        return

    if opts.verbose:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    cammera_connection_id = ''

    client = nvr.UVCRemote(opts.host, opts.port, opts.apikey, id_connection=opts.connect_with_id )

    if opts.list:
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
        return 0

    if opts.name:
        cammera_connection_id = client.name_to_connection_id(opts.name)
        print("got id {}".format(cammera_connection_id))
        if not cammera_connection_id:
            print('`%s\' is not a valid name' % opts.name)
            return 1

    else:
        if opts.connect_with_id:
            if not opts.connection_id and not cammera_connection_id:
                print('Name or connection id is required')
                return 1
            else:
                cammera_connection_id = opts.connection_id
        else:
            if not opts.uuid and not cammera_connection_id:
                print('Name or UUID is required')
                return 1
            else:
                cammera_connection_id = opts.uuid

    if opts.dump:
        client.dump(cammera_connection_id)

    elif opts.recordmode:

        r = client.set_recordmode(cammera_connection_id, opts.recordmode,
                                  opts.recordchannel)
        if r is True:
            return 0
        else:
            return 1
    elif opts.get_picture_settings:
        print("connection_id: {}".format(cammera_connection_id))
        settings = client.get_picture_settings(cammera_connection_id)
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
            result = client.set_picture_settings(cammera_connection_id, settings)
        except Invalid as e:
            print('Invalid value: %s' % e)
            return 1
        for k in settings:
            if type(result[k])(settings[k]) != result[k]:
                print('Rejected: %s' % k)
        return 0
    elif opts.set_led is not None:
        camera = client.get_camera(cammera_connection_id)
        if not camera:
            print('No such camera')
            return 1
        if 'Micro' not in camera['model']:
            print('Only micro cameras support LED status')
            return 2
        do_led(camera, opts.set_led.lower() == 'on')
    elif opts.prune_zones:
        client.prune_zones(cammera_connection_id)
    elif opts.list_zones:
        zones = client.list_zones(cammera_connection_id)
        for zone in zones:
            print(zone['name'])
    elif opts.get_snapshot:
        camera = client.get_camera(cammera_connection_id)
        if not camera:
            print('No such camera')
            return 1
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(do_snapshot(client, camera))
        else:
            sys.stdout.write(do_snapshot(client, camera))
    elif opts.set_password:
        do_set_password(opts)
