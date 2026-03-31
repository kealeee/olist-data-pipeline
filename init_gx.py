import great_expectations as gx
import os

# Define where you want the GX configuration to live
project_dir = "./"

try:
    # This creates the /gx (or /great_expectations) folder structure
    context = gx.get_context(project_root_dir=project_dir)
    
    print("✅ Great Expectations Initialized!")
    print(f"Directory created at: {os.path.abspath(os.path.join(project_dir, 'gx'))}")
    print("\nNext step: Run your 'setup_gx.py' to connect your Postgres database.")

except Exception as e:
    print(f"❌ Initialization failed: {e}")
