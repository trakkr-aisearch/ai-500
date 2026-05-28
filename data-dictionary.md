# AI 500 Data Dictionary

The AI 500 publishes monthly snapshots of Trakkr's public global AI visibility leaderboard.

## Top-Level Fields

| Field | Type | Description |
|---|---|---|
| `meta` | object | Snapshot provenance, schema version, source URLs, license, and publisher metadata. |
| `rankings` | array | Ordered list of 500 public ranking rows. |

## `meta`

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Dataset schema version. |
| `snapshot_month` | string | Snapshot month in `YYYY-MM` format. |
| `generated_at` | string | UTC timestamp when the repository artifact was generated. |
| `source_url` | string | Branded public rankings API URL used for the snapshot. |
| `status_url` | string | Branded public status endpoint for freshness metadata. |
| `methodology_url` | string | Trakkr public methodology URL. |
| `repository_url` | string | Canonical GitHub repository URL. |
| `row_count` | number | Number of rows in `rankings`. |
| `publisher` | object | Dataset publisher metadata. |
| `license` | object | Data and code license metadata. |
| `source_status` | object | Optional status payload from the public rankings API at generation time. |

## Ranking Row Fields

| Field | Type | Description |
|---|---|---|
| `rank` | number | 1-based global AI visibility rank. |
| `brand_id` | string | Backward-compatible public brand identifier returned by the source API. |
| `brand_name` | string | Display name for the brand. |
| `brand_slug` | string | Lowercase slug derived from the brand display name. |
| `brand_url` | string | Public Trakkr rankings URL for the brand. |
| `score` | number | 0-100 global AI visibility score. |
| `mentions` | number | Recent public mention count in the source leaderboard. |
| `cumulative_mentions` | number | Cumulative public mention count in the source leaderboard. |
| `industries` | number | Count of industries/categories where the brand appears in public ranking data. |
| `change_24h` | number | Short-term rank/score movement reported by the public API. |
| `change_7d` | number | Seven-day rank/score movement reported by the public API. |
| `sector` | string | Public sector grouping. |
| `region` | string | Public region grouping. |
| `company_size` | string | Public company-size grouping. |
| `logo_url` | string/null | Public CDN logo URL when available. |
| `context` | array | Public contextual notes returned by the source API. |

Additional fields may be appended over time. Existing fields are preserved for compatibility.
