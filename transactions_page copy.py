import streamlit as st
import pandas as pd
from database import Database

def transactions_page():
    st.markdown("<h1 style='text-align: center; font-size: 2.5em; font-weight: bold;'>Transactions</h1>", unsafe_allow_html=True)
    
    db = Database()
    
    db.cursor.execute('SELECT COUNT(*) FROM transactions')
    count = db.cursor.fetchone()[0]
    
    if count == 0:
        st.info("No transactions available. Add some transactions to see them here.")
    else:
        db.cursor.execute('''
            SELECT item, item_type, amount, category, store_name, date
            FROM transactions
            ORDER BY date DESC
        ''')
        transactions = db.cursor.fetchall()
        
        df = pd.DataFrame(transactions, columns=['Item', 'Item Type', 'Amount', 'Category', 'Store Name', 'Date'])
       
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
    
    # Create category buttons
    cols = st.columns(4)
    for idx, (category, color) in enumerate(category_colors.items()):
        if cols[idx % 4].button(category, key=f"btn_{category}", 
                                use_container_width=True, 
                                help=f"Filter by {category}"):
            st.session_state.selected_category = category

    # Clear filter button
    if st.button("Clear Filter", use_container_width=True):
        st.session_state.selected_category = ''

    # Filter DataFrame based on selected category
    if 'selected_category' in st.session_state and st.session_state.selected_category:
        filtered_df = df[df['Category'] == st.session_state.selected_category]
    else:
        filtered_df = df

    def color_categories(val):
        return f'background-color: {category_colors.get(val, "#E0E0E0")}'
    
    styled_df = filtered_df.style.applymap(color_categories, subset=['Category'])
    
    st.dataframe(styled_df, height=600, use_container_width=True)

    # Display current filter
    st.write(f"Current filter: {st.session_state.selected_category if 'selected_category' in st.session_state and st.session_state.selected_category else 'None'}")