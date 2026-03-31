import os
import great_expectations as gx
from dotenv import load_dotenv

load_dotenv()

# 1. Build connection string
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

# 2. Get context
context = gx.get_context()

try:
    # 3. Connect Datasource
    datasource = context.data_sources.add_or_update_postgres(
        name="olist_datasource", 
        connection_string=connection_string
    )
    
    # 4. Add Assets for Sales, Geography, and Reviews
    datasource.add_table_asset(
        name="fact_sales_asset", 
        table_name="fact_sales",
        schema_name="analytics"
    )
    
    datasource.add_table_asset(
        name="dim_geo_asset", 
        table_name="dim_geography",
        schema_name="analytics"
    )

    # NEW: Add the Reviews asset
    datasource.add_table_asset(
        name="reviews_asset", 
        table_name="stg_order_reviews", 
        schema_name="analytics" 
    )
    
    # 5. Get or Create Suites for all three
    # Sales Suite
    try:
        sales_suite = context.suites.get(name="olist_quality_suite")
    except:
        sales_suite = context.suites.add(gx.ExpectationSuite(name="olist_quality_suite"))

    # Geography Suite
    try:
        geo_suite = context.suites.get(name="geo_quality_suite")
    except:
        geo_suite = context.suites.add(gx.ExpectationSuite(name="geo_quality_suite"))

    # NEW: Reviews Suite
    try:
        reviews_suite = context.suites.get(name="reviews_quality_suite")
    except:
        reviews_suite = context.suites.add(gx.ExpectationSuite(name="reviews_quality_suite"))

    print("✅ Fact, Geo, and Review assets synchronized in Great Expectations!")

except Exception as e:
    print(f"❌ Error during setup: {e}")
