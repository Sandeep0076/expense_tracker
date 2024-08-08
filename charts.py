import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

def create_monthly_expense_chart(data):
    if not data:
        fig = go.Figure()
        fig.add_annotation(text="No expense data available for this month", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    else:
        dates, amounts = zip(*data)
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        sorted_data = sorted(zip(dates, amounts))
        sorted_dates, sorted_amounts = zip(*sorted_data)
        cumulative_amounts = np.cumsum(sorted_amounts)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sorted_dates, y=cumulative_amounts, mode='lines+markers', line=dict(color='#1E90FF', width=2)))
    
    fig.update_layout(
        title='Monthly Expenses',
        xaxis_title='Date',
        yaxis_title='Cumulative Amount',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(200,200,200,0.2)'),
        xaxis=dict(gridcolor='rgba(200,200,200,0.2)'),
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
        margin=dict(l=40, r=40, t=40, b=40),
        height=400,
        width=500,
    )
    return fig