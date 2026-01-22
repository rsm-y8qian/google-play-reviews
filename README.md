### Google Play Reviews Pipeline

A reproducible, end-to-end data pipeline and lightweight UI for collecting, processing, and validating Google Play app reviews.

This project allows users to paste a Google Play app URL, run the pipeline with one click (or via CLI), and automatically generate raw data, processed datasets, and run-level summaries, all organized by app and execution date.

## Features
1. Human-friendly input: paste a Google Play app URL (no package name needed)

2. Clean data organization:
   - Data separated by app
   - Data partitioned by run timestamp

3. Reproducible pipeline:
   - Fetch → Transform → Validate → Store → Summarize

4. Multiple outputs:
   - Raw CSV
   - Processed Parquet (with CSV fallback)
   - JSON run summary

5. Interactive UI (Streamlit):
   - Start pipeline with one click
   - View logs in real time
   - See where files are saved

## Project Structure

google-play-reviews/
├── app.py                     # Streamlit UI
├── config.yaml                # Pipeline configuration
├── pipelines/
│   └── run_pipeline.py        # Main pipeline entrypoint
├── src/
│   ├── fetch.py               # Fetch reviews from Google Play
│   ├── transform.py           # Data transformations
│   ├── validate.py            # Data validation
│   ├── store.py               # Data persistence (parquet/csv)
│   └── utils.py               # URL parsing & helpers
├── data/
│   ├── raw/
│   │   └── <app_slug>/<run_id>/reviews_raw.csv
│   └── processed/
│       └── <app_slug>/<run_id>/reviews.parquet
├── outputs/
│   └── runs/
│       └── <app_slug>/<run_id>/run_summary.json
├── requirements.txt
└── README.md

## How It Works
## Pipeline Stages

1. Fetch
   - Extract app_id from Google Play URL
   - Download reviews via google-play-scraper
   - Save raw data as CSV

2. Transform
   - Basic cleaning
   - Timestamp normalization
   (Extendable for feature engineering)

3. Validate
   - Check required columns
   - Compute missing ratios
   - Generate structured validation report

4. Store
   - Save processed data as Parquet (preferred)
   - Fallback to CSV if Parquet engine unavailable

5. Summarize
   - Write run-level metadata:
   - counts
   - validation results
   - file paths
   - timestamps

## Option 1: Run with UI (Recommended)
1. Install dependencies
   pip install -r requirements.txt
   pip install streamlit

2. Start the UI
   py -m streamlit run app.py

3. UI Workflow
   - Paste a Google Play app URL
      Example: https://play.google.com/store/apps/details?id=com.openai.chatgpt&hl=en&gl=US
   - Click Start
   - Watch the pipeline logs
   - View the run summary and output file paths

## Option 2: Run from Command Line (CLI)
   - You can also run the pipeline directly without the UI.
    py -m pipelines.run_pipeline \
  --url "https://play.google.com/store/apps/details?id=com.openai.chatgpt&hl=en&gl=US"
   - Optional arguments:
      --batch_limit 1000      # number of reviews to fetch this run
      --config config.yaml    # custom config file

## Output Layout (Example)
data/
├── raw/
│   └── chatgpt/
│       └── 20260122T203155Z/
│           └── reviews_raw.csv
├── processed/
│   └── chatgpt/
│       └── 20260122T203155Z/
│           └── reviews.parquet

outputs/
└── runs/
    └── chatgpt/
        └── 20260122T203155Z/
            └── run_summary.json
# Each run is fully traceable and reproducible.
   
## Configuration
All configurable options live in config.yaml:
paths:
  raw_root: "data/raw"
  processed_root: "data/processed"
  runs_root: "outputs/runs"

fetch:
  lang: "en"
  country: "us"
  sort: "newest"
  batch_limit: 500

validation:
  required_columns:
    - reviewId

store:
  prefer_parquet: true
