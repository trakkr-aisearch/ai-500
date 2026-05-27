#!/usr/bin/env python3
"""Fetch the public AI 500 rankings and write monthly snapshot artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_URL = "https://ranking-api-830752870576.us-east1.run.app/api/rankings/global?limit=500"
KNOWN_COLUMNS = [
    "rank",
    "brand_id",
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


def fetch_json(url: str) -> dict[str, Any]:
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
    rankings = data.get("rankings")
    if not isinstance(rankings, list):
        raise RuntimeError("API response must contain a 'rankings' list")
    if not rankings:
        raise RuntimeError("API response contained no ranking rows")
    return data


def month_id(value: str | None) -> str:
    if value:
        try:
            datetime.strptime(value, "%Y-%m")
        except ValueError as exc:
            raise argparse.ArgumentTypeError("month must be in YYYY-MM format") from exc
        return value
    return datetime.now(timezone.utc).strftime("%Y-%m")


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
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: csv_value(row.get(column)) for column in columns})


def changelog_line(month: str, data: dict[str, Any]) -> str:
    rankings = data["rankings"]
    top_brand = rankings[0].get("brand_id", "unknown")
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
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    month = month_id(args.month)
    data = fetch_json(args.api_url)
    json_path, csv_path, latest_path = write_snapshot(root, data, month)

    print(f"Wrote {json_path.relative_to(root)}")
    print(f"Wrote {csv_path.relative_to(root)}")
    print(f"Wrote {latest_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
