# %%
"""Plot the top 20 brands by AI visibility score."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path.cwd()
if not (ROOT / "latest.json").exists():
    ROOT = ROOT.parent

with (ROOT / "latest.json").open(encoding="utf-8") as handle:
    data = json.load(handle)

df = pd.DataFrame(data["rankings"])
top_20 = df.nsmallest(20, "rank").sort_values("score")

ax = top_20.plot.barh(x="brand_id", y="score", legend=False, figsize=(8, 6))
ax.set_xlabel("AI visibility score")
ax.set_ylabel("")
ax.set_title("AI 500 top 20 brands")
plt.tight_layout()
plt.show()
