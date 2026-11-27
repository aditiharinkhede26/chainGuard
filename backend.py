import sqlite3
import bcrypt
import uuid
import qrcode
import cv2
import os

from datetime import date


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect("chainguard.db")

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================
# SCAN HISTORY
# ==========================================

def create_scan_history_table():

    connection = get_connection()

    try:

        connection.execute("""
        CREATE TABLE IF NOT EXISTS Scan_History (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            scan_time TEXT DEFAULT CURRENT_TIMESTAMP,
            scan_result TEXT NOT NULL
        )
        """)

        connection.commit()

    finally:
        connection.close()


def record_scan(product_id, scan_result):

    connection = get_connection()

    try:

        connection.execute("""
        INSERT INTO Scan_History (product_id, scan_result)
        VALUES (?, ?)
        """, (product_id, scan_result))

        connection.commit()

    finally:
        connection.close()


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password):

    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


# ==========================================
# MANUFACTURER REGISTRATION
# ==========================================

def register_manufacturer(company_name, email, password, address):

    if not company_name or not email or not password:
        return "Please fill all required fields."

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


# ==========================================
# MANUFACTURER LOGIN
# ==========================================

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

        if manufacturer is None:
            return "Invalid email or password."

        company_name = manufacturer[1]
        stored_hash = manufacturer[2]
        status = manufacturer[3]

        password_bytes = password.encode("utf-8")
        hashed_bytes = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(password_bytes, hashed_bytes):
            return "Invalid email or password."

        if status != "Approved":
            return "Your account is pending approval."

        return f"Welcome {company_name}! Login successful."

    finally:
        connection.close()


# ==========================================
# ADMIN APPROVAL
# ==========================================

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


# ==========================================
# GENERATE UNIQUE PRODUCT ID
# ==========================================

def generate_product_id():

    unique_id = uuid.uuid4().hex[:10].upper()

    return "CG-" + unique_id


# ==========================================
# QR CODE GENERATION
# ==========================================

def generate_qr_code(product_id):

    os.makedirs("qr_codes", exist_ok=True)

    qr = qrcode.make(product_id)

    file_name = os.path.join(
        "qr_codes",
        f"{product_id}.png"
    )

    qr.save(file_name)

    return file_name


# ==========================================
# PRODUCT REGISTRATION
# ==========================================

def register_product(manufacturer_email, product_name, brand,
                     manufacturing_date, expiry_date):

    if not all([
        manufacturer_email,
        product_name,
        brand,
        manufacturing_date,
        expiry_date
    ]):
        return "Please fill all required fields."

    # Date validation

    try:

        mfg_date = date.fromisoformat(manufacturing_date)
        exp_date = date.fromisoformat(expiry_date)

        if mfg_date > date.today():
            return "Manufacturing date cannot be in the future."

        if exp_date <= mfg_date:
            return "Expiry date must be after manufacturing date."

    except ValueError:

        return "Invalid date format. Use YYYY-MM-DD."

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

        # Insert product into database

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

        # Generate QR Code

        qr_file = generate_qr_code(product_id)

        return (
            f"Product registered successfully! "
            f"Product ID: {product_id}, QR Code: {qr_file}"
        )

    except sqlite3.IntegrityError:

        connection.rollback()

        return "Product registration failed."

    finally:
        connection.close()


# ==========================================
# QR CODE SCANNING
# ==========================================

def scan_qr_code(image_path):

    detector = cv2.QRCodeDetector()

    image = cv2.imread(image_path)

    if image is None:
        return "QR image not found."

    data, points, _ = detector.detectAndDecode(image)

    if data:
        return data

    return "No QR Code detected."


# ==========================================
# PRODUCT VERIFICATION
# ==========================================

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

        # Convert tuple into dictionary

        product = {
            "Product ID": product[0],
            "Product Name": product[1],
            "Brand": product[2],
            "Manufacturer": product[3],
            "Manufacturing Date": product[4],
            "Expiry Date": product[5],
            "Status": product[6]
        }

        # Check product status

        if product["Status"].lower() != "active":

            product["Verification Result"] = "Inactive"

            return product

        # Check expiry date

        expiry_date = date.fromisoformat(product["Expiry Date"])

        if expiry_date < date.today():

            product["Verification Result"] = "Expired"

        else:

            product["Verification Result"] = "Verified"

        return product

    finally:
        connection.close()


# ==========================================
# MAIN TESTING
# ==========================================

if __name__ == "__main__":

    create_scan_history_table()

    scanned_id = scan_qr_code(
        "qr_codes/CG-5D35FF6CDD.png"
    )

    print("Scanned Product ID:", scanned_id)

    if scanned_id.startswith("CG-"):

        result = verify_product(scanned_id)

        print("\nProduct Verification Result:")
        print(result)

        if isinstance(result, dict):

            record_scan(
                scanned_id,
                result["Verification Result"]
            )

        else:

            record_scan(
                scanned_id,
                "Unknown Product"
            )

    else:

        print("QR Scanning Failed!")