# The AI 500

[![Top brand](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Ftrakkr-aisearch%2Fai-500%2Fmain%2Flatest.json&query=%24.rankings%5B0%5D.brand_id&label=top%20brand&color=0366d6)](https://github.com/trakkr-aisearch/ai-500/blob/main/latest.json)
[![Data updated](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Franking-api-830752870576.us-east1.run.app%2Fapi%2Fstatus&query=%24.data_updated_at&label=data%20updated&color=2ea44f)](https://ranking-api-830752870576.us-east1.run.app/api/status)
[![License: MIT and CC BY 4.0](https://img.shields.io/badge/license-MIT%20%2B%20CC%20BY%204.0-lightgrey)](LICENSE)

The AI 500 is a public monthly dataset of the top 500 rows returned by Trakkr's global AI visibility rankings API. Each snapshot records how brands appear in Trakkr's public AI visibility leaderboard, including rank, brand identifier, visibility score, mentions, industry breadth, short-term rank movement, sector, region, company size, logo URL, and any public contextual notes returned by the API.

## Data Files

- `latest.json` - copy of the most recent monthly JSON snapshot.
- `snapshots/YYYY-MM.json` - full public API response for that month.
- `snapshots/YYYY-MM.csv` - flat ranking table, one row per brand.
- `CHANGELOG.md` - one-line index of monthly snapshots.

## How to Use It

Python:

```python
import requests

url = "https://raw.githubusercontent.com/trakkr-aisearch/ai-500/main/latest.json"
data = requests.get(url, timeout=30).json()

top_10 = data["rankings"][:10]
for row in top_10:
    print(row["rank"], row["brand_id"], row["score"])
```

JavaScript:

```js
const url = "https://raw.githubusercontent.com/trakkr-aisearch/ai-500/main/latest.json";
const response = await fetch(url);
const data = await response.json();

console.table(
  data.rankings.slice(0, 10).map(({ rank, brand_id, score, sector }) => ({
    rank,
    brand: brand_id,
    score,
    sector,
  })),
);
```

Additional Python snippets are in [`examples/`](examples/).

## Methodology

Trakkr's public methodology describes the AI 500 as a reference layer for AI-driven brand discovery. The rankings are based on recommendation-style prompts across leading AI assistants including ChatGPT, Claude, Gemini, and Perplexity. Public methodology notes that visibility rewards answer position, repeated appearance across relevant prompts, and breadth across industries; product mentions may be mapped to parent brands with AI-assisted classification and manual overrides.

This repository publishes monthly snapshots of the public API output. It does not publish prompt text, customer-level data, raw model responses, private scoring weights, or Trakkr product analytics. See [`methodology.md`](methodology.md) and the current public methodology at [trakkr.ai/rankings/methodology](https://trakkr.ai/rankings/methodology).

## License

Code in this repository is released under the MIT License. Dataset files in `snapshots/`, `latest.json`, and `CHANGELOG.md` are released under the Creative Commons Attribution 4.0 International License (CC BY 4.0). Attribution should name Trakkr and link to this repository.

## Citation

```bibtex
@dataset{trakkr_ai500_2026,
  title = {The AI 500: Monthly Public Snapshots of Trakkr Global AI Visibility Rankings},
  author = {{Trakkr}},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/trakkr-aisearch/ai-500},
  note = {Monthly snapshots of the public Trakkr global AI visibility rankings}
}
```
