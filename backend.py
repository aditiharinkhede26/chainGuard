import uuid
import sqlite3
import qrcode
import cv2


# Connect to ChainGuard database
def get_connection():

    connection = sqlite3.connect("chainguard.db")

    connection.execute("PRAGMA foreign_keys = ON")

    return connection

import bcrypt


# Hash manufacturer password
def hash_password(password):

    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")



# Register a new manufacturer
def register_manufacturer(company_name, email, password, address):

    # Validate empty fields
    if not company_name or not email or not password:
        return "Please fill all required fields."

    # Hash password
    password_hash = hash_password(password)

    connection = get_connection()

    try:

        connection.execute("""
        INSERT INTO Manufacturers
        (company_name, email, password_hash, address)
        VALUES (?, ?, ?, ?)
        """, (
            company_name,
            email,
            password_hash,
            address
        ))

        connection.commit()

        return "Manufacturer registered successfully!"

    except sqlite3.IntegrityError:
        connection.rollback()
        return "Email already registered or invalid data."

    finally:
        connection.close()



        # Login manufacturer
def login_manufacturer(email, password):

    if not email or not password:
        return "Please enter email and password."

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
        SELECT manufacturer_id, company_name, password_hash, status
        FROM Manufacturers
        WHERE email = ?
        """, (email,))

        manufacturer = cursor.fetchone()

        # Check whether email exists
        if manufacturer is None:
            return "Invalid email or password."

        manufacturer_id = manufacturer[0]
        company_name = manufacturer[1]
        stored_hash = manufacturer[2]
        status = manufacturer[3]

        # Verify password
        password_bytes = password.encode("utf-8")
        hashed_bytes = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(password_bytes, hashed_bytes):
            return "Invalid email or password."

        # Check manufacturer approval status
        if status != "Approved":
            return "Your account is pending approval."

        return f"Welcome {company_name}! Login successful."

    finally:
        connection.close()



        # Approve manufacturer
def approve_manufacturer(email):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
        UPDATE Manufacturers
        SET status = 'Approved'
        WHERE email = ? AND status = 'Pending'
        """, (email,))

        connection.commit()

        if cursor.rowcount == 0:
            return "Manufacturer not found or already approved."

        return "Manufacturer approved successfully!"

    finally:
        connection.close()


# Generate unique Product ID
def generate_product_id():

    unique_id = uuid.uuid4().hex[:10].upper()

    return "CG-" + unique_id


# Register a new product
def register_product(manufacturer_email, product_name, brand,
                     manufacturing_date, expiry_date):

    if not all([manufacturer_email, product_name, brand,
                manufacturing_date, expiry_date]):
        return "Please fill all product details."

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # Check manufacturer approval
        cursor.execute("""
        SELECT manufacturer_id
        FROM Manufacturers
        WHERE email = ? AND status = 'Approved'
        """, (manufacturer_email,))

        manufacturer = cursor.fetchone()

        if manufacturer is None:
            return "Manufacturer not found or not approved."

        manufacturer_id = manufacturer[0]

        # Generate Product ID
        product_id = generate_product_id()

        # Save product in database
        cursor.execute("""
        INSERT INTO Products
        (product_id, product_name, brand, manufacturer_id,
         manufacturing_date, expiry_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            product_name,
            brand,
            manufacturer_id,
            manufacturing_date,
            expiry_date
        ))

        connection.commit()

        #Generate QR code
        qr_file=generate_qr_code(product_id)

        return f"Product registered successfully! Product ID: {product_id}, QR Code: {qr_file}"

        
        
    except sqlite3.IntegrityError:
        connection.rollback()
        return "Product registration failed."

    finally:
        connection.close()



# Generate QR Code for a product
def generate_qr_code(product_id):

    qr = qrcode.make(product_id)

    file_name = f"{product_id}.png"

    qr.save(file_name)

    return file_name


# Scan QR Code
def scan_qr_code(image_path):

    detector = cv2.QRCodeDetector()

    image = cv2.imread(image_path)

    if image is None:
        return "QR image not found."

    data, points, _ = detector.detectAndDecode(image)

    if data:
        return data

    return "No QR Code detected."



# Verify product using Product ID
def verify_product(product_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            Products.product_id,
            Products.product_name,
            Products.brand,
            Manufacturers.company_name,
            Products.manufacturing_date,
            Products.expiry_date,
            Products.status
        FROM Products
        INNER JOIN Manufacturers
        ON Products.manufacturer_id = Manufacturers.manufacturer_id
        WHERE Products.product_id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if product is None:
            return "Product Not Registered in ChainGuard."

        return {
            "Product ID": product[0],
            "Product Name": product[1],
            "Brand": product[2],
            "Manufacturer": product[3],
            "Manufacturing Date": product[4],
            "Expiry Date": product[5],
            "Status": product[6]
        }

    finally:
        connection.close()


if __name__ == "__main__":

    scanned_id = scan_qr_code("CG-5D35FF6CDD.png")

    print("Scanned Product ID:", scanned_id)

    if scanned_id.startswith("CG-"):

        result = verify_product(scanned_id)

        print("\nProduct Verification Result:")
        print(result)

    else:
        print("QR Scanning Failed!")