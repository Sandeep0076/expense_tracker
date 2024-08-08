import streamlit as st
import pandas as pd
from database import Database
from PIL import Image
from vision import extract_recipt_info
import json
import re
from datetime import datetime


def save_azure_response(azure_response):
    current_date = datetime.now().strftime("%d-%Y-%m")
    filename = f"receipt_{current_date}.txt"
    os.makedirs("extracted_data", exist_ok=True)
    with open(os.path.join("extracted_data", filename), "w") as f:
        f.write(azure_response)

def process_receipt(receipt_json):
    pattern = r'\[\s*\{[^]]*\}\s*\]'
    matches = re.findall(pattern, receipt_json, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None
def display_editable_transactions(transactions):
    st.subheader("Receipt Analysis Results")
    
    df = pd.DataFrame(transactions)
    edited_df = st.data_editor(df, num_rows="dynamic")
    
    if st.button("Update Transactions", key="update_transactions_button"):
        st.write("Update button clicked!")
        st.write("Edited DataFrame:", edited_df)
        update_transactions(edited_df.to_dict('records'))

def extract_json_array(text):
    pattern = r'\[\s*\{[^]]*\}\s*\]'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            json_array = json.loads(match)
            return json_array
        except json.JSONDecodeError:
            continue
    
    return None


def update_transactions(transactions):
    st.write("Entering update_transactions function")
    db = Database()
    updated_count = 0
    for transaction in transactions:
        try:
            st.write(f"Updating transaction: {transaction}")
            db.add_transaction(
                amount=float(transaction['Amount']),
                category=transaction['Category'],
                date=transaction['Date'],
                type='expense',
                store_name=transaction['Store Name'],
                item=transaction['Item'],
                item_type=transaction['Item Type'],
                quantity=float(transaction['Quantity'])
            )
            updated_count += 1
        except Exception as e:
            st.error(f"Error updating transaction: {str(e)}")
    
    if updated_count > 0:
        st.success(f"Added {updated_count} transactions to the database.")
    else:
        st.warning("No transactions were updated.")




def process_receipt(receipt_json):
    pattern = r'\[\s*\{[^]]*\}\s*\]'
    matches = re.findall(pattern, receipt_json, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None

def extract_numeric_value(value):
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        numeric_part = re.search(r'\d+\.?\d*', value)
        if numeric_part:
            return float(numeric_part.group())
    return 0.0

def receipt_analysis_page():
    st.markdown("<h1 style='text-align: center;'>Receipt Analysis</h1>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Receipt', use_column_width=True)
        
        if st.button('Analyze Receipt'):
            with st.spinner('Analyzing receipt...'):
                try:
                    #azure_response = extract_recipt_info(uploaded_file)
                    file_path = 'extracted_data/receipt_07-2024-08.txt'

                    with open(file_path, 'r') as file:
                        azure_response = file.read()
                    transactions = process_receipt(azure_response)
                    
                    if transactions:
                        # Convert quantities and amounts to numeric values, and dates to datetime
                        for transaction in transactions:
                            transaction['Quantity'] = extract_numeric_value(transaction['Quantity'])
                            transaction['Amount'] = extract_numeric_value(transaction['Amount'])
                            transaction['Date'] = datetime.strptime(transaction['Date'], '%d-%m-%Y').date()
                        
                        st.session_state.transactions = transactions
                        st.success("Receipt analyzed successfully!")
                    else:
                        st.error("Failed to extract transactions from the receipt.")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    
    if 'transactions' in st.session_state:
        st.subheader("Receipt Analysis Results")
        
        df = pd.DataFrame(st.session_state.transactions)
        
        # Create a data editor for all transactions
        edited_df = st.data_editor(
            df,
            column_config={
                "Item": st.column_config.TextColumn("Item"),
                "Item Type": st.column_config.TextColumn("Item Type"),
                "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, format="%.2f"),
                "Amount": st.column_config.NumberColumn("Amount", min_value=0, format="%.2f"),
                "Category": st.column_config.SelectboxColumn("Category", options=['Groceries', 'Personal Care', 'Other']),
                "Store Name": st.column_config.TextColumn("Store Name"),
                "Date": st.column_config.DateColumn("Date"),
            },
            num_rows="dynamic"
        )
        
        if st.button("Update Transactions in Database"):
            db = Database()
            updated_count = 0
            
            for _, row in edited_df.iterrows():
                try:
                    db.add_transaction(
                        amount=float(row['Amount']),
                        category=row['Category'],
                        date=row['Date'].strftime('%d-%m-%Y'),
                        type='expense',
                        store_name=row['Store Name'],
                        item=row['Item'],
                        item_type=row['Item Type'],
                        quantity=float(row['Quantity'])
                    )
                    updated_count += 1
                except Exception as e:
                    st.error(f"Error updating transaction: {str(e)}")
            
            if updated_count > 0:
                st.success(f"Added {updated_count} transactions to the database.")
                del st.session_state.transactions
            else:
                st.warning("No transactions were updated.")
