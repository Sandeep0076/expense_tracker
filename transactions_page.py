import streamlit as st
import pandas as pd
from database import Database

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
    
    st.markdown(f"""
    <style>
    .dataframe {{
        font-size: 16px;
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        overflow: hidden;
        width: 150% !important;
    }}
    .dataframe th {{
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        text-align: left;
        padding: 15px;
        font-size: 18px;
    }}
    .dataframe td {{
        padding: 15px;
    }}
    .dataframe tr:nth-child(even) {{
        background-color: rgba(242, 242, 242, 0.5);
    }}
    .category-button {{
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        border-radius: 5px;
        cursor: pointer;
        color: black;
    }}
    {' '.join([f'.btn-{category.lower().replace(" ", "-")} {{background-color: {color};}}' for category, color in category_colors.items()])}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### Category Color Legend")
    
    cols = st.columns(4)
    for idx, category in enumerate(categories):
        if cols[idx % 4].button(category, key=f"btn_{category}", 
                                use_container_width=True, 
                                help=f"Filter by {category}"):
            st.session_state.selected_category = category

    if st.button("Clear Filter", use_container_width=True):
        st.session_state.selected_category = ''
    
    transactions = db.get_transactions()

    if not transactions:
        st.info("No transactions available. Add some transactions to see them here.")
    else:
        df = pd.DataFrame(transactions, columns=['Item', 'Item Type', 'Amount', 'Category', 'Store Name', 'Date'])
        
        if 'selected_category' in st.session_state and st.session_state.selected_category:
            filtered_df = df[df['Category'] == st.session_state.selected_category]
        else:
            filtered_df = df

        if filtered_df.empty:
            st.info(f"No transactions found for the category: {st.session_state.selected_category}")
        else:
            def color_categories(val):
                return f'background-color: {category_colors.get(val, "#E0E0E0")}'
            
            styled_df = filtered_df.style.applymap(color_categories, subset=['Category'])
            
            st.dataframe(styled_df, height=600, use_container_width=True)

        st.write(f"Current filter: {st.session_state.selected_category if 'selected_category' in st.session_state and st.session_state.selected_category else 'None'}")
    
    if 'transactions_updated' in st.session_state and st.session_state.transactions_updated:
        st.success("Transactions have been updated!")
        st.session_state.transactions_updated = False