import streamlit as st
from database import Database
from ui_components import create_metric_card, create_sidebar, create_add_transaction_form, set_background
from charts import create_monthly_expense_chart, create_expense_category_chart
from datetime import datetime, timedelta
import os
from transactions_page import transactions_page
from receipt_analysis import receipt_analysis_page

st.set_page_config(layout="wide", page_title="Expense Tracker")

db = Database()

def reset_data():
    db.clear_all_data()
    #db.populate_with_artificial_data()
    st.success("Data has been reset!")
    #st.experimental_rerun()

def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>Expense Tracker Dashboard</h1>", unsafe_allow_html=True)

    col1, col2, col3, col_reset = st.columns([1, 1, 1, 0.2])
    
    with col1:
        create_metric_card("BALANCE", db.get_balance(), "#FF6B6B", budget=15000)
    with col2:
        create_metric_card("LOAN", db.get_loan(), "#4ECB71", budget=10000)
    with col3:
        create_metric_card("SAVINGS", db.get_savings(), "#FFA500", budget=2000)
    with col_reset:
        st.button("Reset Data", key="reset_data", on_click=reset_data)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Monthly Expenses")
        current_date = datetime.now()
        monthly_expenses = db.get_monthly_expenses(current_date.year, current_date.month)
        fig_monthly = create_monthly_expense_chart(monthly_expenses)
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col_right:
        st.subheader("Expenses by Category")
        start_date = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = current_date.strftime('%Y-%m-%d')
        expenses_by_category = db.get_expenses_by_category(start_date, end_date)
        fig_category = create_expense_category_chart(expenses_by_category)
        st.plotly_chart(fig_category, use_container_width=True)

def add_transaction_page():
    st.markdown("<h1 style='text-align: center;'>Add Transaction</h1>", unsafe_allow_html=True)
    submitted, item, item_type, amount, category, store_name, date, quantity = create_add_transaction_form()
    if submitted:
        db = Database()
        # Determine transaction type based on category
        transaction_type = 'income' if category == 'Income' else 'expense'
        db.add_transaction(amount, category, date.strftime('%Y-%m-%d'), transaction_type, store_name, item, item_type, quantity)
        st.success("Transaction added successfully! Refresh the page to see updated data.")

def main():
    if os.path.exists('background.png'):
        set_background()
    else:
        st.warning("Background image not found. Using default background.")

    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'

    create_sidebar(change_page)

    if st.session_state.page == 'add_transaction':
        add_transaction_page()
    elif st.session_state.page == 'dashboard':
        main_dashboard()
    elif st.session_state.page == 'transactions':
        transactions_page()
    elif st.session_state.page == 'receipt_analysis':
        receipt_analysis_page()

def change_page(page):
    st.session_state.page = page

if __name__ == "__main__":
    main()