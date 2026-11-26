
import sqlite3

connection = sqlite3.connect("chainguard.db")

cursor = connection.cursor()

cursor.execute("""
SELECT
    Products.product_id,
    Products.product_name,
    Products.brand,
    Manufacturers.company_name
FROM Products
INNER JOIN Manufacturers
ON Products.manufacturer_id = Manufacturers.manufacturer_id
WHERE Products.product_id = 'CG-59DD7ED16A'
""")

product = cursor.fetchone()

if product:
    print("Product ID:", product[0])
    print("Product Name:", product[1])
    print("Brand:", product[2])
    print("Manufacturer:", product[3])
else:
    print("Product not found!")

connection.close()