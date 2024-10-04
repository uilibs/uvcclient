#   Copyright 2015 Dan Smith (dsmith+uvc@danplanet.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import urllib.parse as urlparse
from http import client as httplib
from typing import Any

from uvcclient.const import LOGGER


class CameraConnectError(Exception):
    pass


class CameraAuthError(Exception):
    pass


class UVCCameraClient:
    def __init__(self, host: str, username: str, password: str, port: int = 80) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._cookie = ""

    def _safe_request(self, *args: Any, **kwargs: Any) -> httplib.HTTPResponse:
        try:
            conn = httplib.HTTPConnection(self._host, self._port)
            conn.request(*args, **kwargs)
            return conn.getresponse()
        except OSError as ex:
            raise CameraConnectError("Unable to contact camera") from ex
        except httplib.HTTPException as ex:
            raise CameraConnectError(f"Error connecting to camera: {ex!s}") from ex

    def login(self) -> None:
        resp = self._safe_request("GET", "/")
        headers = dict(resp.getheaders())
        try:
            self._cookie = headers["Set-Cookie"]
        except KeyError:
            self._cookie = headers["set-cookie"]
        session = self._cookie.split("=")[1].split(";")[0]

        urlencode = urlparse.urlencode

        data = urlencode(
            {
                "username": self._username,
                "password": self._password,
                "AIROS_SESSIONID": session,
            }
        )
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "*",
            "Cookie": self._cookie,
        }
        resp = self._safe_request("POST", "/login.cgi", data, headers)
        if resp.status != 200:
            raise CameraAuthError(f"Failed to login: {resp.reason}")

    def _cfgwrite(self, setting: str, value: str | int) -> bool:
        headers = {"Cookie": self._cookie}
        resp = self._safe_request(
            "GET", f"/cfgwrite.cgi?{setting}={value}", headers=headers
        )
        LOGGER.debug(f"Setting {setting}={value}: {resp.status} {resp.reason}")
        return resp.status == 200

    def set_led(self, enabled: bool) -> bool:
        return self._cfgwrite("led.front.status", int(enabled))

    @property
    def snapshot_url(self) -> str:
        return "/snapshot.cgi"

    @property
    def reboot_url(self) -> str:
        return "/api/1.1/reboot"

    @property
    def status_url(self) -> str:
        return "/api/1.1/status"

    def get_snapshot(self) -> bytes:
        headers = {"Cookie": self._cookie}
        resp = self._safe_request("GET", self.snapshot_url, headers=headers)
        if resp.status in (401, 403, 302):
            raise CameraAuthError("Not logged in")
        elif resp.status != 200:
            raise CameraConnectError(f"Snapshot failed: {resp.status}")
        return resp.read()

    def reboot(self) -> None:
        headers = {"Cookie": self._cookie}
        resp = self._safe_request("GET", self.reboot_url, headers=headers)
        if resp.status in (401, 403, 302):
            raise CameraAuthError("Not logged in")
        elif resp.status != 200:
            raise CameraConnectError(f"Reboot failed: {resp.status}")

    def get_status(self) -> dict[str, Any]:
        headers = {"Cookie": self._cookie}
        resp = self._safe_request("GET", self.status_url, headers=headers)
        if resp.status in (401, 403, 302):
            raise CameraAuthError("Not logged in")
        elif resp.status != 200:
            raise CameraConnectError(f"Status failed: {resp.status}")
        return json.loads(resp.read().decode())


class UVCCameraClientV320(UVCCameraClient):
    @property
    def snapshot_url(self) -> str:
        return "/snap.jpeg"

    def login(self) -> None:
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"username": self._username, "password": self._password})
        resp = self._safe_request("POST", "/api/1.1/login", data, headers=headers)
        if resp.status != 200:
            raise CameraAuthError(f"Failed to login: {resp.reason}")
        headers = dict(resp.getheaders())
        try:
            self._cookie = headers["Set-Cookie"]
        except KeyError:
            self._cookie = headers["set-cookie"]
