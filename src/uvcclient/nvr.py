#!/usr/bin/env python
#
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
import os
import pprint
import urllib.parse as urlparse
import zlib
from http import client as httplib
from typing import Any, Literal

from uvcclient.const import LOGGER


class Invalid(Exception):
    pass


class NotAuthorized(Exception):
    pass


class NvrError(Exception):
    pass


class CameraConnectionError(Exception):
    pass


class UVCRemote:
    """Remote control client for Ubiquiti Unifi Video NVR."""

    CHANNEL_NAMES = ["high", "medium", "low"]

    def __init__(
        self, host: str, port: int, apikey: str, path: str = "/", ssl: bool = False
    ) -> None:
        self._host = host
        self._port = port
        self._path = path
        self._ssl = ssl
        if path != "/":
            raise Invalid("Path not supported yet")
        self._apikey = apikey
        self._bootstrap = self._get_bootstrap()
        version = ".".join(str(x) for x in self.server_version)
        LOGGER.debug(f"Server version is {version}")

    @property
    def server_version(self) -> tuple[int, int, int]:
        version = self._bootstrap["systemInfo"]["version"].split(".")
        major = int(version[0])
        minor = int(version[1])
        try:
            rev = int(version[2])
        except ValueError:
            rev = 0
        return (major, minor, rev)

    @property
    def camera_identifier(self) -> str:
        if self.server_version >= (3, 2, 0):
            return "id"
        else:
            return "uuid"

    def _get_http_connection(self) -> httplib.HTTPConnection:
        if self._ssl:
            return httplib.HTTPSConnection(self._host, self._port)
        else:
            return httplib.HTTPConnection(self._host, self._port)

    def _safe_request(self, *args: Any, **kwargs: Any) -> httplib.HTTPResponse:
        try:
            conn = self._get_http_connection()
            conn.request(*args, **kwargs)
            return conn.getresponse()
        except OSError as ex:
            raise CameraConnectionError("Unable to contact camera") from ex
        except httplib.HTTPException as ex:
            raise CameraConnectionError(f"Error connecting to camera: {ex!s}") from ex

    def _uvc_request(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            return self._uvc_request_safe(*args, **kwargs)
        except OSError as ex:
            raise NvrError("Failed to contact NVR") from ex
        except httplib.HTTPException as ex:
            raise NvrError(f"Error connecting to camera: {ex!s}") from ex

    def _uvc_request_safe(
        self,
        path: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        mimetype: str = "application/json",
    ) -> dict[str, Any]:
        conn = self._get_http_connection()
        if "?" in path:
            url = f"{path}&apiKey={self._apikey}"
        else:
            url = f"{path}?apiKey={self._apikey}"

        headers = {
            "Content-Type": mimetype,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
        }
        LOGGER.debug(f"{method} {url} headers={headers} data={data!r}")
        body = None
        if data:
            body = json.dumps(data)
        conn.request(method, url, body, headers)
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        LOGGER.debug(f"{method} {url} Result: {resp.status} {resp.reason}")
        if resp.status in (401, 403):
            raise NotAuthorized("NVR reported authorization failure")
        if resp.status / 100 != 2:
            raise NvrError(f"Request failed: {resp.status}")

        res = resp.read()
        if (
            headers.get("content-encoding") == "gzip"
            or headers.get("Content-Encoding") == "gzip"
        ):
            res = zlib.decompress(res, 32 + zlib.MAX_WBITS)
        return json.loads(res.decode())

    def _get_bootstrap(self) -> dict[str, Any]:
        return self._uvc_request("/api/2.0/bootstrap")["data"][0]

    def dump(self, uuid: str) -> None:
        """Dump information for a camera by UUID."""
        data = self._uvc_request(f"/api/2.0/camera/{uuid}")
        pprint.pprint(data)

    def set_recordmode(self, uuid: str, mode: str, chan: str | None = None) -> bool:
        """
        Set the recording mode for a camera by UUID.

        :param uuid: Camera UUID
        :param mode: One of none, full, or motion
        :param chan: One of the values from CHANNEL_NAMES
        :returns: True if successful, False or None otherwise
        """
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        settings = data["data"][0]["recordingSettings"]
        mode = mode.lower()
        if mode == "none":
            settings["fullTimeRecordEnabled"] = False
            settings["motionRecordEnabled"] = False
        elif mode == "full":
            settings["fullTimeRecordEnabled"] = True
            settings["motionRecordEnabled"] = False
        elif mode == "motion":
            settings["fullTimeRecordEnabled"] = False
            settings["motionRecordEnabled"] = True
        else:
            raise Invalid("Unknown mode")

        if chan:
            settings["channel"] = self.CHANNEL_NAMES.index(chan)

        data = self._uvc_request(url, "PUT", json.dumps(data["data"][0]))
        updated = data["data"][0]["recordingSettings"]
        return settings == updated

    def get_recordmode(self, uuid: str) -> Literal["none", "full", "motion"]:
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        recmodes = data["data"][0]["recordingSettings"]
        if recmodes["fullTimeRecordEnabled"]:
            return "full"
        elif recmodes["motionRecordEnabled"]:
            return "motion"
        else:
            return "none"

    def get_picture_settings(self, uuid: str) -> dict[str, Any]:
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        return data["data"][0]["ispSettings"]

    def set_picture_settings(
        self, uuid: str, settings: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        for key in settings:
            dtype = type(data["data"][0]["ispSettings"][key])
            try:
                data["data"][0]["ispSettings"][key] = dtype(settings[key])
            except ValueError as ex:
                raise Invalid(
                    f"Setting `{key}' requires {dtype.__name__} not {type(settings[key]).__name__}"
                ) from ex
        data = self._uvc_request(url, "PUT", json.dumps(data["data"][0]))
        return data["data"][0]["ispSettings"]

    def prune_zones(self, uuid: str) -> None:
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        data["data"][0]["zones"] = [data["data"][0]["zones"][0]]
        self._uvc_request(url, "PUT", json.dumps(data["data"][0]))

    def list_zones(self, uuid: str) -> list[dict[str, Any]]:
        url = f"/api/2.0/camera/{uuid}"
        data = self._uvc_request(url)
        return data["data"][0]["zones"]

    def index(self) -> list[dict[str, Any]]:
        """
        Return an index of available cameras.

        :returns: A list of dictionaries with keys of name, uuid
        """
        cams = self._uvc_request("/api/2.0/camera")["data"]
        return [
            {
                "name": x["name"],
                "uuid": x["uuid"],
                "state": x["state"],
                "managed": x["managed"],
                "id": x["_id"],
            }
            for x in cams
            if not x["deleted"]
        ]

    def name_to_uuid(self, name: str) -> str | None:
        """
        Attempt to convert a camera name to its UUID.

        :param name: Camera name
        :returns: The UUID of the first camera with the same name if found,
                  otherwise None. On v3.2.0 and later, returns id.
        """
        cameras = self.index()
        if self.server_version >= (3, 2, 0):
            cams_by_name = {x["name"]: x["id"] for x in cameras}
        else:
            cams_by_name = {x["name"]: x["uuid"] for x in cameras}
        return cams_by_name.get(name)

    def get_camera(self, uuid: str) -> dict[str, Any]:
        return self._uvc_request(f"/api/2.0/camera/{uuid}")["data"][0]

    def get_snapshot(self, uuid: str) -> bytes:
        url = f"/api/2.0/snapshot/camera/{uuid}?force=true&apiKey={self._apikey}"
        print(url)
        resp = self._safe_request("GET", url)
        if resp.status != 200:
            raise NvrError("Snapshot returned %i" % resp.status)
        return resp.read()


def get_auth_from_env() -> tuple[str | None, int, str | None, str]:
    """
    Attempt to get UVC NVR connection information from the environment.

    Supports either a combined variable called UVC formatted like:

        UVC="http://192.168.1.1:7080/?apiKey=XXXXXXXX"

    or individual ones like:

        UVC_HOST=192.168.1.1
        UVC_PORT=7080
        UVC_APIKEY=XXXXXXXXXX

    :returns: A tuple like (host, port, apikey, path)
    """
    combined = os.getenv("UVC")
    if combined:
        # http://192.168.1.1:7080/apikey
        result = urlparse.urlparse(combined)
        if ":" in result.netloc:
            host, found_port = result.netloc.split(":", 1)
            port = int(found_port)
        else:
            host = result.netloc
            port = 7080
        apikey = urlparse.parse_qs(result.query)["apiKey"][0]
        path = result.path
        return host, port, apikey, path
    else:
        env_host = os.getenv("UVC_HOST")
        env_port = int(os.getenv("UVC_PORT", 7080))
        env_apikey = os.getenv("UVC_APIKEY")
        env_path = "/"
        return env_host, env_port, env_apikey, env_path
