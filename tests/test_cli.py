import unittest

import mock

from uvcclient import nvr


class TestCliUtils(unittest.TestCase):
    FAKE_ENV1 = {
        "UVC": "http://192.168.1.1:7080/?apiKey=foo",
    }

    FAKE_ENV2 = {
        "UVC_HOST": "192.168.1.2",
        "UVC_PORT": "7443",
        "UVC_APIKEY": "myKey",
    }

    @mock.patch("os.getenv")
    def test_get_auth_combined(self, mock_getenv):
        mock_getenv.side_effect = self.FAKE_ENV1.get
        host, port, key, path = nvr.get_auth_from_env()
        self.assertEqual("192.168.1.1", host)
        self.assertEqual(7080, port)
        self.assertEqual("foo", key)
        self.assertEqual("/", path)

    @mock.patch("os.getenv")
    def test_get_separate(self, mock_getenv):
        mock_getenv.side_effect = self.FAKE_ENV2.get
        host, port, key, path = nvr.get_auth_from_env()
        self.assertEqual("192.168.1.2", host)
        self.assertEqual(7443, port)
        self.assertEqual("myKey", key)
        self.assertEqual("/", path)
