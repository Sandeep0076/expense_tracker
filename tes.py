import streamlit as st
import pandas as pd
import plotly.express as px

# Sample data (replace with your actual data)
data = {
    'Month': ['February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Expenses': [221233.69, 336835.79, 277462.90, 221627.73, 278887.65, 255841.42, 293196.02, 303601.12, 188623.31]
}
df = pd.DataFrame(data)

# Streamlit app
st.set_page_config(page_title="Expense Report", page_icon=":moneybag:", layout="wide")

st.title("Expenses by Month")

# Time period selection slider
time_period = st.slider("Select Time Period (Months)", min_value=3, max_value=len(df), value=6)

# Filter data based on selected time period
df_filtered = df.tail(time_period)

# Create a modern 3D bar chart using Plotly
fig = px.bar(df_filtered, x='Month', y='Expenses', text_auto='.2s', 
             title=f"Expenses for the Last {time_period} Months")

# Customize the chart appearance
fig.update_traces(marker_color='royalblue', marker_line_color='darkblue',
                  marker_line_width=1.5, opacity=0.8)
fig.update_layout(xaxis_title="Month", yaxis_title="Expenses",
                  font=dict(family="Arial", size=14),
                  plot_bgcolor='rgba(0,0,0,0)') 

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True) 