import sqlite3

# Connect to the database
connection = sqlite3.connect("chainguard.db")

# Enable Foreign Key support
connection.execute("PRAGMA foreign_keys = ON")


print("Database connected successfully!")


# ==========================================
# STEP 1: CREATE MANUFACTURERS TABLE
# ==========================================

connection.execute("""
CREATE TABLE IF NOT EXISTS Manufacturers (
    manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    address TEXT,
    registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'Pending'
)
""")

connection.commit()

print("Manufacturers table created successfully!")


# ==========================================
# STEP 2: INSERT SAMPLE MANUFACTURER
# ==========================================

connection.execute("""
INSERT OR IGNORE INTO Manufacturers
(company_name, email, password_hash, address)
VALUES (?, ?, ?, ?)
""", (
    "ABC Cosmetics",
    "abc@example.com",
    "LEGACY_SAMPLE_NO_LOGIN",
    "Bhopal, India"
))

connection.commit()

print("Sample manufacturer inserted successfully!")
 # Insert second sample manufacturer
connection.execute("""
INSERT OR IGNORE INTO Manufacturers
(company_name, email, password_hash, address)
VALUES (?, ?, ?, ?)
""", (
    "GlowCare Pvt Ltd",
    "glowcare@example.com",
    "DEMO_ONLY_NOT_FOR_LOGIN",
    "Indore, India"
))

connection.commit()

print("Second manufacturer inserted successfully!")


# ==========================================
# STEP 3: CHECK PRODUCTS TABLE
# ==========================================

table_exists = connection.execute("""
SELECT name FROM sqlite_master
WHERE type = 'table' AND name = 'Products'
""").fetchone()


# ==========================================
# STEP 4: CREATE OR MIGRATE PRODUCTS TABLE
# ==========================================

if table_exists is None:

    # Create new Products table
    connection.execute("""
    CREATE TABLE Products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        manufacturer_id INTEGER NOT NULL,
        manufacturing_date TEXT,
        expiry_date TEXT,
        status TEXT DEFAULT 'active',

        FOREIGN KEY (manufacturer_id)
        REFERENCES Manufacturers(manufacturer_id)
    )
    """)

    connection.commit()

    print("New Products table created successfully!")


else:

    # Check current Products table columns
    columns = connection.execute(
        "PRAGMA table_info(Products)"
    ).fetchall()

    column_names = [column[1] for column in columns]


    if "manufacturer" in column_names:

        print("Old Products table detected. Migration required.")

        try:

            connection.execute("BEGIN")

            # Step 1: Check whether all existing manufacturers match
            # with registered manufacturers

            unmatched = connection.execute("""
            SELECT COUNT(*)
            FROM Products p
            LEFT JOIN Manufacturers m
            ON p.manufacturer = m.company_name
            WHERE m.manufacturer_id IS NULL
            """).fetchone()[0]

            if unmatched > 0:
                raise ValueError(
                    f"{unmatched} products have no matching manufacturer. "
                    "Migration stopped to prevent data loss."
                )


            # Step 2: Create temporary Products table

            connection.execute("""
            DROP TABLE IF EXISTS Products_new
            """)

            connection.execute("""
            CREATE TABLE Products_new (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                brand TEXT NOT NULL,
                manufacturer_id INTEGER NOT NULL,
                manufacturing_date TEXT,
                expiry_date TEXT,
                status TEXT DEFAULT 'active',

                FOREIGN KEY (manufacturer_id)
                REFERENCES Manufacturers(manufacturer_id)
            )
            """)

            print("Temporary Products table created successfully!")


            # Step 3: Transfer existing products

            connection.execute("""
            INSERT INTO Products_new (
                product_id,
                product_name,
                brand,
                manufacturer_id,
                manufacturing_date,
                expiry_date,
                status
            )

            SELECT
                p.product_id,
                p.product_name,
                p.brand,
                m.manufacturer_id,
                p.manufacturing_date,
                p.expiry_date,
                p.status

            FROM Products p

            JOIN Manufacturers m
            ON p.manufacturer = m.company_name
            """)

            print("Existing products transferred successfully!")


            # Step 4: Delete old Products table

            connection.execute("DROP TABLE Products")

            # Step 5: Rename temporary table

            connection.execute("""
            ALTER TABLE Products_new
            RENAME TO Products
            """)

            connection.commit()

            print("Products table migrated successfully!")


        except Exception as error:

            connection.rollback()

            print("Migration failed:", error)


    elif "manufacturer_id" in column_names:

        print("Products table is already migrated.")


    else:

        print("Unexpected Products table structure!")

       # Insert a new product

