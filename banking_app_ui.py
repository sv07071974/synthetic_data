# Add visualization and data exploration functions
def visualize_customer_age_distribution(customer_data):
    """Visualize the age distribution of customers"""
    plt.figure(figsize=(10, 6))
    sns.histplot(data=customer_data, x="age", bins=20, kde=True)
    plt.title("Customer Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Count")
    return plt

def visualize_income_distribution(customer_data):
    """Visualize the income distribution of customers"""
    plt.figure(figsize=(10, 6))
    sns.histplot(data=customer_data, x="annual_income", bins=20, kde=True)
    plt.title("Customer Income Distribution")
    plt.xlabel("Annual Income")
    plt.ylabel("Count")
    return plt

def visualize_account_types(account_data):
    """Visualize the distribution of account types"""
    plt.figure(figsize=(10, 6))
    account_counts = account_data["account_type"].value_counts()
    plt.pie(account_counts, labels=account_counts.index, autopct="%1.1f%%", startangle=90)
    plt.title("Distribution of Account Types")
    return plt

def visualize_transaction_types(transaction_data):
    """Visualize the distribution of transaction types"""
    plt.figure(figsize=(12, 6))
    tx_counts = transaction_data["transaction_type"].value_counts()
    sns.barplot(x=tx_counts.index, y=tx_counts.values)
    plt.title("Distribution of Transaction Types")
    plt.xlabel("Transaction Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    return plt

def visualize_kyc_status(kyc_data):
    """Visualize the distribution of KYC verification statuses"""
    plt.figure(figsize=(10, 6))
    status_counts = kyc_data["verification_status"].value_counts()
    plt.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
    plt.title("Distribution of KYC Verification Statuses")
    return plt

def visualize_transfer_types(transfer_data):
    """Visualize the distribution of transfer types"""
    plt.figure(figsize=(10, 6))
    transfer_counts = transfer_data["transfer_type"].value_counts()
    sns.barplot(x=transfer_counts.index, y=transfer_counts.values)
    plt.title("Distribution of Transfer Types")
    plt.xlabel("Transfer Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    return plt

def create_csv_files(customer_data, kyc_data, account_data, transaction_data, transfer_data):
    """Create downloadable CSV files"""
    customer_csv = customer_data.to_csv(index=False)
    kyc_csv = kyc_data.to_csv(index=False)
    account_csv = account_data.to_csv(index=False)
    transaction_csv = transaction_data.to_csv(index=False)
    transfer_csv = transfer_data.to_csv(index=False)
    
    # Create a zip file containing all CSVs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("customer_data.csv", customer_csv)
        zip_file.writestr("kyc_data.csv", kyc_csv)
        zip_file.writestr("account_data.csv", account_csv)
        zip_file.writestr("transaction_data.csv", transaction_csv)
        zip_file.writestr("transfer_data.csv", transfer_csv)
    
    return zip_buffer.getvalue()

def create_json_files(customer_data, kyc_data, account_data, transaction_data, transfer_data):
    """Create downloadable JSON files"""
    customer_json = customer_data.to_json(orient="records")
    kyc_json = kyc_data.to_json(orient="records")
    account_json = account_data.to_json(orient="records")
    transaction_json = transaction_data.to_json(orient="records")
    transfer_json = transfer_data.to_json(orient="records")
    
    # Create a zip file containing all JSONs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("customer_data.json", customer_json)
        zip_file.writestr("kyc_data.json", kyc_json)
        zip_file.writestr("account_data.json", account_json)
        zip_file.writestr("transaction_data.json", transaction_json)
        zip_file.writestr("transfer_data.json", transfer_json)
    
    return zip_buffer.getvalue()

def save_data_to_disk(customer_data, kyc_data, account_data, transaction_data, transfer_data, output_dir=OUTPUT_DIR):
    """Save all generated data to disk"""
    try:
        customer_data.to_csv(f"{output_dir}/customer_data.csv", index=False)
        kyc_data.to_csv(f"{output_dir}/kyc_data.csv", index=False)
        account_data.to_csv(f"{output_dir}/account_data.csv", index=False)
        transaction_data.to_csv(f"{output_dir}/transaction_data.csv", index=False)
        transfer_data.to_csv(f"{output_dir}/transfer_data.csv", index=False)
        
        # Also save as JSON for API-like access
        customer_data.to_json(f"{output_dir}/customer_data.json", orient="records", indent=2)
        kyc_data.to_json(f"{output_dir}/kyc_data.json", orient="records", indent=2)
        account_data.to_json(f"{output_dir}/account_data.json", orient="records", indent=2)
        transaction_data.to_json(f"{output_dir}/transaction_data.json", orient="records", indent=2)
        transfer_data.to_json(f"{output_dir}/transfer_data.json", orient="records", indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

# UI Functions
def generate_data(num_customers, avg_accounts, avg_transactions, num_transfers, progress=gr.Progress()):
    """Generate synthetic banking data with progress tracking"""
    global app_state
    
    progress(0, desc="Starting data generation...")
    start_time = time.time()
    
    # Generate customer data
    progress(0.1, desc="Generating customer data...")
    customer_data = generate_customer_data(num_customers=num_customers)
    app_state.customer_data = customer_data
    app_state.generation_stats["customers"] = len(customer_data)
    
    # Generate KYC data
    progress(0.25, desc="Generating KYC data...")
    kyc_data = generate_kyc_data(customer_data)
    app_state.kyc_data = kyc_data
    app_state.generation_stats["kyc"] = len(kyc_data)
    
    # Generate account data
    progress(0.4, desc="Generating account data...")
    account_data = generate_account_data(customer_data, avg_accounts_per_customer=avg_accounts)
    app_state.account_data = account_data
    app_state.generation_stats["accounts"] = len(account_data)
    
    # Generate transaction data
    progress(0.6, desc="Generating transaction data...")
    transaction_data = generate_transaction_data(account_data, avg_transactions_per_account=avg_transactions)
    app_state.transaction_data = transaction_data
    app_state.generation_stats["transactions"] = len(transaction_data)
    
    # Generate transfer data
    progress(0.8, desc="Generating transfer data...")
    transfer_data = generate_transfer_data(account_data, customer_data, num_transfers=num_transfers)
    app_state.transfer_data = transfer_data
    app_state.generation_stats["transfers"] = len(transfer_data)
    
    # Save data to disk
    progress(0.9, desc="Saving data...")
    save_data_to_disk(customer_data, kyc_data, account_data, transaction_data, transfer_data)
    
    end_time = time.time()
    generation_time = round(end_time - start_time, 2)
    app_state.generation_stats["generation_time"] = generation_time
    
    progress(1.0, desc="Data generation complete!")
    
    # Create summary
    summary = f"""
    ## Banking Synthetic Data Generation Summary
    
    - **Customers**: {app_state.generation_stats.get('customers', 0)}
    - **KYC Records**: {app_state.generation_stats.get('kyc', 0)}
    - **Accounts**: {app_state.generation_stats.get('accounts', 0)}
    - **Transactions**: {app_state.generation_stats.get('transactions', 0)}
    - **Transfers**: {app_state.generation_stats.get('transfers', 0)}
    - **Generation Time**: {app_state.generation_stats.get('generation_time', 0)} seconds
    
    Data has been saved to the `{OUTPUT_DIR}` directory.
    """
    
    return summary

def update_visualizations():
    """Update all visualizations based on current data"""
    if app_state.customer_data is None:
        return None, None, None, None, None, None
    
    age_plot = visualize_customer_age_distribution(app_state.customer_data)
    income_plot = visualize_income_distribution(app_state.customer_data)
    account_plot = visualize_account_types(app_state.account_data)
    transaction_plot = visualize_transaction_types(app_state.transaction_data)
    kyc_plot = visualize_kyc_status(app_state.kyc_data)
    transfer_plot = visualize_transfer_types(app_state.transfer_data)
    
    return age_plot, income_plot, account_plot, transaction_plot, kyc_plot, transfer_plot

def get_customer_sample():
    """Get a formatted sample of customer data"""
    if app_state.customer_data is None:
        return "No data generated yet."
    
    sample = app_state.customer_data.head(5).to_markdown()
    return f"## Customer Data Sample\n\n{sample}"

def get_kyc_sample():
    """Get a formatted sample of KYC data"""
    if app_state.kyc_data is None:
        return "No data generated yet."
    
    sample = app_state.kyc_data.head(5).to_markdown()
    return f"## KYC Data Sample\n\n{sample}"

def get_account_sample():
    """Get a formatted sample of account data"""
    if app_state.account_data is None:
        return "No data generated yet."
    
    sample = app_state.account_data.head(5).to_markdown()
    return f"## Account Data Sample\n\n{sample}"

def get_transaction_sample():
    """Get a formatted sample of transaction data"""
    if app_state.transaction_data is None:
        return "No data generated yet."
    
    sample = app_state.transaction_data.head(5).to_markdown()
    return f"## Transaction Data Sample\n\n{sample}"

def get_transfer_sample():
    """Get a formatted sample of transfer data"""
    if app_state.transfer_data is None:
        return "No data generated yet."
    
    sample = app_state.transfer_data.head(5).to_markdown()
    return f"## Transfer Data Sample\n\n{sample}"

def get_csv_download():
    """Prepare CSV files for download"""
    if app_state.customer_data is None:
        return None
    
    return create_csv_files(
        app_state.customer_data,
        app_state.kyc_data,
        app_state.account_data,
        app_state.transaction_data,
        app_state.transfer_data
    )

def get_json_download():
    """Prepare JSON files for download"""
    if app_state.customer_data is None:
        return None
    
    return create_json_files(
        app_state.customer_data,
        app_state.kyc_data,
        app_state.account_data,
        app_state.transaction_data,
        app_state.transfer_data
    )

# Create the Gradio interface
def create_app():
    with gr.Blocks(title="Banking Synthetic Data Generator") as app:
        gr.Markdown("""
        # 🏦 Banking Synthetic Data Generator
        
        Generate realistic synthetic data for banking applications, including customer profiles, KYC records, accounts, transactions, and fund transfers.
        
        This tool is perfect for:
        - Application testing and development
        - ML/AI model training
        - Demo data for banking applications
        - Simulating various banking scenarios
        """)
        
        with gr.Tab("Generate Data"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Data Generation Parameters")
                    
                    num_customers = gr.Slider(
                        label="Number of Customers",
                        minimum=10,
                        maximum=1000,
                        value=100,
                        step=10
                    )
                    
                    avg_accounts = gr.Slider(
                        label="Average Accounts per Customer",
                        minimum=1,
                        maximum=5,
                        value=1.5,
                        step=0.1
                    )
                    
                    avg_transactions = gr.Slider(
                        label="Average Transactions per Account",
                        minimum=5,
                        maximum=100,
                        value=20,
                        step=5
                    )
                    
                    num_transfers = gr.Slider(
                        label="Number of Fund Transfers",
                        minimum=10,
                        maximum=1000,
                        value=200,
                        step=10
                    )
                    
                    generate_btn = gr.Button("Generate Synthetic Data", variant="primary")
                
                with gr.Column():
                    output_summary = gr.Markdown("Generation summary will appear here.")
            
            generate_btn.click(
                fn=generate_data,
                inputs=[num_customers, avg_accounts, avg_transactions, num_transfers],
                outputs=[output_summary]
            )
        
        with gr.Tab("Visualizations"):
            refresh_viz_btn = gr.Button("Refresh Visualizations")
            
            with gr.Row():
                age_plot = gr.Plot(label="Customer Age Distribution")
                income_plot = gr.Plot(label="Customer Income Distribution")
            
            with gr.Row():
                account_plot = gr.Plot(label="Account Types Distribution")
                kyc_plot = gr.Plot(label="KYC Status Distribution")
            
            with gr.Row():
                transaction_plot = gr.Plot(label="Transaction Types Distribution")
                transfer_plot = gr.Plot(label="Transfer Types Distribution")
            
            refresh_viz_btn.click(
                fn=update_visualizations,
                inputs=[],
                outputs=[age_plot, income_plot, account_plot, transaction_plot, kyc_plot, transfer_plot]
            )
        
        with gr.Tab("Data Samples"):
            refresh_samples_btn = gr.Button("Refresh Data Samples")
            
            with gr.Accordion("Customer Data", open=True):
                customer_sample = gr.Markdown("No data generated yet.")
            
            with gr.Accordion("KYC Data"):
                kyc_sample = gr.Markdown("No data generated yet.")
            
            with gr.Accordion("Account Data"):
                account_sample = gr.Markdown("No data generated yet.")
            
            with gr.Accordion("Transaction Data"):
                transaction_sample = gr.Markdown("No data generated yet.")
            
            with gr.Accordion("Transfer Data"):
                transfer_sample = gr.Markdown("No data generated yet.")
            
            refresh_samples_btn.click(
                fn=lambda: (
                    get_customer_sample(),
                    get_kyc_sample(),
                    get_account_sample(),
                    get_transaction_sample(),
                    get_transfer_sample()
                ),
                inputs=[],
                outputs=[customer_sample, kyc_sample, account_sample, transaction_sample, transfer_sample]
            )
        
        with gr.Tab("Download Data"):
            gr.Markdown("""
            ### Download Generated Data
            
            Download all the synthetic data as CSV or JSON files. The files will be packaged in a ZIP archive.
            """)
            
            with gr.Row():
                csv_btn = gr.Button("Download as CSV")
                json_btn = gr.Button("Download as JSON")
            
            with gr.Row():
                csv_download = gr.File(label="CSV Download")
                json_download = gr.File(label="JSON Download")
            
            csv_btn.click(fn=get_csv_download, inputs=[], outputs=[csv_download])
            json_btn.click(fn=get_json_download, inputs=[], outputs=[json_download])
        
        with gr.Tab("API Documentation"):
            gr.Markdown("""
            # API Documentation
            
            This synthetic data generator also creates JSON files that can be used as a mock API. The data is stored in the `synthetic_data_output` directory.
            
            ## Available Endpoints
            
            - `/customer_data.json` - Customer profiles with personal information
            - `/kyc_data.json` - Know Your Customer verification records
            - `/account_data.json` - Bank account information
            - `/transaction_data.json` - Transaction records
            - `/transfer_data.json` - Fund transfer records
            
            ## Data Relationships
            
            - Each customer can have multiple accounts (joined by `customer_id`)
            - Each customer has one KYC record (joined by `customer_id`)
            - Each account can have multiple transactions (joined by `account_id`)
            - Fund transfers can be linked to source accounts (joined by `source_account_id`)
            
            ## Sample Usage
            
            ```python
            import requests
            import pandas as pd
            
            # Assuming the files are served via a web server
            base_url = "http://your-server/synthetic_data_output"
            
            # Get customer data
            customers = pd.read_json(f"{base_url}/customer_data.json")
            
            # Get accounts for a specific customer
            customer_id = customers.iloc[0]["customer_id"]
            accounts = pd.read_json(f"{base_url}/account_data.json")
            customer_accounts = accounts[accounts["customer_id"] == customer_id]
            
            # Get transactions for a specific account
            account_id = customer_accounts.iloc[0]["account_id"]
            transactions = pd.read_json(f"{base_url}/transaction_data.json")
            account_transactions = transactions[transactions["account_id"] == account_id]
            ```
            
            ## Data Schema
            
            Each data file follows a consistent schema with appropriate fields for its entity type. Refer to the Data Samples tab for examples of each data type.
            """)
    
    return app

# Launch the app
def main():
    app = create_app()
    app.launch(server_name="0.0.0.0")

if __name__ == "__main__":
    main()
