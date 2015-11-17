Client for Ubiquiti's Unifi Camera NVR
======================================

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

For example::

 $ export UVC="http://192.168.1.1:7080/?apiKey=XXXXXXXX"
 $ uvc --name Porch --recordmode motion --recordchannel high
