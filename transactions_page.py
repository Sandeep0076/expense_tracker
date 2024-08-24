import streamlit as st
import pandas as pd
from database import Database
from datetime import datetime, timedelta, date
import calendar

def transactions_page():
    st.markdown("<h1 style='text-align: center; font-size: 2.5em; font-weight: bold;'>Transactions</h1>", unsafe_allow_html=True)
    
    db = Database()
    categories = db.get_categories()
    
    category_colors = {
        'Housing': '#FF9999',
        'Utilities': '#66B2FF',
        'Transportation': '#99FF99',
        'Groceries': '#FFCC99',
        'Healthcare': '#FF99CC',
        'Insurance': '#99CCFF',
        'Savings and Investments': '#CCFF99',
        'Debt Repayment': '#FF99FF',
        'Personal Care': '#99FFCC',
        'Entertainment and Leisure': '#FFFF99',
        'Income': '#C2C2F0',
        'Other': '#E0E0E0'
    }
    
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:first-child button {
        width: 100%;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### Category Color Legend")
    
    cols = st.columns(4)
    for idx, (category, color) in enumerate(category_colors.items()):
        with cols[idx % 4]:
            st.markdown(
                f'<div style="background-color: {color}; padding: 2px; border-radius: 5px; margin-bottom: 2px; text-align: center;">'
                f'<span style="color: black;">{category}</span>'
                '</div>',
                unsafe_allow_html=True
            )
            if st.button(f"Select {category}", key=f"btn_{category}", use_container_width=True):
                st.session_state.selected_category = category
    
    if st.button("Clear Filter", use_container_width=True):
        st.session_state.selected_category = ''
    
    selected_category = st.session_state.get('selected_category', '')

    time_period = st.select_slider("Select Time Period", options=[1, 2, 4, 6, 12], value=1, format_func=lambda x: f"{x} month{'s' if x > 1 else ''}")
    
    today = date.today()
    end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    start_date = (end_date - timedelta(days=30*time_period)).replace(day=1)
    
    transactions = db.get_transactions()

    if not transactions:
        st.info("No transactions available. Add some transactions to see them here.")
    else:
        df = pd.DataFrame(transactions, columns=['Item', 'Tags', 'Amount', 'Category', 'Store Name', 'Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter by date range
        df = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]
        
        # Filter by selected category
        if selected_category:
            df = df[df['Category'] == selected_category]

        if df.empty:
            st.info(f"No transactions found for the selected period and category.")
        else:
            def color_categories(val):
                return f'background-color: {category_colors.get(val, "#E0E0E0")}'
            
            styled_df = df.style.applymap(color_categories, subset=['Category'])
            styled_df = styled_df.format({'Date': lambda x: x.strftime('%Y-%m-%d')})
            
            st.dataframe(styled_df, height=600, use_container_width=True)

        st.write(f"Current filter: {selected_category if selected_category else 'None'}")
        st.write(f"Showing transactions from {start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}")
    
    if 'transactions_updated' in st.session_state and st.session_state.transactions_updated:
        st.success("Transactions have been updated!")
        st.session_state.transactions_updated = False