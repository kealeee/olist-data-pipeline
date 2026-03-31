import pandas as pd
from sqlalchemy import create_engine, text  # Added 'text' for raw SQL execution
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("🔧 Starting Olist Raw Data Ingestion...\n")

# Read connection settings from .env
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not POSTGRES_PASSWORD:
    print("❌ Error: POSTGRES_PASSWORD not found in .env file")
    sys.exit(1)

try:
    engine = create_engine(
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
        pool_pre_ping=True
    )
    
    # --- NEW: Ensure the 'raw' schema exists before loading ---
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()  # Required for SQLAlchemy 2.0+
        print("✅ Successfully connected to PostgreSQL and verified 'raw' schema!")
    # ----------------------------------------------------------

except Exception as e:
    print(f"❌ Failed to connect to PostgreSQL: {e}")
    print("Please check your .env file and make sure PostgreSQL is running.")
    sys.exit(1)

# Rest of the script (data directory + loading logic)
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

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

for csv_file, table_name in csv_files.items():
    filepath = os.path.join(data_dir, csv_file)
    if os.path.exists(filepath):
        try:
            print(f"📄 Loading {csv_file} into raw.{table_name} ...")
            # Using 'latin1' often helps with Brazilian special characters in this dataset
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
            print(f"✅ Successfully loaded {len(df):,} rows into raw.{table_name}")
        except Exception as e:
            print(f"❌ Error loading {csv_file}: {e}")
    else:
        print(f"⚠️ File not found: {filepath}")

print("\n🎉 Raw data ingestion process finished!")
