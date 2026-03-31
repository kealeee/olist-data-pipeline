import great_expectations as gx
from great_expectations.expectations import ExpectColumnValuesToBeBetween, ExpectColumnValuesToNotBeNull

context = gx.get_context()

# 1. DELETE the old suite to clear errors
try:
    context.suites.delete("olist_quality_suite")
    print("🗑️ Old suite cleared.")
except:
    pass

# 2. Create a FRESH suite
suite = context.suites.add(gx.ExpectationSuite(name="olist_quality_suite"))

# 3. Add only the CLEAN rules (matching your SQL columns)
suite.add_expectation(ExpectColumnValuesToNotBeNull(column="order_id"))
suite.add_expectation(ExpectColumnValuesToBeBetween(column="price", min_value=0.01))

# 4. Get the asset and run validation
asset = context.data_sources.get("olist_datasource").get_asset("fact_sales_asset")

try:
    batch_definition = asset.add_batch_definition_whole_table(name="all_data_batch")
except:
    batch_definition = asset.get_batch_definition(name="all_data_batch")

validation_definition = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="olist_validation_definition", data=batch_definition, suite=suite)
)

print("🚀 Running final check...")
results = validation_definition.run()

context.build_data_docs()
context.open_data_docs()

if results.success:
    print("✅ SUCCESS! Your data is officially 'Award-Winning' quality.")
else:
    print("❌ Still failing? Check the 'Observed Value' in your browser tab.")
