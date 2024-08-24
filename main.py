import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from ui_components import create_metric_card, create_sidebar, create_add_transaction_form, set_background
from charts import create_monthly_expense_chart, create_expense_category_chart
from datetime import date, timedelta
import os
from transactions_page import transactions_page
from receipt_analysis import receipt_analysis_page, parse_quantity
from calendar_component import calendar_page
from report_page import report_page



st.set_page_config(layout="wide", page_title="Expense Tracker")

db = Database()

def reset_data():
    db.clear_all_data()
    st.success("Data has been reset!")
    st.session_state.data_changed = True

def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>Expense Tracker Dashboard</h1>", unsafe_allow_html=True)

    col1, col2, col3, col_reset = st.columns([1, 1, 1, 0.2])
    
    current_date = date.today()
    monthly_budget = 500
    monthly_spending = db.get_monthly_spending(current_date.year, current_date.month)
    budget_left = monthly_budget - monthly_spending
    
    with col1:
        create_metric_card("BUDGET", budget_left, "#FF6B6B" if budget_left < 0 else "#4ECB71", budget=monthly_budget)
    with col2:
        create_metric_card("LOAN", db.get_loan(), "#4ECB71", budget=15000)
    with col3:
        create_metric_card("SAVINGS", db.get_savings(), "#FFA500", budget=8000)
    with col_reset:
        st.button("Reset Data", key="reset_data", on_click=reset_data)

    chart_height = 400  # Set a fixed height for both charts

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Monthly Expenses")
        current_date = date.today()
        start_date = current_date.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        daily_expenses = db.get_daily_spending(start_date, end_date)
        
        df = pd.DataFrame(daily_expenses, columns=['Date', 'Amount'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        fig = px.bar(df, x='Date', y='Amount',
                    title=f"Daily Expenses for {current_date.strftime('%B %Y')}",
                    labels={'Date': 'Date', 'Amount': 'Total Spent (€)'},
                    text='Amount',
                    height=chart_height,
                    color='Amount',
                    color_continuous_scale=px.colors.qualitative.Set3)
        
        fig.update_traces(texttemplate='%{text:.2f}€', textposition='outside')
        fig.update_xaxes(tickformat='%d %b')
        fig.update_layout(
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black'),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with col_right:
        st.subheader("Expenses by Category")
        start_date = current_date - timedelta(days=30)
        end_date = current_date
        expenses_by_category = db.get_expenses_by_category(start_date, end_date)
        
        df_category = pd.DataFrame(expenses_by_category, columns=['Category', 'Amount'])
        
        fig_category = px.pie(df_category, values='Amount', names='Category', 
                            title='Expenses by Category',
                            height=chart_height,
                            color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig_category.update_traces(textposition='inside', 
                                texttemplate='%{label}<br>€%{value:.2f}',
                                hovertemplate='<b>%{label}</b><br>Amount: €%{value:.2f}<br>%{percent}')
        
        fig_category.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig_category, use_container_width=True)

def add_transaction_callback():
    st.session_state.transaction_submitted = True

def add_transaction_page():
    st.markdown("<h1 style='text-align: center;'>Add Transaction</h1>", unsafe_allow_html=True)
    
    message_container = st.empty()
    
    submitted, item, tags, amount, category, store_name, date, quantity = create_add_transaction_form()
    
    if submitted:
        db = Database()
        transaction_type = 'income' if category == 'Income' else 'expense'
        db.add_transaction(amount, category, date, transaction_type, store_name, item, tags, parse_quantity(quantity))
        
        message_container.success("Transaction added successfully!")
        st.session_state.data_changed = True

def change_page(page):
    st.session_state.page = page




def main():
    if 'data_changed' not in st.session_state:
        st.session_state.data_changed = False

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
    elif st.session_state.page == 'calendar':
        calendar_page()
    elif st.session_state.page == 'expense_report':
        report_page()

if __name__ == "__main__":
    main()