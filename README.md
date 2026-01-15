# Google Play Reviews Pipeline (ChatGPT)

This repo ingests Google Play reviews for the ChatGPT app, performs schema alignment and feature engineering, and produces analysis-ready datasets for downstream exploration and storage.

## Project Structure
- `data/raw/`: ingested raw review data (CSV)
- `data/processed/`: canonical + enriched datasets (CSV)
- `notebooks/`: EDA + validation notebook(s)
- `DATA_SCHEMA.md`: canonical schema definition

## Data Source
Reviews are collected via `google-play-scraper` using the package id:
- `com.openai.chatgpt`

## Outputs
- `data/raw/play_reviews_ingested.csv`: raw ingested data
- `data/processed/reviews_enriched.csv`: schema-aligned + engineered dataset

## How to Run
1. Create environment and install dependencies:
   - `pip install -r requirements.txt`
2. Run the notebook:
   - `notebooks/01_eda_and_validation.ipynb`
3. Confirm processed output exists:
   - `data/processed/reviews_enriched.csv`

## Notes / Next Steps
- Implement a lightweight relational storage layer (SQLite/DuckDB) based on `DATA_SCHEMA.md`
- Add loading scripts under `src/` to support repeatable pipeline runs
