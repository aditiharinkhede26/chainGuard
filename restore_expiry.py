import sqlite3

connection = sqlite3.connect("chainguard.db")

connection.execute("""
UPDATE Products
SET expiry_date = '2028-11-20'
WHERE product_id = 'CG-5D35FF6CDD'
""")

connection.commit()
connection.close()

print("Expiry date restored successfully!")