#!/usr/bin/env python3
"""Fetch the public AI 500 rankings and write monthly snapshot artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


API_URL = "https://api.trakkr.ai/public/rankings/global?limit=500"
STATUS_URL = "https://api.trakkr.ai/public/rankings/status"
METHODOLOGY_URL = "https://trakkr.ai/rankings/methodology"
REPOSITORY_URL = "https://github.com/trakkr-aisearch/ai-500"
SCHEMA_VERSION = "1.1"
KNOWN_COLUMNS = [
    "rank",
    "brand_id",
    "brand_name",
    "brand_slug",
    "brand_url",
    "score",
    "mentions",
    "cumulative_mentions",
    "industries",
    "change_24h",
    "change_7d",
    "sector",
    "region",
    "company_size",
    "logo_url",
    "context",
]


def fetch_json(url: str, *, require_rankings: bool = True) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "trakkr-ai-500-snapshot/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected HTTP status {response.status}")
            payload = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch rankings from {url}: {exc}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"API did not return valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("API response must be a JSON object")
    if not require_rankings:
        return data

    rankings = data.get("rankings")
    if not isinstance(rankings, list):
        raise RuntimeError("API response must contain a 'rankings' list")
    if not rankings:
        raise RuntimeError("API response contained no ranking rows")
    return data


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{path} did not contain valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    rankings = data.get("rankings")
    if not isinstance(rankings, list):
        raise RuntimeError(f"{path} must contain a 'rankings' list")
    return data


def month_id(value: str | None) -> str:
    if value:
        try:
            datetime.strptime(value, "%Y-%m")
        except ValueError as exc:
            raise argparse.ArgumentTypeError("month must be in YYYY-MM format") from exc
        return value
    return datetime.now(timezone.utc).strftime("%Y-%m")


def brand_name(row: dict[str, Any]) -> str:
    for key in ("brand_name", "brand", "name", "brand_id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def brand_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def brand_url(value: str) -> str:
    return f"https://trakkr.ai/rankings/brand/{quote(value, safe='')}"


def enrich_rankings(data: dict[str, Any]) -> None:
    for row in data["rankings"]:
        if not isinstance(row, dict):
            raise RuntimeError("Each ranking row must be a JSON object")
        name = brand_name(row)
        row.setdefault("brand_name", name)
        row.setdefault("brand_slug", brand_slug(name))
        row.setdefault("brand_url", brand_url(name))


def build_meta(
    *,
    month: str,
    generated_at: str,
    row_count: int,
    source_url: str,
    status_url: str,
    source_status: dict[str, Any] | None,
) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_month": month,
        "generated_at": generated_at,
        "source_url": source_url,
        "status_url": status_url,
        "methodology_url": METHODOLOGY_URL,
        "repository_url": REPOSITORY_URL,
        "row_count": row_count,
        "publisher": {
            "name": "Trakkr",
            "url": "https://trakkr.ai",
        },
        "license": {
            "data": "CC-BY-4.0",
            "data_url": "https://creativecommons.org/licenses/by/4.0/",
            "code": "MIT",
            "code_url": "https://opensource.org/license/mit",
        },
    }
    if source_status is not None:
        meta["source_status"] = source_status
    return meta


def prepare_snapshot(
    data: dict[str, Any],
    *,
    month: str,
    source_url: str,
    status_url: str,
    source_status: dict[str, Any] | None,
) -> dict[str, Any]:
    enrich_rankings(data)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    data["meta"] = build_meta(
        month=month,
        generated_at=generated_at,
        row_count=len(data["rankings"]),
        source_url=source_url,
        status_url=status_url,
        source_status=source_status,
    )
    return data


def csv_columns(rows: list[dict[str, Any]]) -> list[str]:
    observed = []
    for column in KNOWN_COLUMNS:
        if any(column in row for row in rows):
            observed.append(column)

    extras = sorted({key for row in rows for key in row} - set(observed))
    return observed + extras


def csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = csv_columns(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: csv_value(row.get(column)) for column in columns})


def changelog_line(month: str, data: dict[str, Any]) -> str:
    rankings = data["rankings"]
    top_brand = rankings[0].get("brand_name") or rankings[0].get("brand_id", "unknown")
    row_count = len(rankings)
    return f"- {month}: captured {row_count} global ranking rows; top brand: {top_brand}."


def update_changelog(path: Path, month: str, data: dict[str, Any]) -> None:
    header = "# Changelog\n\nMonthly public snapshots of the AI 500 global rankings.\n\n"
    new_line = changelog_line(month, data)

    existing_lines: list[str] = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
        existing_lines = [line for line in lines if line.startswith("- ")]

    lines_by_month: dict[str, str] = {}
    for line in existing_lines:
        key = line.split(":", 1)[0].replace("- ", "", 1)
        if key:
            lines_by_month[key] = line
    lines_by_month[month] = new_line

    ordered = [lines_by_month[key] for key in sorted(lines_by_month, reverse=True)]
    path.write_text(header + "\n".join(ordered) + "\n", encoding="utf-8")


def write_snapshot(root: Path, data: dict[str, Any], month: str) -> tuple[Path, Path, Path]:
    snapshots_dir = root / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    json_path = snapshots_dir / f"{month}.json"
    csv_path = snapshots_dir / f"{month}.csv"
    latest_path = root / "latest.json"

    rows = data["rankings"]
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("Each ranking row must be a JSON object")

    write_json(json_path, data)
    write_csv(csv_path, rows)
    shutil.copyfile(json_path, latest_path)
    update_changelog(root / "CHANGELOG.md", month, data)

    return json_path, csv_path, latest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a monthly AI 500 snapshot.")
    parser.add_argument("--month", help="Snapshot month in YYYY-MM format. Defaults to current UTC month.")
    parser.add_argument("--api-url", default=API_URL, help="Rankings API URL.")
    parser.add_argument("--status-url", default=STATUS_URL, help="Rankings status API URL.")
    parser.add_argument("--input-json", help="Read an existing rankings JSON object instead of fetching the API.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    month = month_id(args.month)
    data = load_json(Path(args.input_json)) if args.input_json else fetch_json(args.api_url)

    source_status = None
    try:
        source_status = fetch_json(args.status_url, require_rankings=False)
    except RuntimeError as exc:
        print(f"Warning: status metadata unavailable: {exc}", file=sys.stderr)

    prepare_snapshot(
        data,
        month=month,
        source_url=args.api_url,
        status_url=args.status_url,
        source_status=source_status,
    )
    json_path, csv_path, latest_path = write_snapshot(root, data, month)

    print(f"Wrote {json_path.relative_to(root)}")
    print(f"Wrote {csv_path.relative_to(root)}")
    print(f"Wrote {latest_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
