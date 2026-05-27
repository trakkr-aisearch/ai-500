# %%
"""Compute month-over-month rank changes between the two latest snapshots."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path.cwd()
if not (ROOT / "snapshots").exists():
    ROOT = ROOT.parent

snapshot_paths = sorted((ROOT / "snapshots").glob("*.json"))
if len(snapshot_paths) < 2:
    print("Need at least two monthly snapshots to compute month-over-month changes.")
    raise SystemExit(0)

previous_path, current_path = snapshot_paths[-2:]
with previous_path.open(encoding="utf-8") as handle:
    previous_data = json.load(handle)
with current_path.open(encoding="utf-8") as handle:
    current_data = json.load(handle)

previous = pd.DataFrame(previous_data["rankings"])
current = pd.DataFrame(current_data["rankings"])

changes = current[["brand_id", "rank"]].merge(
    previous[["brand_id", "rank"]],
    on="brand_id",
    suffixes=("_current", "_previous"),
)
changes["rank_change"] = changes["rank_previous"] - changes["rank_current"]

print(f"{previous_path.stem} to {current_path.stem}")
print(changes.sort_values("rank_change", ascending=False).head(20))
