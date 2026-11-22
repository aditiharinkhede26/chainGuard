import sqlite3

# Connect to the database
connection = sqlite3.connect("chainguard.db")

print("Database connected successfully!")

# Create Products table
connection.execute("""
CREATE TABLE IF NOT EXISTS Products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    manufacturing_date TEXT,
    expiry_date TEXT,
    status TEXT DEFAULT 'active'
)
""")

connection.commit()

print("Products table created successfully!")

# Check Products table structure
result = connection.execute("PRAGMA table_info(Products)")

for column in result:
    print(column)


# Fetch all products

result = connection.execute("SELECT * FROM Products")

for product in result:
    print(product)

connection.close()

print("Database connection closed.")