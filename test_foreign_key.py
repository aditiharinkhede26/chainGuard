import sqlite3

connection = sqlite3.connect("chainguard.db")

connection.execute("PRAGMA foreign_keys = ON")

try:
    connection.execute("""
    INSERT INTO Products
    (product_id, product_name, brand, manufacturer_id)
    VALUES ('TEST999', 'Test Product', 'Test Brand', 999)
    """)

    connection.commit()
    print("Insert succeeded")

except sqlite3.IntegrityError as e:
    connection.rollback()
    print("Foreign Key test passed:", e)

connection.close()