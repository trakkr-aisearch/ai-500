# %%
"""Filter the latest snapshot by sector."""

import json
from pathlib import Path

import pandas as pd


SECTOR = "Platform"

ROOT = Path.cwd()
if not (ROOT / "latest.json").exists():
    ROOT = ROOT.parent

with (ROOT / "latest.json").open(encoding="utf-8") as handle:
    data = json.load(handle)

df = pd.DataFrame(data["rankings"])
sector_df = df[df["sector"].eq(SECTOR)].sort_values("rank")

print(sector_df[["rank", "brand_name", "score", "mentions", "industries"]].head(25))
