import gradio as gr
import pandas as pd
import numpy as np
import random
import faker
import datetime
import uuid
import json
import os
from faker import Faker
from faker.providers import bank, person, address, company, credit_card, date_time
from mimesis import Person, Address, Finance, Datetime, locales
from mimesis.schema import Field, Schema
from mimesis.enums import Gender
import matplotlib.pyplot as plt
import seaborn as sns
import time
import zipfile
import io

# Initialize the synthetic data generators
fake = Faker()
fake.add_provider(bank)
fake.add_provider(person)
fake.add_provider(address)
fake.add_provider(company)
fake.add_provider(credit_card)
fake.add_provider(date_time)

# Initialize mimesis generators with locale
person_gen = Person(locale=locales.EN)
address_gen = Address(locale=locales.EN)
finance_gen = Finance(locale=locales.EN)
datetime_gen = Datetime(locale=locales.EN)

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Global variables
OUTPUT_DIR = "synthetic_data_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create a shared state for the app
class AppState:
    def __init__(self):
        self.customer_data = None
        self.kyc_data = None
        self.account_data = None
        self.transaction_data = None
        self.transfer_data = None
        self.generation_stats = {}
        
app_state = AppState()

# Classes for different banking data generators
class CustomerGenerator:
    """Generate synthetic customer data for account onboarding"""
    
    def __init__(self):
        self.customer_ids = set()
        self.email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
        
    def generate_customer_id(self):
        """Generate a unique customer ID"""
        while True:
            customer_id = f"CUST{random.randint(1000000, 9999999)}"
            if customer_id not in self.customer_ids:
                self.customer_ids.add(customer_id)
                return customer_id
    
    def generate_single_customer(self):
        """Generate a single customer record"""
        gender = random.choice(["M", "F"])
        first_name = person_gen.first_name(gender=Gender.MALE if gender == "M" else Gender.FEMALE)
        last_name = person_gen.last_name()
        dob = datetime_gen.date(start=1950, end=2005)
        age = datetime.datetime.now().year - dob.year
        
        customer = {
            "customer_id": self.generate_customer_id(),
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "age": age,
            "email": f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.email_domains)}",
            "phone_number": person_gen.telephone(),
            "nationality": address_gen.country(),
            "address_line1": address_gen.address(),
            "city": address_gen.city(),
            "state": address_gen.state(),
            "postal_code": address_gen.postal_code(),
            "country": address_gen.country(),
            "occupation": fake.job(),
            "employer": fake.company(),
            "annual_income": round(random.uniform(30000, 250000), 2),
            "registration_date": datetime_gen.date(start=2020, end=2024).strftime("%Y-%m-%d"),
            "credit_score": random.randint(300, 850)
        }
        return customer
    
    def generate_customers(self, count=100):
        """Generate multiple customer records"""
        customers = []
        for _ in range(count):
            customers.append(self.generate_single_customer())
        return pd.DataFrame(customers)


