Client for Ubiquiti's Unifi Camera NVR
======================================

.. image:: https://travis-ci.org/kk7ds/uvcclient.svg?branch=master
    :target: https://travis-ci.org/kk7ds/uvcclient

This is extremely raw at the moment. Use at your own risk.

Hopefully this is enough to get you going::

  Usage: uvc [options]

  Options:
    -h, --help            show this help message and exit
    -H HOST, --host=HOST  UVC Hostname
    -P PORT, --port=PORT  UVC Port
    -K APIKEY, --apikey=APIKEY
                          UVC API Key
    -v, --verbose
    -d, --dump
    -u UUID, --uuid=UUID  Camera UUID
    --name=NAME           Camera name
    -l, --list
    --recordmode=RECORDMODE
                          Recording mode (none,full,motion)
    --recordchannel=RECORDCHANNEL
                          Recording channel (high,medium,low)
    -p, --get-picture-settings
                          Return picture settings as a string
    --set-picture-settings=SET_PICTURE_SETTINGS
                          Set picture settings with a string like that returned
                          from --get-picture-settings
    --set-led=ENABLED     Enable/Disable front LED (on,off)
    --get-snapshot        Get a snapshot image and write to stdout
    --prune-zones         Prune all but the first motion zone
    --list-zones          List motion zones
    --set-password        Store camera password

For example::

 $ export UVC="http://192.168.1.1:7080/?apiKey=XXXXXXXX"
 $ uvc --name Porch --recordmode motion --recordchannel high

or::

 $ export UVC="http://192.168.1.1:7080/?apiKey=XXXXXXXX"
 $ uvc -l
 fb9e6d48-6f5a-42b2-8cb4-e3705a99a0e2: Inside                   [    online]
 f0579c60-e400-477e-8f89-f8861ef58f80: Parking                  [    online]
 998b134e-13ea-4465-ad39-6ad27b067ac4: Spare                    [   offline]
 5474242a-51d5-428e-97de-826675068e70: Front Porch              [    online]
 715f0725-e7e1-4214-a551-41071c82bacd: Garage                   [    online]

In order to take actions on cameras directly (such as change the LED
state on a UVC Micro or get a snapshot from the camera) you need to
set the admin password for it. The NVR tells us the username, but we
must store the password. To do this::

 $ uvc --name Porch --set-password
 This will store the administrator password for a camera
 for later use. It will be stored on disk obscured, but
 NOT ENCRYPTED! If this is not okay, cancel now.

 Password:
 Confirm:
 Password set

Then you can do things like get a snapshot from the camera directly::

 $ uvc --name Porch --get-snapshot > foo.jpg
