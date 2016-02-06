try:
    import httplib
except ImportError:
    from http import client as httplib

import json
import unittest
import zlib

import mock

from uvcclient import nvr


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
        client = nvr.UVCRemote('foo', 7080, 'key')
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
        client = nvr.UVCRemote('foo', 7080, 'key')
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
        client = nvr.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 404
        self.assertRaises(nvr.NvrError,
                          client._uvc_request, '/bar', method='PUT',
                          data='foobar')

    def test_uvc_request_failed_noauth(self):
        client = nvr.UVCRemote('foo', 7080, 'key')
        conn = httplib.HTTPConnection.return_value
        resp = conn.getresponse.return_value
        resp.status = 401
        self.assertRaises(nvr.NotAuthorized,
                          client._uvc_request, '/bar', method='PUT',
                          data='foobar')

    def test_uvc_request_deflated(self):
        client = nvr.UVCRemote('foo', 7080, 'key')
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

        client = nvr.UVCRemote('foo', 7080, 'key')
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

    def test_get_picture_settings(self):
        fake_resp = {'data': [{'ispSettings': {'settingA': 1,
                                               'settingB': 'foo'}}]}
        client = nvr.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.return_value = fake_resp
            self.assertEqual({'settingA': 1, 'settingB': 'foo'},
                             client.get_picture_settings('uuid'))

    def test_set_picture_settings(self):
        fake_resp = {'data': [{'ispSettings': {'settingA': 1,
                                               'settingB': 'foo'}}]}
        client = nvr.UVCRemote('foo', 7080, 'key')
        newvals = {'settingA': 2, 'settingB': 'foo'}
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.return_value = fake_resp
            resp = client.set_picture_settings('uuid', newvals)
            mock_r.assert_any_call('/api/2.0/camera/uuid', 'PUT',
                                   json.dumps({'ispSettings': newvals}))
            self.assertEqual(fake_resp['data'][0]['ispSettings'], resp)

    def test_set_picture_settings_coerces(self):
        fake_resp = {'data': [{'ispSettings': {'settingA': 1,
                                               'settingB': 'foo',
                                               'settingC': False,
                                           }}]}
        client = nvr.UVCRemote('foo', 7080, 'key')
        newvals = {'settingA': '2', 'settingB': False, 'settingC': 'foo'}
        newvals_expected = {'settingA': 2, 'settingB':
                            'False', 'settingC': True}
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.return_value = fake_resp
            resp = client.set_picture_settings('uuid', newvals)
            mock_r.assert_any_call('/api/2.0/camera/uuid', 'PUT',
                                   json.dumps(
                                       {'ispSettings': newvals_expected}))
            self.assertEqual(fake_resp['data'][0]['ispSettings'], resp)

    def test_get_zones(self):
        fake_resp = {'data': [{'zones': ['fake-zone1',
                                         'fake-zone2']}]}
        client = nvr.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.return_value = fake_resp
            resp = client.list_zones('uuid')
            mock_r.assert_any_call('/api/2.0/camera/uuid')
            self.assertEqual(fake_resp['data'][0]['zones'], resp)

    def test_prune_zones(self):
        fake_resp = {'data': [{'zones': ['fake-zone1',
                                         'fake-zone2']}]}
        client = nvr.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_uvc_request') as mock_r:
            mock_r.return_value = fake_resp
            resp = client.prune_zones('uuid')
            mock_r.assert_any_call('/api/2.0/camera/uuid', 'PUT',
                                   json.dumps({'zones': ['fake-zone1']}))
