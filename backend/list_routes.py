#!/usr/bin/env python3
"""
Script to list all registered Flask routes.
"""

# Import the app from app.py
from app import app

# Print all registered routes
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule} - {', '.join(rule.methods)}")

# Specifically check for batch-entities routes
print("\nBatch entity routes:")
batch_routes = [rule for rule in app.url_map.iter_rules() if "batch-entities" in str(rule)]
if batch_routes:
    for rule in batch_routes:
        print(f"{rule} - {', '.join(rule.methods)}")
else:
    print("No batch-entities routes found!") 