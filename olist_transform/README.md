🚀 Getting Started
1. Prerequisites
Ensure you have a PostgreSQL instance running and a virtual environment active.

bash
pip install -r requirements.txt


2. Ingestion & Transformation

bash
python scripts/load_raw.py
dbt deps
dbt run --full-refresh


3. Automated Quality Gate (The "Flex")
To ensure data integrity before analysis, run the triple-asset validation:

bash
python run_quality_check.py


This will automatically open the GX Data Docs in your browser showing the status of 45+ business logic checks.
