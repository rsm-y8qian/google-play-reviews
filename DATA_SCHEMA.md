# Data Schema

This project uses a simple, reproducible data pipeline with explicit “raw” and “processed” layers.  
Tables are linked via a shared primary key: `review_id`.

## Data Flow

1. **Ingestion** → `data/raw/play_reviews_ingested.csv`  
2. **Processing / Enrichment** → `data/processed/reviews_enriched.csv`  
3. **Analysis-ready merge (derived)** → `data/processed/reviews_merged.csv` (optional)

- **Join key / Primary key:** `review_id`
- `reviews_merged.csv` is a convenience dataset created by joining raw + enriched features on `review_id`.

---

## Table: `raw.play_reviews`  
**File:** `data/raw/play_reviews_ingested.csv`  
**Grain:** 1 row per Google Play review (as ingested)  
**Primary Key:** `review_id`

| Column | Type | Description |
|---|---|---|
| review_id | string | Unique review identifier (primary key) |
| user_name | string | Reviewer display name |
| user_image_url | string | Reviewer avatar URL |
| review_text | string | Review text content |
| rating | int | Star rating (1–5) |
| thumbs_up | int | Helpful/upvote count at time of scrape |
| review_created_version | string | App version recorded on review creation (if available) |
| review_time | string | Review timestamp (string in CSV; parseable to datetime) |
| reply_text | string/nullable | Developer reply text (nullable) |
| reply_time | string/nullable | Developer reply time (nullable) |
| app_version | string | App version field captured during ingestion (if available) |

**Notes**
- Some reply-related columns may be missing (null) when no developer response exists.
- Timestamp fields are stored as strings in CSV and can be parsed to datetime in downstream analysis.

---

## Table: `processed.reviews_enriched`  
**File:** `data/processed/reviews_enriched.csv`  
**Grain:** 1 row per review (same `review_id` key), enriched with derived features  
**Primary Key:** `review_id`  
**Upstream:** derived from `raw.play_reviews`

| Column | Type | Description |
|---|---|---|
| review_id | string | Unique review identifier (primary key) |
| user_name | string | Reviewer display name (carried from raw) |
| user_image_url | string | Reviewer avatar URL (carried from raw) |
| review_text | string | Review text content (carried from raw) |
| rating | int | Star rating (1–5) |
| thumbs_up_count | int | Helpful/upvote count (standardized naming) |
| app_version | string | App version (standardized naming) |
| review_time | string | Review timestamp (string in CSV; parseable to datetime) |
| reply_content | string/nullable | Developer reply text (standardized naming; nullable) |
| replied_at | string/nullable | Developer reply timestamp (standardized naming; nullable) |
| review_len | int | Character length of `review_text` |
| word_count | int | Word count of `review_text` |
| sentiment | float/nullable | Sentiment score (derived from review text; nullable if not computed) |

**Notes**
- This dataset standardizes a few fields compared to raw (e.g., `thumbs_up_count`, `reply_content`, `replied_at`).
- Derived features (`review_len`, `word_count`, `sentiment`) support downstream EDA/modeling.

---

## Table: `processed.reviews_merged` (optional, derived)
**File:** `data/processed/reviews_merged.csv`  
**Grain:** 1 row per review  
**Primary Key:** `review_id`  
**Definition:** left-join `raw.play_reviews` with selected enriched fields from `processed.reviews_enriched` on `review_id`.

| Column Group | Description |
|---|---|
| Raw columns | Full set of ingested fields from `raw.play_reviews` |
| Enriched columns | `thumbs_up_count`, `reply_content`, `replied_at`, `review_len`, `word_count`, `sentiment` |

**Purpose**
- Provides an analysis-ready “single table” view for convenience.
- Can be regenerated anytime from raw + processed sources; it is not required as a source-of-truth artifact.

---

## Relational Layer (Lightweight)

Even without a database, the project treats datasets as relational tables:

- `raw.play_reviews` (source-of-truth)
- `processed.reviews_enriched` (deterministic transformations + derived features)
- Relationship: `raw.play_reviews.review_id` ↔ `processed.reviews_enriched.review_id`

Downstream analysis should reference the processed layer (or the merged view) to ensure consistent feature definitions.

