import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import Database
from datetime import date, timedelta
import calendar

def report_page():
    st.title("Expenses Report")

    db = Database()

    report_type = st.radio("Select Report Type", ["Expenses by Amount", "Expenses by Category", "Expenses by Tag"], horizontal=True)

    time_period = st.slider("Select Time Period (Months)", min_value=1, max_value=12, value=3)

    end_date = date.today().replace(day=1) + timedelta(days=32)
    end_date = end_date.replace(day=1) - timedelta(days=1)
    start_date = (end_date - timedelta(days=30 * time_period)).replace(day=1)

    if report_type == "Expenses by Amount":
        expenses_by_month = db.get_expenses_by_month(time_period)
        if not expenses_by_month:
            st.warning("No data available for the selected time period.")
            return
        
        df = pd.DataFrame(expenses_by_month, columns=['Month', 'Expenses'])
        df['Month'] = pd.to_datetime(df['Month'])
        df = df.sort_values('Month')
        
        # Ensure we only have the last 'time_period' months
        df = df.tail(time_period)
        
        fig = px.bar(df, x='Month', y='Expenses', text='Expenses',
                     title=f"Expenses for the Last {time_period} Months")
        fig.update_traces(marker_color='royalblue', marker_line_color='darkblue',
                          marker_line_width=1.5, opacity=0.8,
                          texttemplate='%{text:.2f}', textposition='outside')
        fig.update_xaxes(
            tickmode='array',
            tickvals=df['Month'],
            ticktext=[d.strftime('%b %Y') for d in df['Month']],
            tickangle=45
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Expenses (€)",
            xaxis={'categoryorder':'category ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Expenses by Category":
        expenses_by_category = db.get_expenses_by_category_and_month(start_date, end_date)
        if not expenses_by_category:
            st.warning("No data available for the selected time period.")
            return
        
        df = pd.DataFrame(expenses_by_category, columns=['Month', 'Category', 'Expenses'])
        df['Month'] = pd.to_datetime(df['Month'])
        df = df.sort_values('Month')

        date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
        
        df_pivot = df.pivot(index='Month', columns='Category', values='Expenses').reindex(date_range).fillna(0)

        fig = go.Figure()
        for category in df_pivot.columns:
            fig.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot[category],
                name=category,
                text=df_pivot[category].round(2),
                textposition='inside'
            ))

        fig.update_layout(
            barmode='stack',
            title=f"Expenses by Category for the Last {time_period} Months",
            xaxis_title="Month",
            yaxis_title="Total Amount (€)",
            legend_title="Category",
            xaxis=dict(
                tickmode='array',
                tickvals=df_pivot.index,
                ticktext=[d.strftime('%b %Y') for d in df_pivot.index]
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Expenses by Tag
        transactions = db.get_transactions_with_tags(start_date, end_date)
        if not transactions:
            st.warning("No data available for the selected time period.")
            return
        
        df = pd.DataFrame(transactions, columns=['Month', 'Tags', 'Amount'])
        df['Month'] = pd.to_datetime(df['Month'])
        
        df['Tags'] = df['Tags'].str.split(',')
        df = df.explode('Tags')
        df['Tags'] = df['Tags'].str.strip()
        
        df_grouped = df.groupby(['Month', 'Tags'])['Amount'].sum().reset_index()
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
        
        df_pivot = df_grouped.pivot(index='Month', columns='Tags', values='Amount').reindex(date_range).fillna(0)

        fig = go.Figure()
        for tag in df_pivot.columns:
            fig.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot[tag],
                name=tag,
                text=df_pivot[tag].round(2),
                textposition='inside'
            ))

        fig.update_layout(
            barmode='stack',
            title=f"Expenses by Tag for the Last {time_period} Months",
            xaxis_title="Month",
            yaxis_title="Total Amount (€)",
            legend_title="Tag",
            xaxis=dict(
                tickmode='array',
                tickvals=df_pivot.index,
                ticktext=[d.strftime('%b %Y') for d in df_pivot.index]
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    fig.update_layout(font=dict(family="Arial", size=14),
                      plot_bgcolor='rgba(0,0,0,0)')