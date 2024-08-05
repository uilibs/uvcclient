import contextlib
import unittest
from unittest import mock

from uvcclient import store

try:
    import __builtin__ as builtins
except ImportError:
    import builtins


class OpenHelper:
    def __init__(self):
        self.mock = mock.MagicMock()

    @contextlib.contextmanager
    def fake_open(self, path, mode):
        self.path = path
        self.mode = mode
        yield self.mock


class TestStore(unittest.TestCase):
    @mock.patch.object(builtins, "open")
    @mock.patch("os.path.expanduser")
    def test_loads_correct_file_default(self, mock_expand, mock_open):
        mock_expand.return_value = "foobar"
        mock_open.side_effect = OSError
        store.InfoStore()
        mock_open.assert_called_once_with("foobar")

    @mock.patch.object(builtins, "open")
    @mock.patch("os.path.expanduser")
    def test_loads_correct_file(self, mock_expand, mock_open):
        mock_open.side_effect = OSError
        store.InfoStore("barfoo")
        self.assertFalse(mock_expand.called)
        mock_open.assert_called_once_with("barfoo")

    @mock.patch("os.chmod")
    def test_writes_correct_file(self, mock_chmod):
        with mock.patch.object(builtins, "open") as mock_open:
            mock_open.side_effect = OSError
            s = store.InfoStore("barfoo")
        opener = OpenHelper()
        with mock.patch.object(builtins, "open", new=opener.fake_open):
            s.save()
        self.assertTrue(opener.mock.write.called)
        mock_chmod.assert_called_once_with("barfoo", 0o600)

    def test_get_camera_passwords(self):
        with mock.patch.object(builtins, "open") as mock_open:
            mock_open.side_effect = OSError
            s = store.InfoStore("barfoo")
        s._data = {"camera_passwords": {"foo": "bar"}}
        self.assertEqual({"foo": "bar"}, s.get_camera_passwords())
        self.assertEqual("bar", s.get_camera_password("foo"))
        self.assertEqual(None, s.get_camera_password("doesnotexist"))

    def test_set_camera_password(self):
        with mock.patch.object(builtins, "open") as mock_open:
            mock_open.side_effect = OSError
            s = store.InfoStore("barfoo")
        with mock.patch.object(s, "save") as mock_save:
            s.set_camera_password("foo", "bar")
            mock_save.assert_called_once_with()
        self.assertEqual({"foo": "bar"}, s.get_camera_passwords())
