import streamlit as st
import base64
import plotly.graph_objects as go


def set_background():
    # Add CSS to set the background image and style the charts
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{base64.b64encode(open('background.png', 'rb').read()).decode()}");
            background-size: cover;
        }}
        .stPlotlyChart > div {{
            background-color: rgba(255, 255, 255, 0.7) !important;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def create_sidebar(change_page_callback):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.7) !important;
        }
        [data-testid="stSidebarNav"] {
            background-color: rgba(255, 255, 255, 0.0) !important;
        }
        .css-1d391kg {
            background-color: rgba(255, 255, 255, 0.0) !important;
        }
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            background-color: rgba(255, 255, 255, 0.5) !important;
        }
        .css-1wbqy5l {
            color: rgba(0, 0, 0, 0.8) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.sidebar:
        st.image("logo.png", width=100)
        st.title("MENU")
        if st.button("Dashboard", key="sidebar_dashboard"):
            change_page_callback('dashboard')
        st.markdown("### REPORTS")
        if st.button("Transactions", key="sidebar_transactions"):
            change_page_callback('transactions')
        if st.button("Report 2", key="sidebar_report2"):
            change_page_callback('report2')
        if st.button("Notes", key="sidebar_notes"):
            change_page_callback('notes')
        if st.button("Calendar", key="sidebar_calendar"):
            change_page_callback('calendar')
        st.markdown("### TRANSACTIONS")
        if st.button("Add Transaction", key="sidebar_add_transaction"):
            change_page_callback('add_transaction')
        if st.button("Upload Receipt", key="sidebar_receipt_analysis"):
            change_page_callback('receipt_analysis')

def create_add_transaction_form():
    with st.form("add_transaction"):
        st.subheader("Add Transaction")
        item = st.text_input("Item")
        item_type = st.text_input("Item Type")
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", [
            "Housing", "Utilities", "Transportation", "Groceries", "Healthcare",
            "Insurance", "Savings and Investments", "Debt Repayment",
            "Personal Care", "Entertainment and Leisure", "Income", "Other"
        ])
        store_name = st.text_input("Store Name")
        date = st.date_input("Date")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        submitted = st.form_submit_button("Add Transaction")
        return submitted, item, item_type, amount, category, store_name, date, quantity

def create_metric_card(title, value, color, budget):
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.7);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            height: 240px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
        ">
            <h3 style="color: #333; margin-bottom: 10px;">{title}</h3>
            <h2 style="color: {color}; font-size: 2.5em; margin: 0;">${value:.2f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )