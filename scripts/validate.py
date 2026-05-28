#!/usr/bin/env python3
"""Validate AI 500 snapshot structure and monthly artifact consistency."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_META_FIELDS = {
    "schema_version",
    "snapshot_month",
    "generated_at",
    "source_url",
    "status_url",
    "methodology_url",
    "repository_url",
    "row_count",
    "publisher",
    "license",
}

REQUIRED_ROW_FIELDS = {
    "rank",
    "brand_id",
    "brand_name",
    "brand_slug",
    "brand_url",
    "score",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def validate_snapshot(path: Path) -> dict[str, Any]:
    data = load_json(path)
    meta = data.get("meta")
    if not isinstance(meta, dict):
        raise AssertionError(f"{path} is missing top-level meta")
    missing_meta = REQUIRED_META_FIELDS - set(meta)
    if missing_meta:
        raise AssertionError(f"{path} meta missing fields: {sorted(missing_meta)}")

    rankings = data.get("rankings")
    if not isinstance(rankings, list):
        raise AssertionError(f"{path} must contain a rankings list")
    if len(rankings) != 500:
        raise AssertionError(f"{path} must contain 500 ranking rows, found {len(rankings)}")
    if meta.get("row_count") != len(rankings):
        raise AssertionError(f"{path} meta.row_count must match rankings length")

    seen_brands: set[str] = set()
    for expected_rank, row in enumerate(rankings, 1):
        if not isinstance(row, dict):
            raise AssertionError(f"{path} row {expected_rank} must be an object")
        missing_row = REQUIRED_ROW_FIELDS - set(row)
        if missing_row:
            raise AssertionError(f"{path} row {expected_rank} missing fields: {sorted(missing_row)}")
        if row.get("rank") != expected_rank:
            raise AssertionError(f"{path} expected rank {expected_rank}, found {row.get('rank')}")
        brand_id = str(row.get("brand_id") or "").strip()
        if not brand_id:
            raise AssertionError(f"{path} row {expected_rank} has blank brand_id")
        if brand_id in seen_brands:
            raise AssertionError(f"{path} duplicate brand_id: {brand_id}")
        seen_brands.add(brand_id)
        brand_url = str(row.get("brand_url") or "")
        if not brand_url.startswith("https://trakkr.ai/rankings/brand/"):
            raise AssertionError(f"{path} row {expected_rank} has invalid brand_url: {brand_url}")

    if not str(meta["source_url"]).startswith("https://api.trakkr.ai/public/rankings/global"):
        raise AssertionError(f"{path} meta.source_url must use the branded public rankings endpoint")
    if meta["status_url"] != "https://api.trakkr.ai/public/rankings/status":
        raise AssertionError(f"{path} meta.status_url must use the branded public status endpoint")
    return data


def validate_csv(path: Path) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if len(rows) != 500:
        raise AssertionError(f"{path} must contain 500 data rows, found {len(rows)}")
    missing = REQUIRED_ROW_FIELDS - set(reader.fieldnames or [])
    if missing:
        raise AssertionError(f"{path} missing columns: {sorted(missing)}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest = validate_snapshot(root / "latest.json")
    month = latest["meta"]["snapshot_month"]
    snapshot_json = root / "snapshots" / f"{month}.json"
    snapshot_csv = root / "snapshots" / f"{month}.csv"

    if load_json(root / "latest.json") != validate_snapshot(snapshot_json):
        raise AssertionError("latest.json must match the current monthly JSON snapshot")
    validate_csv(snapshot_csv)

    print(f"Validated AI 500 snapshot {month}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
