#!/usr/bin/env python3
"""
Banking Synthetic Data Generator

A comprehensive tool for generating realistic synthetic banking data including:
- Customer profiles
- KYC records
- Bank accounts
- Transactions
- Fund transfers

Author: Your Name
Date: March 25, 2025
"""

import os
import sys
import pandas as pd
from banking_synthetic_data_app import *
from banking_app_ui import create_app

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "gradio", "pandas", "numpy", "faker", "mimesis", 
        "matplotlib", "seaborn", "tabulate"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages. Please install:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """Setup the environment for the application"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Set up logging if needed
    # (Add logging setup here if required)
    
    return True

def run_headless(args):
    """Run the application in headless mode (no UI)"""
    if len(args) < 2:
        print("Usage: python main.py headless <num_customers>")
        return False
    
    try:
        num_customers = int(args[1])
    except ValueError:
        print("Error: Number of customers must be an integer")
        return False
    
    print(f"Generating synthetic data for {num_customers} customers...")
    
    # Default parameters
    avg_accounts = 1.5
    avg_transactions = 20
    num_transfers = 200
    
    # Override defaults with command-line arguments if provided
    if len(args) >= 3:
        try:
            avg_accounts = float(args[2])
        except ValueError:
            print("Warning: Invalid avg_accounts parameter, using default (1.5)")
    
    if len(args) >= 4:
        try:
            avg_transactions = int(args[3])
        except ValueError:
            print("Warning: Invalid avg_transactions parameter, using default (20)")
    
    if len(args) >= 5:
        try:
            num_transfers = int(args[4])
        except ValueError:
            print("Warning: Invalid num_transfers parameter, using default (200)")
    
    # Generate data
    start_time = time.time()
    
    print("Generating customer data...")
    customer_data = generate_customer_data(num_customers=num_customers)
    
    print("Generating KYC data...")
    kyc_data = generate_kyc_data(customer_data)
    
    print("Generating account data...")
    account_data = generate_account_data(customer_data, avg_accounts_per_customer=avg_accounts)
    
    print("Generating transaction data...")
    transaction_data = generate_transaction_data(account_data, avg_transactions_per_account=avg_transactions)
    
    print("Generating transfer data...")
    transfer_data = generate_transfer_data(account_data, customer_data, num_transfers=num_transfers)
    
    print("Saving data...")
    save_data_to_disk(customer_data, kyc_data, account_data, transaction_data, transfer_data)
    
    end_time = time.time()
    generation_time = round(end_time - start_time, 2)
    
    print("\nData generation complete!")
    print(f"Generation time: {generation_time} seconds")
    print(f"Customers: {len(customer_data)}")
    print(f"KYC records: {len(kyc_data)}")
    print(f"Accounts: {len(account_data)}")
    print(f"Transactions: {len(transaction_data)}")
    print(f"Transfers: {len(transfer_data)}")
    print(f"\nData saved to: {os.path.abspath(OUTPUT_DIR)}")
    
    return True

def run_ui():
    """Run the application with Gradio UI"""
    app = create_app()
    print("Starting Banking Synthetic Data Generator UI...")
    app.launch(server_name="0.0.0.0")
    return True

def main():
    """Main entry point for the application"""
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Process command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "headless":
            return run_headless(sys.argv[1:])
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available commands: headless")
            return False
    
    # Default: Run with UI
    return run_ui()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
