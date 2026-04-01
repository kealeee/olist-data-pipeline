import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys
import time
import requests
from pathlib import Path

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

# ====================== DATA DOWNLOAD & LOADING ======================
data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
data_dir.mkdir(parents=True, exist_ok=True)

# Public reliable URLs (from a well-known open repo)
DATA_URLS = {
    "olist_customers_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_orders_dataset.csv",
    "olist_products_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_products_dataset.csv",
    "olist_sellers_dataset.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/olist_sellers_dataset.csv",
    "product_category_name_translation.csv": "https://raw.githubusercontent.com/ozlerhakan/olist/master/product_category_name_translation.csv",
}

csv_files = {
    "olist_customers_dataset.csv": "raw_olist_customers",
    "olist_geolocation_dataset.csv": "raw_olist_geolocation",
    "olist_order_items_dataset.csv": "raw_olist_order_items",
    "olist_order_payments_dataset.csv": "raw_olist_order_payments",
    "olist_order_reviews_dataset.csv": "raw_olist_order_reviews",
    "olist_orders_dataset.csv": "raw_olist_orders",
    "olist_products_dataset.csv": "raw_olist_products",
    "olist_sellers_dataset.csv": "raw_olist_sellers",
    "product_category_name_translation.csv": "raw_product_category_translation"
}


def download_file(url: str, filepath: Path) -> bool:
    if filepath.exists():
        print(f"✅ Using cached file: {filepath.name}")
        return True

    print(f"📥 Downloading {filepath.name}...")
    try:
        response = requests.get(url, stream=True, timeout=90)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded {filepath.name} successfully")
        return True
    except Exception as e:
        print(f"❌ Download failed for {filepath.name}: {e}")
        return False


# Main loading loop
for csv_file, table_name in csv_files.items():
    filepath = data_dir / csv_file

    # Download if missing
    if not filepath.exists():
        url = DATA_URLS.get(csv_file)
        if url:
            success = download_file(url, filepath)
            if not success:
                print(f"⚠️ Skipping {csv_file} - download failed")
                continue
        else:
            print(f"⚠️ No URL configured for {csv_file}")
            continue

    # Load into database
    if filepath.exists():
        try:
            print(f"📄 Loading {csv_file} → raw.{table_name}")
            df = pd.read_csv(filepath, encoding='utf-8')
            df.to_sql(
                name=table_name,
                con=engine,
                schema='raw',
                if_exists='replace',
                index=False,
                chunksize=5000,
                method='multi'
            )
            print(f"✅ Loaded {len(df):,} rows into raw.{table_name}")
        except Exception as e:
            print(f"❌ Error loading {csv_file}: {e}")
    else:
        print(f"⚠️ File not available: {csv_file}")

print("\n🎉 Raw data ingestion process finished!")