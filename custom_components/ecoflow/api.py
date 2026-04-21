"""EcoFlow API client — HTTP + MQTT."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import random
import time
from typing import Any, Callable

import aiohttp

_LOGGER = logging.getLogger(__name__)


def _build_sign(params: dict, access_key: str, secret_key: str) -> tuple[str, str, str, str]:
    """Create HMAC-SHA256 signature per EcoFlow docs."""
    nonce = str(random.randint(100000, 999999))
    timestamp = str(int(time.time() * 1000))

    # All parameters (including auth fields) must be flattened and sorted together
    flat: list[str] = []
    _flatten(params, "", flat)
    flat.append(f"accessKey={access_key}")
    flat.append(f"nonce={nonce}")
    flat.append(f"timestamp={timestamp}")
    flat.sort()

    query_str = "&".join(flat)

    # HMAC-SHA256 → hex
    sign = hmac.new(
        secret_key.encode("utf-8"),
        query_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return nonce, timestamp, sign, query_str


def _flatten(obj: Any, prefix: str, result: list[str]) -> None:
    """Recursively flatten a dict to param=value strings using JSON-like representation."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            _flatten(v, new_key, result)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}[{i}]"
            _flatten(v, new_key, result)
    else:
        # Convert values to JSON-compatible strings
        if obj is True:
            val = "true"
        elif obj is False:
            val = "false"
        elif obj is None:
            val = "null"
        else:
            val = str(obj)
        result.append(f"{prefix}={val}")


def _headers(access_key: str, nonce: str, timestamp: str, sign: str) -> dict:
    return {
        "accessKey": access_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
        "Content-Type": "application/json;charset=UTF-8",
    }


class EcoFlowApiError(Exception):
    """Raised when the EcoFlow API returns an error."""


class EcoFlowApiClient:
    """HTTP API client for EcoFlow open platform."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        session: aiohttp.ClientSession,
        api_host: str = "https://api-e.ecoflow.com",
    ) -> None:
        self._access_key = access_key
        self._secret_key = secret_key
        self._session = session
        self._base = api_host.rstrip("/")

    # ── GET requests (no body — params go in query string) ───────────────────

    async def _get(self, path: str, query: dict | None = None) -> dict:
        params = query or {}
        nonce, timestamp, sign, _ = _build_sign(params, self._access_key, self._secret_key)
        headers = _headers(self._access_key, nonce, timestamp, sign)
        url = self._base + path
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
        if data.get("code") != "0":
            raise EcoFlowApiError(f"API error: {data.get('message', data)}")
        return data

    # ── POST requests (JSON body) ─────────────────────────────────────────────

    async def _post(self, path: str, body: dict) -> dict:
        nonce, timestamp, sign, _ = _build_sign(body, self._access_key, self._secret_key)
        headers = _headers(self._access_key, nonce, timestamp, sign)
        url = self._base + path
        async with self._session.post(url, json=body, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
        if data.get("code") != "0":
            raise EcoFlowApiError(f"API error: {data.get('message', data)}")
        return data

    # ── PUT requests (JSON body) ──────────────────────────────────────────────

    async def _put(self, path: str, body: dict) -> dict:
        nonce, timestamp, sign, _ = _build_sign(body, self._access_key, self._secret_key)
        headers = _headers(self._access_key, nonce, timestamp, sign)
        url = self._base + path
        async with self._session.put(url, json=body, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
        if data.get("code") != "0":
            raise EcoFlowApiError(f"API error: {data.get('message', data)}")
        return data

    # ── Public API methods ────────────────────────────────────────────────────

    async def get_device_list(self) -> list[dict]:
        """Return list of devices bound to the account."""
        data = await self._get("/iot-open/sign/device/list")
        return data.get("data", [])

    async def get_all_quota(self, sn: str) -> dict:
        """Fetch all quota values for a device."""
        data = await self._get("/iot-open/sign/device/quota/all", {"sn": sn})
        return data.get("data", {})

    async def set_quota(self, sn: str, params: dict) -> None:
        """Set one or more device quota values."""
        body = {"sn": sn, "params": params}
        await self._put("/iot-open/sign/device/quota", body)

    async def get_mqtt_cert(self) -> dict:
        """Obtain MQTT credentials."""
        data = await self._get("/iot-open/sign/certification")
        return data.get("data", {})

    async def test_credentials(self) -> bool:
        """Validate credentials by fetching the device list."""
        try:
            await self.get_device_list()
            return True
        except Exception:  # noqa: BLE001
            return False


# ─── MQTT client (uses paho-mqtt in a thread) ────────────────────────────────

class EcoFlowMQTTClient:
    """Subscribe to real-time device data via MQTT."""

    def __init__(
        self,
        cert: dict,
        sn: str,
        on_data: Callable[[dict], None],
        on_status: Callable[[bool], None],
    ) -> None:
        self._cert = cert
        self._sn = sn
        self._on_data = on_data
        self._on_status = on_status
        self._client = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start the MQTT client in a background thread."""
        import paho.mqtt.client as mqtt  # imported lazily

        self._loop = loop
        account = self._cert["certificateAccount"]
        password = self._cert["certificatePassword"]
        host = self._cert["url"]
        port = int(self._cert["port"])
        protocol = self._cert.get("protocol", "mqtts")

        quota_topic = f"/open/{account}/{self._sn}/quota"
        status_topic = f"/open/{account}/{self._sn}/status"

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                _LOGGER.debug("EcoFlow MQTT connected")
                client.subscribe(quota_topic)
                client.subscribe(status_topic)
            else:
                _LOGGER.warning("EcoFlow MQTT connect failed rc=%s", rc)

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
            except ValueError:
                return

            if msg.topic == status_topic:
                online = payload.get("params", {}).get("status", 0) == 1
                if self._loop:
                    asyncio.run_coroutine_threadsafe(
                        _call_async(self._on_status, online), self._loop
                    )
            else:
                # Quota report: flatten nested params into flat dict
                params = payload.get("params", payload)
                if self._loop:
                    asyncio.run_coroutine_threadsafe(
                        _call_async(self._on_data, params), self._loop
                    )

        client = mqtt.Client(client_id=f"ha-ecoflow-{self._sn}", protocol=mqtt.MQTTv311)
        client.username_pw_set(account, password)
        if protocol == "mqtts":
            import ssl
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect_async(host, port, keepalive=60)
        client.loop_start()
        self._client = client

    def stop(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None

    def publish_set(self, params: dict) -> None:
        """Publish a set command via MQTT (fire-and-forget)."""
        if not self._client:
            return
        cert = self._cert
        account = cert["certificateAccount"]
        topic = f"/open/{account}/{self._sn}/set"
        payload = {
            "id": str(int(time.time() * 1000)),
            "version": "1.0",
            **params,
        }
        self._client.publish(topic, json.dumps(payload))


async def _call_async(fn: Callable, *args) -> None:
    """Safely call a sync or async callback."""
    result = fn(*args)
    if asyncio.iscoroutine(result):
        await result
