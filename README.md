# Google Play Reviews Pipeline (ChatGPT)

This repo ingests Google Play reviews for the ChatGPT app, performs schema alignment
and feature engineering, and produces analysis-ready datasets for downstream
exploration and storage.

## Project Structure
- `data/raw/`: raw ingested review data (CSV)
- `data/processed/`: schema-aligned and feature-enriched datasets (CSV)
- `notebooks/`: EDA, validation, and data-layer notebooks
- `DATA_SCHEMA.md`: canonical schema definition

## Data Source
Reviews are collected via `google-play-scraper` using the package id:
- `com.openai.chatgpt`

## Outputs
- `data/raw/play_reviews_ingested.csv`: raw ingested data (deduplicated by `review_id`)
- `data/processed/reviews_enriched.csv`: schema-aligned and feature-engineered dataset
- `data/processed/reviews_merged.csv`: analysis-ready dataset created by joining raw and processed data on `review_id`

## How to Run
1. Create environment and install dependencies:
   - `pip install -r requirements.txt`

2. Run EDA and validation:
   - `notebooks/01_eda_and_validation.ipynb`

3. Build lightweight relational data layer:
   - `notebooks/02_data_layer.ipynb`

4. Confirm processed output exists:
   - `data/processed/reviews_enriched.csv`

## Notes / Next Steps
- Optionally persist the relational layer using SQLite or DuckDB
- Add loading scripts under `src/` to support repeatable pipeline runs