class KYCGenerator:
    """Generate synthetic KYC verification data"""
    
    def __init__(self, customer_data):
        self.customer_data = customer_data
        self.document_types = ["Passport", "Driver's License", "National ID Card", "Residence Permit"]
        self.verification_statuses = ["Pending", "Verified", "Rejected", "Additional Info Required"]
        self.verification_methods = ["Manual Review", "Automated", "Video Verification", "Third-party API"]
        self.risk_categories = ["Low", "Medium", "High"]
        
    def generate_kyc_data(self):
        """Generate KYC data for all customers"""
        kyc_records = []
        
        for _, customer in self.customer_data.iterrows():
            document_type = random.choice(self.document_types)
            
            # Weighted probability for verification status - most should be verified
            status_weights = [0.15, 0.70, 0.05, 0.10]
            verification_status = random.choices(self.verification_statuses, weights=status_weights)[0]
            
            # Create expiry date (usually valid for 5-10 years)
            issue_date = datetime.datetime.strptime(customer["registration_date"], "%Y-%m-%d")
            expiry_years = random.randint(5, 10)
            expiry_date = (issue_date + datetime.timedelta(days=365 * expiry_years)).strftime("%Y-%m-%d")
            
            # Create verification date (usually within 1-7 days of registration)
            verification_days = random.randint(1, 7)
            verification_date = (issue_date + datetime.timedelta(days=verification_days)).strftime("%Y-%m-%d")
            
            # Risk score calculation based on some factors
            risk_factors = []
            # Age-based risk (younger and very old customers might pose higher risk)
            if customer["age"] < 25 or customer["age"] > 70:
                risk_factors.append(0.1)
            # Income-based risk (very high income might need extra verification)
            if customer["annual_income"] > 200000:
                risk_factors.append(0.15)
            # Random risk element
            risk_factors.append(random.uniform(0, 0.5))
            
            risk_score = min(sum(risk_factors), 1.0)
            risk_category = "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.7 else "High"
            
            # Additional notes based on verification status
            notes = ""
            if verification_status == "Rejected":
                reasons = ["Document expired", "Information mismatch", "Poor image quality", "Suspected fraud"]
                notes = random.choice(reasons)
            elif verification_status == "Additional Info Required":
                info_needed = ["Secondary ID", "Proof of address", "Clear photo", "Income verification"]
                notes = f"Required: {random.choice(info_needed)}"
            
            kyc_record = {
                "customer_id": customer["customer_id"],
                "document_type": document_type,
                "document_number": f"{document_type[:3].upper()}{random.randint(10000000, 99999999)}",
                "issuing_country": customer["nationality"],
                "issue_date": customer["registration_date"],
                "expiry_date": expiry_date,
                "verification_status": verification_status,
                "verification_date": verification_date,
                "verification_method": random.choice(self.verification_methods),
                "risk_score": round(risk_score, 2),
                "risk_category": risk_category,
                "pep_status": random.choices([True, False], weights=[0.03, 0.97])[0],
                "sanctions_match": random.choices([True, False], weights=[0.01, 0.99])[0],
                "notes": notes
            }
            
            kyc_records.append(kyc_record)
        
        return pd.DataFrame(kyc_records)


class AccountGenerator:
    """Generate synthetic bank account data"""
    
    def __init__(self, customer_data):
        self.customer_data = customer_data
        self.account_ids = set()
        self.account_types = ["Savings", "Checking", "Money Market", "Certificate of Deposit", "Investment"]
        self.currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
        self.status_options = ["Active", "Dormant", "Closed", "Frozen", "Pending"]
        
    def generate_account_id(self):
        """Generate a unique account ID"""
        while True:
            account_id = f"ACCT{random.randint(10000000, 99999999)}"
            if account_id not in self.account_ids:
                self.account_ids.add(account_id)
                return account_id
    
    def generate_accounts(self, avg_accounts_per_customer=1.5):
        """Generate account data for customers"""
        accounts = []
        
        for _, customer in self.customer_data.iterrows():
            # Each customer can have 1-3 accounts
            num_accounts = np.random.poisson(avg_accounts_per_customer - 1) + 1
            num_accounts = min(max(num_accounts, 1), 3)
            
            for _ in range(num_accounts):
                account_type = random.choice(self.account_types)
                
                # Opening balance based on account type and customer income
                if account_type == "Savings":
                    min_balance = 500
                    max_balance = customer["annual_income"] * 0.2
                elif account_type == "Checking":
                    min_balance = 100
                    max_balance = customer["annual_income"] * 0.1
                elif account_type == "Money Market":
                    min_balance = 1000
                    max_balance = customer["annual_income"] * 0.3
                elif account_type == "Certificate of Deposit":
                    min_balance = 5000
                    max_balance = customer["annual_income"] * 0.4
                else:  # Investment
                    min_balance = 10000
                    max_balance = customer["annual_income"] * 0.5
                
                opening_balance = round(random.uniform(min_balance, max_balance), 2)
                
                # Account opening date (after customer registration)
                registration_date = datetime.datetime.strptime(customer["registration_date"], "%Y-%m-%d")
                days_after_registration = random.randint(0, 30)
                opening_date = (registration_date + datetime.timedelta(days=days_after_registration)).strftime("%Y-%m-%d")
                
                # Interest rate based on account type
                if account_type == "Savings":
                    interest_rate = round(random.uniform(0.01, 0.03), 4)
                elif account_type == "Checking":
                    interest_rate = round(random.uniform(0.0, 0.01), 4)
                elif account_type == "Money Market":
                    interest_rate = round(random.uniform(0.02, 0.04), 4)
                elif account_type == "Certificate of Deposit":
                    interest_rate = round(random.uniform(0.03, 0.06), 4)
                else:  # Investment
                    interest_rate = None
                
                # Status weights - most accounts should be active
                status_weights = [0.85, 0.05, 0.05, 0.02, 0.03]
                status = random.choices(self.status_options, weights=status_weights)[0]
                
                # If account is closed, add closing date
                closing_date = None
                if status == "Closed":
                    opening_datetime = datetime.datetime.strptime(opening_date, "%Y-%m-%d")
                    # Account typically closed after 30-365 days
                    closing_days = random.randint(30, 365)
                    closing_date = (opening_datetime + datetime.timedelta(days=closing_days)).strftime("%Y-%m-%d")
                
                account = {
                    "account_id": self.generate_account_id(),
                    "customer_id": customer["customer_id"],
                    "account_type": account_type,
                    "account_number": str(random.randint(1000000000, 9999999999)),
                    "routing_number": str(random.randint(100000000, 999999999)),
                    "currency": random.choice(self.currencies),
                    "opening_balance": opening_balance,
                    "current_balance": opening_balance if status != "Closed" else 0,
                    "available_balance": opening_balance * 0.95 if status == "Active" else 0,
                    "interest_rate": interest_rate,
                    "opening_date": opening_date,
                    "closing_date": closing_date,
                    "status": status,
                    "overdraft_limit": round(customer["annual_income"] * 0.02, 2) if account_type == "Checking" else 0,
                    "last_activity_date": datetime_gen.date(start=2023, end=2024).strftime("%Y-%m-%d") if status == "Active" else None
                }
                
                accounts.append(account)
        
        return pd.DataFrame(accounts)


