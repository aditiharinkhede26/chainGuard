import sqlite3

connection = sqlite3.connect("chainguard.db")

cursor = connection.cursor()

cursor.execute("""
SELECT company_name, email, password_hash, status
FROM Manufacturers
WHERE email = 'testcosmetics@example.com'
""")

manufacturer = cursor.fetchone()

if manufacturer:
    print("Company:", manufacturer[0])
    print("Email:", manufacturer[1])
    print("Password Hash:", manufacturer[2])
    print("Status:", manufacturer[3])
else:
    print("Manufacturer not found!")

connection.close()