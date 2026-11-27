import sqlite3

connection = sqlite3.connect("chainguard.db")

connection.execute("""
UPDATE Products
SET expiry_date = '2025-01-01'
WHERE product_id = 'CG-5D35FF6CDD'
""")

connection.commit()
connection.close()

print("Test expiry date updated successfully!")