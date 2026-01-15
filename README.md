# Google Play Reviews Pipeline (ChatGPT)

This repo ingests Google Play reviews for the ChatGPT app, performs schema alignment and feature engineering, and produces analysis-ready datasets for downstream exploration and storage.

## Project Structure
- `data/raw/`: raw ingested review data (CSV)
- `data/processed/`: schema-aligned and feature-enriched datasets (CSV)
- `notebooks/`: EDA and validation notebooks
- `DATA_SCHEMA.md`: canonical schema definition

## Data Source
Reviews are collected via `google-play-scraper` using the package id:
- `com.openai.chatgpt`

## Outputs
- `data/raw/play_reviews_ingested.csv`: raw ingested data (deduplicated by `review_id`)
- `data/processed/reviews_enriched.csv`: schema-aligned and feature-engineered dataset

## How to Run
1. Create environment and install dependencies:
   - `pip install -r requirements.txt`
2. Run the notebook to perform ingestion, schema alignment, feature engineering, and analysis:
   - `notebooks/01_eda_and_validation.ipynb`
3. Confirm processed output exists:
   - `data/processed/reviews_enriched.csv`

## Notes / Next Steps
- Implement a lightweight relational storage layer (SQLite/DuckDB) based on `DATA_SCHEMA.md`
- Add loading scripts under `src/` to support repeatable pipeline runs
