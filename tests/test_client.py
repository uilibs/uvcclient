try:
    import httplib
except ImportError:
    from http import client as httplib

import json
import unittest
import zlib

import mock

from uvcclient import uvcclient


class TestClientLowLevel(unittest.TestCase):
    def setUp(self):
        super(TestClientLowLevel, self).setUp()
        self._patches = []
        try:
            import httplib
            http_mock = mock.patch('httplib.HTTPConnection')
        except ImportError:
            http_mock = mock.patch('http.client.HTTPConnection')
        http_mock.start()
        self._patches.append(http_mock)

    def cleanUp(self):
        for i in self._patches:
            i.stop()

    def test_uvc_request_get(self):
        client = uvcclient.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 200
        resp.read.return_value = json.dumps({}).encode()
        client._uvc_request('/bar')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
        }
        conn.request.assert_called_once_with('GET', '/bar?apiKey=key',
                                             None, headers)

    def test_uvc_request_put(self):
        client = uvcclient.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 200
        resp.read.return_value = json.dumps({}).encode()
        result = client._uvc_request('/bar?foo=bar', method='PUT',
                                     data='foobar')
        self.assertEqual({}, result)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
        }
        conn.request.assert_called_once_with('PUT', '/bar?foo=bar&apiKey=key',
                                             'foobar', headers)

    def test_uvc_request_failed(self):
        client = uvcclient.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 404
        result = client._uvc_request('/bar', method='PUT', data='foobar')
        self.assertEqual(None, result)

    def test_uvc_request_deflated(self):
        client = uvcclient.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 200
        resp.read.return_value = zlib.compress(json.dumps({}).encode())
        resp.getheaders.return_value = [('Content-Encoding', 'gzip')]
        client._uvc_request('/bar')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
        }
        conn.request.assert_called_once_with('GET', '/bar?apiKey=key',
                                             None, headers)


class TestClient(unittest.TestCase):
    def test_set_recordmode(self):
        fake_resp1 = {'data': [{'recordingSettings': {
            'fullTimeRecordEnabled': False,
            'motionRecordEnabled': False,
        }}]}
        fake_resp2 = {'data': [{'recordingSettings': {
            'fullTimeRecordEnabled': True,
            'motionRecordEnabled': False,
            'channel': 1,
        }}]}

        def fake_req(path, method='GET', data=None):
            if method == 'GET':
                return fake_resp1
            elif method == 'PUT':
                self.assertEqual(json.dumps(fake_resp2['data'][0]), data)
                return fake_resp2

        client = uvcclient.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.side_effect = fake_req
            client.set_recordmode('uuid', 'full', chan='medium')
            self.assertTrue(mock_r.called)

        fake_resp2['data'][0]['recordingSettings'] = {
            'fullTimeRecordEnabled': False,
            'motionRecordEnabled': True,
            'channel': 0,
        }
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.side_effect = fake_req
            client.set_recordmode('uuid', 'motion', chan='high')
            self.assertTrue(mock_r.called)
