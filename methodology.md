# Methodology

This document summarizes only the public methodology Trakkr currently describes for The AI 500. For the current canonical methodology, see [trakkr.ai/rankings/methodology](https://trakkr.ai/rankings/methodology).

## Scope

The AI 500 is a public ranking of brand visibility in AI-assisted discovery. This repository snapshots the global top 500 rows exposed by the public rankings API once per month.

## Data Collection

Trakkr publicly describes the rankings as based on recommendation-style prompts run across leading AI assistants, including ChatGPT, Claude, Gemini, and Perplexity. The goal is to measure which brands assistants surface when users ask for recommendations in a category.

## Visibility Score

The public methodology says the visibility score rewards three high-level signals:

- Position: whether a brand appears near the top of an answer.
- Frequency: whether a brand appears consistently across relevant prompts.
- Breadth: whether a brand appears across multiple relevant industries.

Trakkr's public methodology also states that quadratic scaling with logarithmic compression is used so very large outliers do not flatten the rest of the ranking set. This repository does not publish private scoring weights, prompt text, or raw model responses.

## Brand Mapping

The public methodology says product mentions can roll up to parent brands through AI-assisted classification with manual overrides. This allows a brand to receive credit when an assistant mentions a flagship product rather than the parent company name directly.

## Snapshot Fields

Each ranking row is published as returned by the public API. Current fields include:

- `rank`
- `brand_id`
- `brand_name`
- `brand_slug`
- `brand_url`
- `score`
- `mentions`
- `cumulative_mentions`
- `industries`
- `change_24h`
- `change_7d`
- `sector`
- `region`
- `company_size`
- `logo_url`
- `context`

Monthly JSON snapshots also include top-level `meta` provenance with schema version, snapshot month, generation time, source URLs, methodology URL, publisher, and license metadata. Fields may change if the public API evolves. Monthly JSON snapshots preserve the full rankings API response for that month; CSV snapshots flatten ranking rows for analysis.

See [`data-dictionary.md`](data-dictionary.md) for the current field reference.
