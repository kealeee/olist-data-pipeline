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

print(f"\n✅ Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...")
time.sleep(2)

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

    # ✅ NEW: Verify connection by listing tables
    tables_df = pd.read_sql(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'raw' ORDER BY tablename;", 
        engine
    )
    print(f"📋 Current raw schema tables: {len(tables_df)}")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)


# ====================== OLIST CSV FILES MAPPING ======================
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

loaded_tables = []
failed_tables = []

for csv_file, table_name in csv_files.items():
    filepath = data_dir / csv_file

    if filepath.exists():
        try:
            print(f"📄 Loading {csv_file} → raw.{table_name}")
            
            # Read with BOM handling
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            print(f"   📊 Found {len(df):,} rows, {len(df.columns)} columns")
            
            # ✅ FIXED: Clean column names WITHOUT .str.lower()
            # Keep original casing from CSV headers for dbt compatibility
            original_cols = df.columns.tolist()
            print(f"   🔤 Original columns (first 3): {original_cols[:3]}")
            
            df.columns = (
                df.columns
                .str.strip()                    # Remove leading/trailing spaces
                .str.replace(r'^\s+|\s+$', '', regex=True)  # More aggressive space cleaning
                .str.replace(r'[^\w\s]', '', regex=True)    # Remove special chars but keep letters/numbers
            )
            
            cleaned_cols = df.columns.tolist()
            print(f"   ✅ Cleaned columns (first 3): {cleaned_cols[:3]}")
            
            # Verify critical columns exist after cleaning
            if table_name == 'raw_olist_customers':
                if 'customer_id' not in cleaned_cols:
                    print("   ❌ WARNING: 'customer_id' missing after cleaning!")
            
            df.to_sql(
                name=table_name,
                con=engine,
                schema='raw',
                if_exists='replace',  # Drop and recreate each time
                index=False,
                chunksize=5000,
                method='multi'
            )
            
            # ✅ NEW: Verify table creation
            row_count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM raw.{table_name}", engine).iloc[0]['cnt']
            print(f"✅ Loaded {len(df):,} rows → verified {row_count:,} rows in raw.{table_name}")
            loaded_tables.append(table_name)
            
        except Exception as e:
            print(f"❌ Error loading {csv_file}: {e}")
            failed_tables.append(csv_file)
    else:
        print(f"⚠️  File not found: {csv_file} (skipped)")

# ====================== FINAL VERIFICATION ======================
print(f"\n📊 SUMMARY:")
print(f"   ✅ Loaded tables: {len(loaded_tables)}")
for table in loaded_tables:
    print(f"      - raw.{table}")
print(f"   ❌ Failed: {len(failed_tables)}")
if failed_tables:
    print(f"      - {', '.join(failed_tables)}")

# ✅ NEW: Print critical column verification for dbt
print("\n🔍 Verifying dbt-critical columns:")
critical_tables = {
    'raw_olist_customers': ['customer_id'],
    'raw_olist_orders': ['order_id', 'customer_id'],
    'raw_olist_order_items': ['order_id'],
    'raw_olist_products': ['product_id', 'product_category_name'],
    'raw_olist_reviews': ['review_id', 'order_id']
}

with engine.connect() as conn:
    for table_name, cols in critical_tables.items():
        result = conn.execute(
            text(f"""
                SELECT string_agg(column_name, ', ') as columns 
                FROM information_schema.columns 
                WHERE table_schema = 'raw' AND table_name = :table 
                  AND column_name = ANY(string_to_array(:cols, ','))
            """),
            {"table": table_name, "cols": ', '.join(cols)}
        )
        found_cols = result.fetchone()[0] or "NONE"
        status = "✅" if found_cols != "NONE" else "❌"
        print(f"   {status} {table_name}: {found_cols}")

print("\n🎉 Raw data ingestion process finished!")
engine.dispose()
