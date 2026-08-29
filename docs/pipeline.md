# Collection and intelligence pipeline

Each enabled source is collected concurrently with HTTPX. Failures are returned independently so one unavailable publisher cannot fail the entire run. RSS and Atom entries are normalized into a common model: title, canonical URL, author, excerpt, publication timestamp and categories.

Tracking parameters and fragments are removed before the database uniqueness check. Publisher HTML in excerpts is reduced to plain text. Dates are normalized to UTC.

## Story grouping

NewsPulse compares significant normalized title tokens using Jaccard similarity. Related titles over the configured threshold share a story cluster. This deterministic method is fast, inspectable and requires no paid AI service. A production evolution could combine it with embeddings and named-entity extraction.

## Trend scoring

The 0–100 score combines:

- recency with exponential decay;
- number of independent sources;
- total coverage volume.

Source diversity receives more weight than raw volume so a single prolific publisher cannot dominate the ranking. Coverage timelines establish publication order only; they do not claim that one publisher copied another.

