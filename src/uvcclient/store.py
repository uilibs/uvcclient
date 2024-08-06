import base64
import json
import logging
import os
from typing import Any

LOG = logging.getLogger(__name__)
_INFO_STORE = None


class UnableToManageStore(Exception):
    pass


class InfoStore:
    _data: dict[str, Any]

    def __init__(self, path: str | None = None) -> None:
        if path is None:
            path = os.path.expanduser(os.path.join("~", ".uvcclient"))
        self._path = path
        self.load()

    def load(self) -> None:
        try:
            with open(self._path) as f:
                self._data = json.loads(base64.b64decode(f.read()).decode())
        except OSError:
            LOG.debug("No info store")
            self._data = {}
        except Exception as ex:
            LOG.error("Failed to read store data: %s", ex)
            raise UnableToManageStore("Unable to write to store") from ex

    def save(self) -> None:
        try:
            with open(self._path, "w") as f:
                f.write(base64.b64encode(json.dumps(self._data).encode()).decode())
            os.chmod(self._path, 0o600)
        except OSError as ex:
            LOG.error("Unable to write store: %s", str(ex))
            raise UnableToManageStore("Unable to write to store") from ex

    def get_camera_passwords(self) -> dict[str, str]:
        return self._data.get("camera_passwords", {})

    def get_camera_password(self, uuid: str) -> str | None:
        return self.get_camera_passwords().get(uuid)

    def set_camera_password(self, uuid: str, password: str) -> None:
        if "camera_passwords" not in self._data:
            self._data["camera_passwords"] = {}
        self._data["camera_passwords"][uuid] = password
        self.save()


def get_info_store(path: str | None = None) -> InfoStore:
    global _INFO_STORE
    if _INFO_STORE is None:
        _INFO_STORE = InfoStore(path)
    return _INFO_STORE
