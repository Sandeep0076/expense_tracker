import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd

def create_monthly_expense_chart(data):
    if not data:
        fig = go.Figure()
        fig.add_annotation(text="No expense data available for this month", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    else:
        # Convert data to DataFrame
        df = pd.DataFrame(data, columns=['day', 'cumulative_total'])
        df['day'] = df['day'].astype(int)
        
        # Get the current month and year
        current_date = date.today()
        year, month = current_date.year, current_date.month
        
        # Create a date range for the entire month
        start_date = date(year, month, 1)
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Create a full DataFrame with all days of the month
        full_df = pd.DataFrame({'date': date_range, 'day': date_range.day})
        
        # Merge with the expense data and fill missing values
        df = pd.merge(full_df, df, on='day', how='left').ffill().fillna(0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['cumulative_total'], 
            mode='lines+markers',
            line=dict(color='#1E90FF', width=2),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Cumulative Amount: $%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Cumulative Monthly Expenses',
        xaxis_title='Date',
        yaxis_title='Cumulative Amount ($)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(200,200,200,0.2)'),
        xaxis=dict(
            gridcolor='rgba(200,200,200,0.2)',
            tickformat='%b %d',
            tickmode='auto',
            nticks=10
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=400,
        width=700,
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='rgba(0,0,0,0.1)', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='rgba(0,0,0,0.1)', mirror=True)
    return fig


def create_expense_category_chart(data):
    if not data:
        fig = go.Figure()
        fig.add_annotation(text="No expense data available for this period", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    else:
        categories, amounts = zip(*data)
        fig = px.pie(
            names=categories,
            values=amounts,
            title='Expenses by Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig