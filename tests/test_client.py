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
        bootstrap_mock = mock.patch.object(nvr.UVCRemote, '_get_bootstrap',
                                           side_effect=self._bootstrap)
        bootstrap_mock.start()
        self._patches.append(bootstrap_mock)

    def _bootstrap(self):
        return {'systemInfo': {'version': '3.1.3'}}

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


class TestClient32(unittest.TestCase):
    @mock.patch.object(nvr.UVCRemote, '_get_bootstrap')
    def test_bootstrap_server_version(self, mock_bootstrap):
        mock_bootstrap.return_value = {'systemInfo': {'version': '3.4.5'}}
        client = nvr.UVCRemote('foo', 7080, 'key')
        self.assertEqual((3, 4, 5), client.server_version)

    @mock.patch.object(nvr.UVCRemote, '_get_bootstrap')
    def test_bootstrap_server_version(self, mock_bootstrap):
        mock_bootstrap.return_value = {'systemInfo': {'version': '3.4.beta5'}}
        client = nvr.UVCRemote('foo', 7080, 'key')
        self.assertEqual((3, 4, 0), client.server_version)

    @mock.patch.object(nvr.UVCRemote, '_get_bootstrap')
    @mock.patch.object(nvr.UVCRemote, 'index')
    def test_310_returns_uuid(self, mock_index, mock_bootstrap):
        mock_index.return_value = [{
            'name': mock.sentinel.name,
            'uuid': mock.sentinel.uuid,
            'id': mock.sentinel.id,
        }]
        mock_bootstrap.return_value = {'systemInfo': {'version': '3.1.0'}}
        client = nvr.UVCRemote('foo', 7080, 'key')
        self.assertEqual(mock.sentinel.uuid, client.name_to_uuid(
            mock.sentinel.name))

    @mock.patch.object(nvr.UVCRemote, '_get_bootstrap')
    @mock.patch.object(nvr.UVCRemote, 'index')
    def test_320_returns_uuid(self, mock_index, mock_bootstrap):
        mock_index.return_value = [{
            'name': mock.sentinel.name,
            'uuid': mock.sentinel.uuid,
            'id': mock.sentinel.id,
        }]
        mock_bootstrap.return_value = {'systemInfo': {'version': '3.2.0'}}
        client = nvr.UVCRemote('foo', 7080, 'key')
        self.assertEqual(mock.sentinel.id, client.name_to_uuid(
            mock.sentinel.name))


class TestClient(unittest.TestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        self._patches = []
        try:
            import httplib
            http_mock = mock.patch('httplib.HTTPConnection')
        except ImportError:
            http_mock = mock.patch('http.client.HTTPConnection')
        http_mock.start()
        self._patches.append(http_mock)
        bootstrap_mock = mock.patch.object(nvr.UVCRemote, '_get_bootstrap',
                                           side_effect=self._bootstrap)
        bootstrap_mock.start()
        self._patches.append(bootstrap_mock)

    def _bootstrap(self):
        return {'systemInfo': {'version': '3.1.3'}}

    def cleanUp(self):
        for i in self._patches:
            i.stop()

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

    def test_get_snapshot(self):
        client = nvr.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_safe_request') as mock_r:
            mock_r.return_value.status = 200
            mock_r.return_value.read.return_value = 'image'
            resp = client.get_snapshot('foo')
            mock_r.assert_called_once_with(
                'GET', '/api/2.0/snapshot/camera/foo?force=true&apiKey=key')
            self.assertEqual('image', resp)

    def test_get_snapshot_error(self):
        client = nvr.UVCRemote('foo', 7080, 'key')
        with mock.patch.object(client, '_safe_request') as mock_r:
            mock_r.return_value.status = 401
            self.assertRaises(nvr.NvrError, client.get_snapshot, 'foo')
