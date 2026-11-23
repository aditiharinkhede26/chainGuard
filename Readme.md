# ChainGuard
 ### Blockchain-Based Product Verification with ML-Powered Anomaly Detection

## About the Project

ChainGuard is a multi-brand product verification and traceability platform designed to help identify suspicious products and unusual activities across supply chains.

The application combines QR code and barcode scanning, blockchain technology, machine learning, and supply-chain tracking to provide product information and verification insights.

It is initially focused on skincare and cosmetic products.

## Problem Statement

Counterfeit products and supply-chain manipulation are major challenges in the cosmetics and skincare industry.

Customers often lack access to reliable product information and transparent supply-chain records.

ChainGuard aims to address this problem through product identification, traceability, and suspicious activity detection.

## Key Features

- Multi-brand manufacturer registration.
- Individual product identification using unique IDs.
- QR code generation for registered products.
- Open product scanner for registered and unregistered products.
- External product information lookup where available.
- Supply-chain tracking.
- Blockchain-based record verification.
- ML-powered suspicious activity detection.
- Supply-chain graph analysis.
- Customer and administrator dashboards.

## Technology Stack

- **Programming Language:** Python
- **Frontend:** Streamlit
- **Database:** SQLite
- **Machine Learning:** Scikit-learn
- **Data Processing:** Pandas, NumPy
- **Blockchain:** Solidity, Web3.py
- **QR Code:** Python QR Code Library
- **Graph Analysis:** NetworkX
- **Version Control:** Git and GitHub

## How It Works

1. Manufacturers register their accounts.
2. Manufacturers register their products.
3. The system generates unique IDs and QR codes for individual product units.
4. Supply-chain events are recorded.
5. Customers scan product QR codes or barcodes.
6. ChainGuard retrieves available product information and verification records.
7. Machine learning analyses suspicious patterns and generates risk insights.

## Project Status

Currently under development.

## Limitations

- Unregistered products may not have ChainGuard verification records.
- External product information depends on the availability of reliable databases.
- A QR code or barcode scan alone cannot prove physical product authenticity.
- Blockchain protects recorded information from unauthorized alteration but cannot independently guarantee that the original information was genuine.
- ML identifies suspicious patterns; it does not conclusively prove that a product is counterfeit.

## Future Scope

- NFC-based product verification.
- Advanced manufacturer verification.
- Cloud database integration.
- Mobile application.
- Advanced ML and deep learning models.
- Real-time supply-chain tracking.
- Integration with additional product information databases.