import great_expectations as gx
from great_expectations.expectations import (
    ExpectColumnValuesToBeBetween, 
    ExpectColumnValuesToNotBeNull, 
    ExpectColumnValuesToBeInSet
)

# 1. Initialize the Context
context = gx.get_context()

# --- 🎯 SECTION A: FACT SALES VALIDATION ---
# Logic: Ensure core transaction data is clean for revenue reporting
sales_suite = context.suites.get(name="olist_quality_suite")
sales_asset = context.data_sources.get("olist_datasource").get_asset("fact_sales_asset")

sales_suite.add_expectation(ExpectColumnValuesToNotBeNull(column="order_id"))
sales_suite.add_expectation(ExpectColumnValuesToBeBetween(column="price", min_value=0.01))

try:
    sales_batch = sales_asset.add_batch_definition_whole_table(name="all_sales_batch")
except:
    sales_batch = sales_asset.get_batch_definition(name="all_sales_batch")

sales_val_def = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="olist_sales_validation", data=sales_batch, suite=sales_suite)
)


# --- 🎯 SECTION B: DIM GEOGRAPHY VALIDATION ---
# Logic: Validate the custom-engineered Brazilian Macro-Regions
geo_suite = context.suites.get(name="geo_quality_suite")
geo_asset = context.data_sources.get("olist_datasource").get_asset("dim_geo_asset")

geo_suite.add_expectation(ExpectColumnValuesToBeInSet(
    column="macro_region", 
    value_set=['North', 'Northeast', 'Central-West', 'Southeast', 'South']
))

try:
    geo_batch = geo_asset.add_batch_definition_whole_table(name="all_geo_batch")
except:
    geo_batch = geo_asset.get_batch_definition(name="all_geo_batch")

geo_val_def = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="olist_geo_validation", data=geo_batch, suite=geo_suite)
)


# --- 🎯 SECTION C: ORDER REVIEWS VALIDATION (NEW AWARD FLEX) ---
# Logic: Ensure customer satisfaction data is accurate for strategic analysis
reviews_suite = context.suites.get(name="reviews_quality_suite")
reviews_asset = context.data_sources.get("olist_datasource").get_asset("reviews_asset")

reviews_suite.add_expectation(ExpectColumnValuesToBeBetween(
    column="review_score", min_value=1, max_value=5
))

try:
    reviews_batch = reviews_asset.add_batch_definition_whole_table(name="all_reviews_batch")
except:
    reviews_batch = reviews_asset.get_batch_definition(name="all_reviews_batch")

reviews_val_def = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="olist_reviews_validation", data=reviews_batch, suite=reviews_suite)
)


# --- 🚀 SECTION D: EXECUTION & AUTOMATED REPORTING ---
print("🚀 Running Triple-Asset Quality Checks: Sales + Geography + Reviews...")
sales_results = sales_val_def.run()
geo_results = geo_val_def.run()
reviews_results = reviews_val_def.run()

# Build and Open the "Award-Winning" Data Docs Dashboard
context.build_data_docs()
context.open_data_docs()

# Final Console Feedback
if sales_results.success and geo_results.success and reviews_results.success:
    print("✅ PASS: All production assets meet quality standards.")
else:
    print("❌ FAIL: Quality issues detected. Check Data Docs for details.")
