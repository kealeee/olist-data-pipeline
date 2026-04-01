import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys
import time
from pathlib import Path
import re

print("🔧 Starting Olist Raw Data Ingestion...\n")

# ====================== DATABASE CONNECTION ======================
POSTGRES_USER = os.getenv("POSTGRES_USER", "").strip()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "").strip()
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost").strip()
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432").strip()
POSTGRES_DB = os.getenv("POSTGRES_DB", "").strip()

print("🔍 Environment Variables Check:")
print(f"   POSTGRES_USER     = {POSTGRES_USER}")
print(f"   POSTGRES_HOST     = {POSTGRES_HOST}")
print(f"   POSTGRES_PORT     = {POSTGRES_PORT}")
print(f"   POSTGRES_DB       = {POSTGRES_DB}")
print(f"   POSTGRES_PASSWORD = {'[SET]' if POSTGRES_PASSWORD else '[NOT SET]'}")

if not POSTGRES_PASSWORD:
    print("\n❌ Error: POSTGRES_PASSWORD is not set!")
    sys.exit(1)

if not all([POSTGRES_USER, POSTGRES_DB]):
    print("\n❌ Error: Missing POSTGRES_USER or POSTGRES_DB!")
    sys.exit(1)

print(f"\n✅ Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...\n")
time.sleep(3)

try:
    engine = create_engine(
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
        pool_pre_ping=True,
        echo=False
    )
    
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()
        print("✅ Successfully connected and 'raw' schema verified!")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# ====================== LOCAL FILE LOADING ======================
data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
data_dir.mkdir(parents=True, exist_ok=True)

csv_files = {
    "olist_customers_dataset.csv": "raw_olist_customers",
    "olist_geolocation_dataset.csv": "raw_olist_geolocation",
    "olist_order_items_dataset.csv": "raw_olist_order_items",
    "olist_order_payments_dataset.csv": "raw_olist_payments",
    "olist_order_reviews_dataset.csv": "raw_olist_reviews",
    "olist_orders_dataset.csv": "raw_olist_orders",
    "olist_products_dataset.csv": "raw_olist_products",
    "olist_sellers_dataset.csv": "raw_olist_sellers",
    "product_category_name_translation.csv": "raw_product_category_translation"
}

for csv_file, table_name in csv_files.items():
    filepath = data_dir / csv_file

    if filepath.exists():
        try:
            print(f"📄 Loading {csv_file} → raw.{table_name}")
            
            # Use 'utf-8-sig' to automatically strip Byte Order Marks (BOM) common in Olist CSVs
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # CRITICAL FIX FOR GITHUB ACTIONS: 
            # 1. Strip spaces 
            # 2. Convert to lowercase 
            # 3. Remove non-ASCII hidden characters that break Postgres lookups
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(r'[^\x00-\x7F]+', '', regex=True)
            )

            df.to_sql(
                name=table_name,
                con=engine,
                schema='raw',
                if_exists='replace',
                index=False,
                chunksize=5000,
                method='multi'
            )
            print(f"✅ Successfully loaded {len(df):,} rows into raw.{table_name}")
        except Exception as e:
            print(f"❌ Error loading {csv_file}: {e}")
    else:
        print(f"⚠️ File not found: {csv_file}, skipped.")

print("\n🎉 Raw data ingestion process finished!")
