import json
from web3 import Web3
import os

# Connect to local blockchain
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Check blockchain connection
if web3.is_connected():
    print("Blockchain Connected Successfully!")

# Get available blockchain accounts
accounts = web3.eth.accounts

# Select first account
owner = accounts[0]

print("Available Accounts:", len(accounts))
print("Selected Account:", owner)


# Load Contract ABI
with open("contracts/ChainGuard.json", "r") as file:
    contract_abi = json.load(file)

# Load Contract Bytecode
with open("contracts/ChainGuard_bytecode.txt", "r") as file:
    contract_bytecode = file.read().strip()

print("Contract ABI and Bytecode Loaded Successfully!")

# Create Contract Instance
ChainGuard = web3.eth.contract(
    abi=contract_abi,
    bytecode=contract_bytecode
)

# Check Existing Contract Address
address_file = "contracts/contract_address.txt"

if os.path.exists(address_file):

    with open(address_file, "r") as file:
        contract_address = file.read().strip()

    print("Existing Smart Contract Address Loaded!")

else:

    # Deploy New Smart Contract
    transaction_hash = ChainGuard.constructor().transact({
        "from": owner
    })

    # Wait for Deployment Transaction
    transaction_receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    # Get Deployed Contract Address
    contract_address = transaction_receipt.contractAddress

    # Save Contract Address
    with open(address_file, "w") as file:
        file.write(contract_address)

    print("Smart Contract Deployed Successfully!")


# Connect to deployed smart contract
contract = web3.eth.contract(
    address=contract_address,
    abi=contract_abi
)

print("Connected to ChainGuard Smart Contract!")


# Register Product on Blockchain

def register_product_on_blockchain(product_id, product_name, brand):

    tx_hash = contract.functions.registerProduct(
        product_id,
        product_name,
        brand
    ).transact({
        "from": owner
    })

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "success": True,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber
    }


# Verify Product on Blockchain

def verify_product_on_blockchain(product_id):

    result = contract.functions.verifyProduct(
        product_id
    ).call()

    return {
        "exists": result[0],
        "product_name": result[1],
        "brand": result[2],
        "registered_by": result[3],
        "registered_at": result[4]
    }