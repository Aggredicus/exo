#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# ConsciOS integration addition maintained in Aggredicus/exo.
# This file is not part of upstream exo unless separately contributed and accepted.

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class CompatibilitySummary:
    protocol: str
    endpoint: str
    node_count: int
    instance_count: int
    task_count: int
    model_ids: list[str]
    last_event_applied_index: int | None
    mutating_requests_sent: bool = False


def normalize_endpoint(value: str) -> str:
    endpoint = value.strip().rstrip("/")
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("endpoint must be an absolute http(s) URL")
    return endpoint


def _json_get(endpoint: str, path: str, timeout: float) -> Any:
    request = Request(
        f"{endpoint}{path}",
        method="GET",
        headers={"Accept": "application/json", "User-Agent": "ConsciOS-exo-probe/1"},
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is explicit user input
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"GET {path} returned HTTP {response.status}")
        return json.load(response)


def _count(value: Any) -> int:
    if isinstance(value, (dict, list, tuple)):
        return len(value)
    return 0


def _node_count(state: dict[str, Any]) -> int:
    for key in ("nodeIdentities", "node_identities"):
        count = _count(state.get(key))
        if count:
            return count

    topology = state.get("topology")
    if isinstance(topology, dict):
        for key in ("nodes", "nodeIds", "node_ids"):
            count = _count(topology.get(key))
            if count:
                return count
    return 0


def _model_ids(payload: Any) -> list[str]:
    rows: Any
    if isinstance(payload, dict):
        rows = payload.get("data", [])
    else:
        rows = payload
    if not isinstance(rows, list):
        return []
    result = [row.get("id") for row in rows if isinstance(row, dict)]
    return sorted(value for value in result if isinstance(value, str) and value)


def inspect(endpoint: str, timeout: float = 5.0) -> CompatibilitySummary:
    normalized = normalize_endpoint(endpoint)
    state_raw = _json_get(normalized, "/state", timeout)
    models_raw = _json_get(normalized, "/v1/models", timeout)
    if not isinstance(state_raw, dict):
        raise TypeError("exo /state response must be a JSON object")

    return CompatibilitySummary(
        protocol="conscios-exo-http/v1",
        endpoint=normalized,
        node_count=_node_count(state_raw),
        instance_count=_count(state_raw.get("instances")),
        task_count=_count(state_raw.get("tasks")),
        model_ids=_model_ids(models_raw),
        last_event_applied_index=state_raw.get(
            "lastEventAppliedIdx", state_raw.get("last_event_applied_idx")
        ),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only compatibility probe for the ConsciOS browser provider. "
            "Only GET /state and GET /v1/models are requested."
        )
    )
    parser.add_argument("--endpoint", required=True, help="exo API endpoint")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = inspect(args.endpoint, timeout=args.timeout)
    except (ValueError, TypeError, RuntimeError, HTTPError, URLError, TimeoutError) as exc:
        print(f"ConsciOS compatibility probe failed: {exc}", file=sys.stderr)
        return 1

    indent = None if args.compact else 2
    print(json.dumps(asdict(summary), indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
