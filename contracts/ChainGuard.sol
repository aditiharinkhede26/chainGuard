// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ChainGuard {
    // Product Information
struct Product {
    string productName;
    string brand;
    address registeredBy;
    uint256 registeredAt;
    bool exists;
}

// Store products using Product ID
mapping(string => Product) private products;

// Event generated when a product is registered
event ProductRegistered(
    string productId,
    string productName,
    string brand,
    address manufacturer
);

function registerProduct(
    string memory productId,
    string memory productName,
    string memory brand
) public {

    require(!products[productId].exists, "Product already registered");

    products[productId] = Product({
        productName: productName,
        brand: brand,
        registeredBy: msg.sender,
        registeredAt: block.timestamp,
        exists: true
    });

    emit ProductRegistered(
        productId,
        productName,
        brand,
        msg.sender
    );
}

function verifyProduct(string memory productId)
    public
    view
    returns (
        bool,
        string memory,
        string memory,
        address,
        uint256
    )
{
    Product memory product = products[productId];

    if (!product.exists) {
        return (false, "", "", address(0), 0);
    }

    return (
        true,
        product.productName,
        product.brand,
        product.registeredBy,
        product.registeredAt
    );
}
}