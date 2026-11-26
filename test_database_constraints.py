import sqlite3

connection = sqlite3.connect("chainguard.db")

connection.execute("PRAGMA foreign_keys = ON")


# TEST 1: Duplicate Email

try:
    connection.execute("""
    INSERT INTO Manufacturers
    (company_name, email, password_hash)
    VALUES ('Test Company', 'abc@example.com', 'test')
    """)

    print("Duplicate email test failed!")

except sqlite3.IntegrityError:
    connection.rollback()
    print("Test 1 passed: Duplicate email rejected!")


# TEST 2: Missing Required Value

try:
    connection.execute("""
    INSERT INTO Products
    (product_id, product_name, brand, manufacturer_id)
    VALUES ('TEST001', NULL, 'Test Brand', 1)
    """)

    print("NOT NULL test failed!")

except sqlite3.IntegrityError:
    connection.rollback()
    print("Test 2 passed: Missing product name rejected!")


# TEST 3: Invalid Manufacturer ID

try:
    connection.execute("""
    INSERT INTO Products
    (product_id, product_name, brand, manufacturer_id)
    VALUES ('TEST002', 'Test Product', 'Test Brand', 999)
    """)

    print("Foreign Key test failed!")

except sqlite3.IntegrityError:
    connection.rollback()
    print("Test 3 passed: Invalid manufacturer ID rejected!")


connection.close()