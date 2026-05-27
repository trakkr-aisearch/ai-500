# Shipped

Published repository: https://github.com/trakkr-aisearch/ai-500

Publication status: published to GitHub after the empty public repository was created in the `trakkr-aisearch` organization.

## First Snapshot

The first snapshot ran successfully for `2026-05`.

- `snapshots/2026-05.json` contains the full public global rankings API response.
- `snapshots/2026-05.csv` contains 500 flat ranking rows.
- `latest.json` matches `snapshots/2026-05.json`.
- `CHANGELOG.md` includes the `2026-05` snapshot entry.
- Local validation confirmed valid JSON, 500 CSV rows, and Google as the top-ranked brand in this snapshot.

## Sensitivity Flags

None. The repository commits only data returned by the public global rankings API and does not include customer-level data, raw prompts, raw model responses, private scoring weights, query-volume detail, product pricing, or internal product analytics.

## Next Monthly Run

The GitHub Actions workflow runs on the first day of each month at 09:00 UTC. The next scheduled run is `2026-06-01 09:00 UTC`.

On each run, `scripts/snapshot.py` will fetch the public rankings API, write the current `YYYY-MM` JSON and CSV files, refresh `latest.json`, update `CHANGELOG.md`, and commit and push the result if anything changed.