class TransactionGenerator:
    """Generate synthetic bank transaction data"""
    
    def __init__(self, account_data):
        self.account_data = account_data
        self.transaction_types = ["Deposit", "Withdrawal", "Transfer", "Payment", "Fee", "Interest"]
        self.payment_categories = ["Utilities", "Shopping", "Groceries", "Entertainment", "Travel", 
                                  "Dining", "Healthcare", "Education", "Housing", "Transportation"]
        self.channels = ["Online Banking", "Mobile App", "ATM", "Branch", "Automated/System"]
        self.statuses = ["Completed", "Pending", "Failed", "Reversed"]
        
    def generate_transactions(self, avg_transactions_per_account=20, max_days_back=90):
        """Generate transaction data for accounts"""
        transactions = []
        
        for _, account in self.account_data.iterrows():
            # Skip closed accounts or generate fewer transactions
            if account["status"] == "Closed":
                continue
            elif account["status"] == "Dormant":
                avg_transactions = 2
            elif account["status"] == "Frozen":
                avg_transactions = 5
            else:
                avg_transactions = avg_transactions_per_account
            
            # Number of transactions follows a Poisson distribution
            num_transactions = np.random.poisson(avg_transactions)
            
            # Opening date of the account
            opening_date = datetime.datetime.strptime(account["opening_date"], "%Y-%m-%d")
            
            # Today's date for reference
            today = datetime.datetime.now()
            
            # Generate transactions
            running_balance = account["opening_balance"]
            
            for i in range(num_transactions):
                # Generate transaction date (between opening date and today)
                days_since_opening = (today - opening_date).days
                if days_since_opening <= 0:
                    continue
                
                max_days = min(days_since_opening, max_days_back)
                if max_days <= 0:
                    continue
                    
                days_ago = random.randint(0, max_days)
                transaction_date = (today - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                # Transaction type based on weights
                tx_type_weights = [0.3, 0.25, 0.2, 0.2, 0.03, 0.02]
                transaction_type = random.choices(self.transaction_types, weights=tx_type_weights)[0]
                
                # Transaction amount based on type and account balance
                if transaction_type == "Deposit":
                    min_amount = 10
                    max_amount = 5000
                    amount = round(random.uniform(min_amount, max_amount), 2)
                    amount_sign = 1
                elif transaction_type == "Withdrawal":
                    min_amount = 10
                    max_amount = min(running_balance * 0.5, 1000)
                    if max_amount < min_amount:
                        max_amount = min_amount
                    amount = round(random.uniform(min_amount, max_amount), 2)
                    amount_sign = -1
                elif transaction_type == "Transfer":
                    min_amount = 50
                    max_amount = min(running_balance * 0.7, 3000)
                    if max_amount < min_amount:
                        max_amount = min_amount
                    amount = round(random.uniform(min_amount, max_amount), 2)
                    # Transfer can be incoming or outgoing
                    amount_sign = random.choice([-1, 1])
                elif transaction_type == "Payment":
                    min_amount = 10
                    max_amount = min(running_balance * 0.4, 2000)
                    if max_amount < min_amount:
                        max_amount = min_amount
                    amount = round(random.uniform(min_amount, max_amount), 2)
                    amount_sign = -1
                elif transaction_type == "Fee":
                    amount = round(random.uniform(1, 50), 2)
                    amount_sign = -1
                else:  # Interest
                    if account["interest_rate"]:
                        amount = round(running_balance * account["interest_rate"] / 12, 2)
                    else:
                        amount = round(running_balance * 0.0025, 2)  # Default interest
                    amount_sign = 1
                
                # Apply amount sign
                signed_amount = amount * amount_sign
                
                # Update running balance
                new_balance = running_balance + signed_amount
                
                # Transaction status (mostly completed)
                status_weights = [0.95, 0.03, 0.01, 0.01]
                status = random.choices(self.statuses, weights=status_weights)[0]
                
                # If transaction failed, don't update balance
                if status == "Failed":
                    new_balance = running_balance
                
                # Transaction details
                transaction = {
                    "transaction_id": str(uuid.uuid4()),
                    "account_id": account["account_id"],
                    "transaction_date": transaction_date,
                    "transaction_type": transaction_type,
                    "amount": abs(amount),  # Store absolute amount
                    "direction": "Credit" if amount_sign > 0 else "Debit",
                    "running_balance": round(new_balance, 2) if status == "Completed" else round(running_balance, 2),
                    "description": self._generate_description(transaction_type),
                    "category": random.choice(self.payment_categories) if transaction_type == "Payment" else None,
                    "channel": random.choice(self.channels),
                    "status": status,
                    "reference_number": f"REF{random.randint(1000000, 9999999)}",
                    "counterparty_name": self._generate_counterparty(transaction_type) if transaction_type in ["Transfer", "Payment"] else None,
                    "counterparty_account": f"ACCT{random.randint(1000000, 9999999)}" if transaction_type in ["Transfer"] else None
                }
                
                transactions.append(transaction)
                
                # Update running balance for next transaction (if completed)
                if status == "Completed":
                    running_balance = new_balance
            
        return pd.DataFrame(transactions)
    
    def _generate_description(self, transaction_type):
        """Generate a realistic transaction description"""
        if transaction_type == "Deposit":
            templates = [
                "Salary deposit",
                "Cash deposit",
                "Check deposit",
                "Direct deposit",
                "Transfer in",
                "Mobile deposit",
                "Refund from {}"
            ]
            merchants = ["Amazon", "Walmart", "Target", "Best Buy", "Apple Store", "Gas Station", "Department Store"]
            template = random.choice(templates)
            return template.format(random.choice(merchants)) if "{}" in template else template
        
        elif transaction_type == "Withdrawal":
            templates = [
                "ATM withdrawal",
                "Cash withdrawal",
                "Teller withdrawal",
                "Check withdrawal",
                "Transfer out"
            ]
            return random.choice(templates)
        
        elif transaction_type == "Transfer":
            templates = [
                "Transfer to account ending in {}",
                "Transfer from account ending in {}",
                "Online transfer",
                "Scheduled transfer",
                "Recurring transfer",
                "Transfer to {}"
            ]
            template = random.choice(templates)
            if "{}" in template:
                if "ending in" in template:
                    return template.format(random.randint(1000, 9999))
                else:
                    return template.format(fake.name())
            return template
        
        elif transaction_type == "Payment":
            categories = {
                "Utilities": ["Electric bill", "Water bill", "Gas bill", "Internet bill", "Phone bill"],
                "Shopping": ["Amazon purchase", "Online shopping", "Department store purchase", "{} purchase"],
                "Groceries": ["Grocery shopping", "Supermarket", "Food store"],
                "Entertainment": ["Movie tickets", "Streaming service", "Concert tickets", "Game purchase"],
                "Travel": ["Airline tickets", "Hotel booking", "Car rental", "Travel agency"],
                "Dining": ["Restaurant payment", "Coffee shop", "Fast food", "Food delivery"],
                "Healthcare": ["Doctor's visit", "Pharmacy", "Health insurance", "Dental payment"],
                "Education": ["Tuition payment", "Book purchase", "Course fee", "School supplies"],
                "Housing": ["Rent payment", "Mortgage payment", "Property tax", "HOA dues"],
                "Transportation": ["Gas station", "Car payment", "Public transport", "Ride sharing"]
            }
            category = random.choice(list(categories.keys()))
            description = random.choice(categories[category])
            if "{}" in description:
                merchants = ["Amazon", "Walmart", "Target", "Best Buy", "Apple", "Nike", "Adidas", "H&M", "Macy's"]
                return description.format(random.choice(merchants))
            return description
        
        elif transaction_type == "Fee":
            fees = [
                "Monthly service fee",
                "ATM fee",
                "Overdraft fee",
                "Wire transfer fee",
                "Late payment fee",
                "Foreign transaction fee",
                "Account maintenance fee"
            ]
            return random.choice(fees)
        
        else:  # Interest
            return "Interest payment"
    
    def _generate_counterparty(self, transaction_type):
        """Generate a realistic counterparty name"""
        if transaction_type == "Transfer":
            # 50% chance it's a transfer to another person
            if random.random() < 0.5:
                return fake.name()
            else:
                # Internal account transfer
                return "Own account"
        elif transaction_type == "Payment":
            businesses = [
                "Amazon", "Netflix", "Spotify", "Apple", "Google", "Uber", "Lyft", 
                "Walmart", "Target", "Costco", "Whole Foods", "Safeway", "AT&T",
                "Verizon", "Comcast", "PG&E", "State Farm", "Geico", "Bank of America",
                "Chase", "Wells Fargo", "American Express", "Capital One"
            ]
            return random.choice(businesses)
        return None


class FundTransferGenerator:
    """Generate synthetic fund transfer data"""
    
    def __init__(self, account_data, customer_data):
        self.account_data = account_data
        self.customer_data = customer_data
        self.transfer_types = ["Internal Transfer", "External Transfer", "Wire Transfer", "ACH Transfer"]
        self.transfer_statuses = ["Completed", "Pending", "Failed", "Cancelled"]
        self.reasons = ["Regular Payment", "Bill Payment", "Investment", "Loan Repayment", "Savings", "Family Support"]
        
    def generate_transfers(self, count=200):
        """Generate synthetic fund transfer data"""
        # Get active accounts only
        active_accounts = self.account_data[self.account_data["status"] == "Active"]
        
        if len(active_accounts) < 2:
            raise ValueError("Need at least 2 active accounts to generate transfers")
        
        transfers = []
        for _ in range(count):
            # Randomly select source account
            source_account = active_accounts.sample(1).iloc[0]
            
            # Transfer type
            transfer_type = random.choice(self.transfer_types)
            
            # For internal transfers, select a destination account from the same customer or another customer
            if transfer_type == "Internal Transfer":
                # 70% chance it's between same customer's accounts
                if random.random() < 0.7:
                    customer_accounts = active_accounts[active_accounts["customer_id"] == source_account["customer_id"]]
                    if len(customer_accounts) > 1:
                        # Select an account that's different from the source
                        dest_accounts = customer_accounts[customer_accounts["account_id"] != source_account["account_id"]]
                        if len(dest_accounts) > 0:
                            dest_account = dest_accounts.sample(1).iloc[0]
                        else:
                            # No other account for this customer, select a random one
                            dest_account = active_accounts[active_accounts["account_id"] != source_account["account_id"]].sample(1).iloc[0]
                    else:
                        # Only one account for this customer, select a random one
                        dest_account = active_accounts[active_accounts["account_id"] != source_account["account_id"]].sample(1).iloc[0]
                else:
                    # Different customer, same bank
                    dest_account = active_accounts[active_accounts["account_id"] != source_account["account_id"]].sample(1).iloc[0]
                
                # Set destination details
                destination_account_id = dest_account["account_id"]
                destination_account_number = dest_account["account_number"]
                destination_bank_name = "Same Bank"
                
                # Get destination customer details
                dest_customer = self.customer_data[self.customer_data["customer_id"] == dest_account["customer_id"]].iloc[0]
                destination_account_holder = f"{dest_customer['first_name']} {dest_customer['last_name']}"
            
            else:  # External transfers
                destination_account_id = None
                destination_account_number = f"{random.randint(10000000, 99999999)}"
                
                if transfer_type == "Wire Transfer":
                    banks = ["Chase Bank", "Bank of America", "Wells Fargo", "Citibank", "Capital One", 
                            "TD Bank", "PNC Bank", "US Bank", "HSBC", "Barclays"]
                else:
                    banks = ["Chase Bank", "Bank of America", "Wells Fargo", "Citibank", "Capital One", 
                            "TD Bank", "PNC Bank", "US Bank", "HSBC", "Barclays", 
                            "Venmo", "PayPal", "Cash App", "Zelle"]
                
                destination_bank_name = random.choice(banks)
                destination_account_holder = fake.name()
            
            # Transfer date
            transfer_date = datetime_gen.date(start=2023, end=2024)
            
            # Transfer amount (based on source account balance)
            max_amount = min(source_account["current_balance"] * 0.8, 5000)
            if max_amount < 10:
                max_amount = 10
            amount = round(random.uniform(10, max_amount), 2)
            
            # Status weights - most transfers should be completed
            status_weights = [0.85, 0.10, 0.03, 0.02]
            status = random.choices(self.transfer_statuses, weights=status_weights)[0]
            
            # Transaction fees
            if transfer_type == "Wire Transfer":
                fee = round(random.uniform(15, 30), 2)
            elif transfer_type == "External Transfer":
                fee = round(random.uniform(0, 5), 2)
            else:
                fee = 0
            
            # Settlement date (same day or next day for internal transfers, 1-3 days for external)
            if transfer_type == "Internal Transfer":
                settlement_days = random.randint(0, 1)
            elif transfer_type == "ACH Transfer":
                settlement_days = random.randint(1, 3)
            else:
                settlement_days = random.randint(0, 3)
            
            settlement_date = (transfer_date + datetime.timedelta(days=settlement_days)).strftime("%Y-%m-%d") if status == "Completed" else None
            
            # Reference number
            reference_number = f"TRF{random.randint(1000000, 9999999)}"
            
            transfer = {
                "transfer_id": str(uuid.uuid4()),
                "source_account_id": source_account["account_id"],
                "source_account_number": source_account["account_number"],
                "destination_account_id": destination_account_id,
                "destination_account_number": destination_account_number,
                "destination_bank_name": destination_bank_name,
                "destination_account_holder": destination_account_holder,
                "transfer_type": transfer_type,
                "amount": amount,
                "currency": source_account["currency"],
                "transfer_date": transfer_date.strftime("%Y-%m-%d"),
                "settlement_date": settlement_date,
                "status": status,
                "reference_number": reference_number,
                "fee": fee,
                "reason": random.choice(self.reasons),
                "notes": f"Transfer to {destination_account_holder}" if random.random() < 0.3 else ""
            }
            
            transfers.append(transfer)
        
        return pd.DataFrame(transfers)


# Functions for data generation

def generate_customer_data(num_customers=100):
    """Generate synthetic customer data"""
    customer_gen = CustomerGenerator()
    return customer_gen.generate_customers(count=num_customers)

def generate_kyc_data(customer_data):
    """Generate synthetic KYC data"""
    kyc_gen = KYCGenerator(customer_data)
    return kyc_gen.generate_kyc_data()

def generate_account_data(customer_data, avg_accounts_per_customer=1.5):
    """Generate synthetic account data"""
    account_gen = AccountGenerator(customer_data)
    return account_gen.generate_accounts(avg_accounts_per_customer=avg_accounts_per_customer)

def generate_transaction_data(account_data, avg_transactions_per_account=20):
    """Generate synthetic transaction data"""
    transaction_gen = TransactionGenerator(account_data)
    return transaction_gen.generate_transactions(avg_transactions_per_account=avg_transactions_per_account)

def generate_transfer_data(account_data, customer_data, num_transfers=200):
    """Generate synthetic fund transfer data"""
    transfer_gen = FundTransferGenerator(account_data, customer_data)
    return transfer_gen.generate_transfers(count=num_transfers)
