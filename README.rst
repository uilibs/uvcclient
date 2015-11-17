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