connection.execute("""
INSERT OR IGNORE INTO Products
(product_id, product_name, brand, manufacturer_id,
 manufacturing_date, expiry_date, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "CG10004",
    "Hydrating Face Moisturizer",
    "GlowCare",
    5,
    "2026-11-20",
    "2028-11-20",
    "active"
))

connection.commit()

print("New product inserted successfully!") 

# ==========================================
# STEP 5: CHECK PRODUCTS TABLE STRUCTURE
# ==========================================

print("\n----- PRODUCTS TABLE STRUCTURE -----")

result = connection.execute(
    "PRAGMA table_info(Products)"
)

for column in result:
    print(column)


# ==========================================
# STEP 6: CHECK MANUFACTURERS TABLE STRUCTURE
# ==========================================

print("\n----- MANUFACTURERS TABLE STRUCTURE -----")

result = connection.execute(
    "PRAGMA table_info(Manufacturers)"
)

for column in result:
    print(column)


# ==========================================
# STEP 7: FETCH ALL MANUFACTURERS
# ==========================================

print("\n----- REGISTERED MANUFACTURERS -----")

result = connection.execute(
    "SELECT * FROM Manufacturers"
)

for manufacturer in result:
    print(manufacturer)


# ==========================================
# STEP 8: FETCH ALL PRODUCTS
# ==========================================

print("\n----- REGISTERED PRODUCTS -----")

result = connection.execute(
    "SELECT * FROM Products"
)

for product in result:
    print(product)
    # ==========================================
# STEP 8.1: SEARCH PRODUCT USING WHERE
# ==========================================

print("\n----- SEARCH SPECIFIC PRODUCT -----")

result = connection.execute(
    "SELECT * FROM Products WHERE product_id = ?",
    ("CG10004",)
)

for product in result:
    print(product)

# ==========================================
# STEP 8.2: SORT PRODUCTS USING ORDER BY
# ==========================================

print("\n----- PRODUCTS SORTED BY NAME -----")

result = connection.execute("""
SELECT * FROM Products
ORDER BY product_name ASC
""")

for product in result:
    print(product)

# ==========================================
# STEP 8.3: UPDATE PRODUCT STATUS
# ==========================================

print("\n----- UPDATE PRODUCT STATUS -----")

connection.execute("""
UPDATE Products
SET status = ?
WHERE product_id = ?
""", ("inactive", "CG10004"))

connection.commit()

print("Product status updated successfully!")

# Verify updated record
result = connection.execute("""
SELECT * FROM Products
WHERE product_id = ?
""", ("CG10004",))

for product in result:
    print(product)



  # ==========================================
# STEP 8.4: JOIN PRODUCTS AND MANUFACTURERS
# ==========================================

print("\n----- PRODUCTS WITH MANUFACTURER DETAILS -----")

result = connection.execute("""
SELECT
    Products.product_id,
    Products.product_name,
    Manufacturers.company_name
FROM Products
INNER JOIN Manufacturers
ON Products.manufacturer_id = Manufacturers.manufacturer_id
""")

for product in result:
    print(product)  



    # ==========================================
# STEP 8.5: AGGREGATE FUNCTIONS
# ==========================================

print("\n----- DATABASE STATISTICS -----")

# 1. Total Products
result = connection.execute(
    "SELECT COUNT(*) FROM Products"
).fetchone()

print("Total Products:", result[0])


# 2. Total Manufacturers
result = connection.execute(
    "SELECT COUNT(*) FROM Manufacturers"
).fetchone()

print("Total Manufacturers:", result[0])


# 3. Active Products
result = connection.execute(
    "SELECT COUNT(*) FROM Products WHERE status = 'active'"
).fetchone()

print("Active Products:", result[0])


# ==========================================
# STEP 9: CLOSE DATABASE CONNECTION
# ==========================================

connection.close()

print("\nDatabase connection closed!")
