#!/usr/bin/env python3
"""Generate an image through the ShineMoon OpenAI-compatible Images API."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://shinemoon.com/v1"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, help="Image prompt.")
    parser.add_argument("--out", required=True, help="Output image path, usually under outputs/.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name. Default: {DEFAULT_MODEL}")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"Requested size. Default: {DEFAULT_SIZE}")
    parser.add_argument("--base-url", default=os.getenv("SHINEMOON_IMAGE_API_BASE", DEFAULT_BASE_URL))
    parser.add_argument("--api-key-env", default="SHINEMOON_API_KEY", help="Environment variable containing the API key.")
    parser.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print sanitized request details without calling the API.")
    return parser.parse_args()


def safe_error_summary(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text[:1200]

    error = data.get("error", data)
    if isinstance(error, dict):
        summary = {
            key: error.get(key)
            for key in ("type", "code", "message")
            if error.get(key) is not None
        }
        return json.dumps(summary or error, ensure_ascii=False)[:1200]
    return json.dumps(error, ensure_ascii=False)[:1200]


def main() -> int:
    args = parse_args()
    endpoint = args.base_url.rstrip("/") + "/images/generations"
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "response_format": "b64_json",
    }

    if args.dry_run:
        print(json.dumps({"endpoint": endpoint, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        print(f"Missing API key: set {args.api_key_env}.", file=sys.stderr)
        return 2

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        print(f"HTTP {exc.code}: {safe_error_summary(raw)}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Network error: {exc.reason}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw.decode("utf-8"))
        image_b64 = data["data"][0]["b64_json"]
    except Exception as exc:  # noqa: BLE001 - produce useful CLI diagnostics.
        print(f"Could not find data[0].b64_json in HTTP {status} response: {exc}", file=sys.stderr)
        print(safe_error_summary(raw), file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image_bytes = base64.b64decode(image_b64)
    out_path.write_bytes(image_bytes)

    print(json.dumps({
        "status": status,
        "out": str(out_path),
        "bytes": len(image_bytes),
        "model": args.model,
        "requested_size": args.size,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
