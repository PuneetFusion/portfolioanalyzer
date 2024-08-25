import streamlit as st
import pandas as pd
import yfinance as yf

def analyze_portfolio(portfolio):
    # Placeholder for actual analysis logic
    total_equity = sum(holding['percentage'] for holding in portfolio if holding['type'] == 'Equity')
    total_fixed_income = sum(holding['percentage'] for holding in portfolio if holding['type'] == 'Fixed Income')
    total_cash = sum(holding['percentage'] for holding in portfolio if holding['type'] == 'Cash')
    
    risk_level = "moderate"
    if total_equity > 70:
        risk_level = "aggressive"
    elif total_equity < 30:
        risk_level = "conservative"
    
    return {
        'equity_percentage': total_equity,
        'fixed_income_percentage': total_fixed_income,
        'cash_percentage': total_cash,
        'risk_level': risk_level
    }

def generate_summary(analysis):
    summary = f"""
    This portfolio is designed with a {analysis['risk_level']} approach to investing. 
    It consists of {analysis['equity_percentage']:.1f}% in stocks, which provide potential for growth, 
    {analysis['fixed_income_percentage']:.1f}% in bonds, which offer stability and income, 
    and {analysis['cash_percentage']:.1f}% in cash for liquidity. 
    This mix aims to balance the potential for returns with a level of risk that may be suitable for many investors. 
    Remember, all investments carry risk, and it's important to consider your personal financial goals and risk tolerance.
    """
    return summary.strip()

st.title('Portfolio Analysis App')

st.write("""
Enter your portfolio details below. For each holding, provide:
1. The ticker symbol (e.g., AAPL for Apple Inc.)
2. The percentage of your portfolio it represents (e.g., 10 for 10%)
3. The type of security (Equity, Fixed Income, or Cash)
""")

num_holdings = st.number_input('Number of holdings in your portfolio', min_value=1, max_value=20, value=5)

portfolio = []

for i in range(num_holdings):
    st.subheader(f'Holding {i+1}')
    ticker = st.text_input(f'Ticker Symbol for Holding {i+1}', key=f'ticker_{i}')
    percentage = st.number_input(f'Percentage for Holding {i+1}', min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f'percentage_{i}')
    security_type = st.selectbox(f'Type of Security for Holding {i+1}', ['Equity', 'Fixed Income', 'Cash'], key=f'type_{i}')
    
    portfolio.append({
        'ticker': ticker,
        'percentage': percentage,
        'type': security_type
    })

if st.button('Analyze Portfolio'):
    total_percentage = sum(holding['percentage'] for holding in portfolio)
    
    if abs(total_percentage - 100) > 0.01:
        st.error(f'Error: Your total portfolio percentage is {total_percentage}%. It should add up to 100%.')
    else:
        analysis = analyze_portfolio(portfolio)
        summary = generate_summary(analysis)
        
        st.subheader('Portfolio Summary')
        st.write(summary)

st.write("""
Note: This is a simplified analysis and should not be considered financial advice. 
Always consult with a qualified financial advisor before making investment decisions.
""")