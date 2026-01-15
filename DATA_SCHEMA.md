# Data Schema (Google Play Reviews Ingestion)

This project ingests Google Play reviews and stores them in a lightweight relational schema
designed for analysis + future pipeline extensions.

## 1) apps (dimension)
**Primary Key:** `app_id`

| column | type | description |
|---|---|---|
| app_id | TEXT | Google Play package name (e.g., `com.openai.chatgpt`) |
| platform | TEXT | constant: `google_play` |
| created_at | TIMESTAMP | record creation time (optional) |

## 2) app_versions (dimension)
**Primary Key:** `version_id`  
**Unique:** (`app_id`, `version_string`)

| column | type | description |
|---|---|---|
| version_id | INTEGER | surrogate key (autoincrement) |
| app_id | TEXT | FK -> apps.app_id |
| version_string | TEXT | app version string as observed in reviews |
| first_seen_at | TIMESTAMP | first time this version appears (optional) |
| last_seen_at | TIMESTAMP | last time this version appears (optional) |

## 3) reviews (fact)
**Primary Key:** `review_id`  
**Foreign Keys:** `app_id`, `version_id`

| column | type | description |
|---|---|---|
| review_id | TEXT | unique review id (dedup key) |
| app_id | TEXT | FK -> apps.app_id |
| version_id | INTEGER | FK -> app_versions.version_id (nullable) |
| rating | INTEGER | 1–5 |
| review_text | TEXT | raw review text |
| review_time | TIMESTAMP | review created time |
| thumbs_up_count | INTEGER | likes/upvotes (nullable) |
| user_name | TEXT | author name (nullable) |
| reply_content | TEXT | developer reply (nullable) |
| replied_at | TIMESTAMP | developer reply timestamp (nullable) |
| lang | TEXT | ingestion parameter (e.g., `en`) |
| country | TEXT | ingestion parameter (e.g., `us`) |
| ingested_at | TIMESTAMP | pipeline ingestion time |

### Derived columns stored in `reviews` (enriched features)
These are computed downstream and stored as columns for convenience at this stage:

| column | type | description |
|---|---|---|
| review_len | INTEGER | character length of review_text |
| word_count | INTEGER | token/word count |
| sentiment | TEXT | sentiment label (neg/neu/pos) |
| compound | REAL | sentiment score (e.g., VADER compound) |
| hour | INTEGER | 0–23 extracted from review_time |

## Canonical field mapping
The ingestion source may produce slightly different keys; we normalize to canonical names:

- `content` -> `review_text`
- `score` -> `rating`
- `at` -> `review_time`
- `reviewId` -> `review_id` (then stored as `review_id`)
- `userName` -> `user_name`
- `thumbsUpCount` -> `thumbs_up_count`
- `replyContent` -> `reply_content`
- `repliedAt` -> `replied_at`
- `appVersion` -> `app_version`

## Recommended indexes (for DB phase)
- reviews(review_time)
- reviews(version_id)
- reviews(rating)
- reviews(app_id, review_time)
