try:
    import httplib
except ImportError:
    from http import client as httplib

import unittest

import mock

from uvcclient import camera


class TestCamera(unittest.TestCase):
    def test_set_led_on(self):
        c = camera.UVCCameraClient('foo', 'ubnt', 'ubnt')
        with mock.patch.object(c, '_cfgwrite') as mock_write:
            c.set_led(False)
            mock_write.assert_called_once_with('led.front.status', 0)

    def test_set_led_off(self):
        c = camera.UVCCameraClient('foo', 'ubnt', 'ubnt')
        with mock.patch.object(c, '_cfgwrite') as mock_write:
            c.set_led(True)
            mock_write.assert_called_once_with('led.front.status', 1)

    def test_cfgwrite(self):
        c = camera.UVCCameraClient('foo', 'ubnt', 'ubnt')
        c._cookie = 'foo-cookie'
        with mock.patch.object(httplib, 'HTTPConnection') as mock_h:
            conn = mock_h.return_value
            conn.getresponse.return_value.status = 200
            self.assertTrue(c._cfgwrite('foo', 'bar'))
            headers = {'Cookie': 'foo-cookie'}
            conn.request.assert_called_once_with('GET',
                                                 '/cfgwrite.cgi?foo=bar',
                                                 headers=headers)

    @mock.patch.object(httplib, 'HTTPConnection')
    def test_login(self, mock_h):
        c = camera.UVCCameraClient('foo', 'ubnt', 'ubnt')
        first = mock.MagicMock()
        second = mock.MagicMock()
        counter = [0]

        def fake_conn(*a, **k):
            if counter[0] == 0:
                counter[0] += 1
                return first
            elif counter[0] == 1:
                counter[0] += 1
                return second

        mock_h.side_effect = fake_conn
        cookie = 'thecookie AIROS_SESSIONID=foo; bar'
        first.getresponse.return_value.getheaders.return_value = [
            ('set-cookie', cookie)]
        second.getresponse.return_value.status = 200
        c.login()
        first.request.assert_called_once_with('GET', '/')
        self.assertEqual('POST',
                         second.request.call_args_list[0][0][0])
        self.assertEqual('/login.cgi',
                         second.request.call_args_list[0][0][1])
        formdata = 'AIROS_SESSIONID=foo&password=ubnt&username=ubnt'
        self.assertEqual(
            sorted(formdata.split('&')),
            sorted(second.request.call_args_list[0][0][2].split('&')))
        self.assertEqual(cookie,
                         second.request.call_args_list[0][0][3]['Cookie'])
