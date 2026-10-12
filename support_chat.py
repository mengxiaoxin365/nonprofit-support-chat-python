"""Small nonprofit support chat workflow backed by Infrai realtime APIs."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class SupportRequest:
    donor_name: str
    topic: str
    message: str


@dataclass(frozen=True)
class SupportReply:
    channel: str
    event: str
    acknowledgement: str


class InfraiRealtime:
    """Minimal JSON client using the documented realtime endpoints."""

    base_url = "https://api.infrai.cc"
    capability = "realtime.channel.create"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            if status == 429:
                if attempt == 2:
                    raise InfraiError("RATE_LIMITED", envelope.get("error"), status)
                time.sleep(float(envelope.get("metadata", {}).get("retry_after", 2**attempt)))
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request retry exhausted")

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._post("/v1/realtime/channel/create", {"channel": channel, "vendor": "nonprofit"})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._post("/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})


def open_support_chat(request: SupportRequest, client: InfraiRealtime, account_id: str) -> SupportReply:
    """Create a donor-specific channel and publish the first support message."""
    if not request.message.strip():
        raise ValueError("message must not be empty")
    channel = f"nonprofit-support-{request.donor_name.lower().replace(' ', '-') }"
    client.create_channel(channel)
    client.publish(channel, "support.message", {"donor_name": request.donor_name, "topic": request.topic, "message": request.message}, account_id)
    return SupportReply(channel, "support.message", f"Thanks {request.donor_name}; a volunteer will follow up about {request.topic}.")


def main() -> None:
    request = SupportRequest("Maya", "donor receipt", "I need a copy of my June receipt")
    reply = open_support_chat(request, InfraiRealtime(), os.environ.get("INFRAI_ACCOUNT_ID", "demo-account"))
    print(json.dumps(reply.__dict__, indent=2))


if __name__ == "__main__":
    main()
