from backend import (
    get_manufacturer_products,
    get_manufacturer_product_count,
    get_manufacturer_scan_history,
    record_scan
)

manufacturer_id = 1

# Get manufacturer products
products = get_manufacturer_products(manufacturer_id)

print("\nManufacturer Products:")

for product in products:
    print(product)

# Get total product count
count = get_manufacturer_product_count(manufacturer_id)

print("\nTotal Registered Products:", count)


# Get manufacturer scan history
history = get_manufacturer_scan_history(manufacturer_id)

print("\nManufacturer Scan History:")

for scan in history:
    print(scan)