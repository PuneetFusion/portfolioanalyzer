import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def fetch_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data

def calculate_returns(data):
    returns = data.pct_change().dropna()
    return returns

def calculate_portfolio_metrics(returns, weights):
    portfolio_return = np.sum(returns.mean() * weights) * 252
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility
    return portfolio_return, portfolio_volatility, sharpe_ratio

def analyze_portfolio(portfolio):
    tickers = [holding['ticker'] for holding in portfolio if holding['ticker'].upper() != 'CASH']
    weights = np.array([holding['percentage'] / 100 for holding in portfolio if holding['ticker'].upper() != 'CASH'])
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*3)  # 3 years of historical data
    
    data = fetch_data(tickers, start_date, end_date)
    returns = calculate_returns(data)
    
    portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(returns, weights)
    
    total_equity = sum(holding['percentage'] for holding in portfolio if holding['type'] == 'Equity')
    total_fixed_income = sum(holding['percentage'] for holding in portfolio if holding['type'] == 'Fixed Income')
    total_cash = sum(holding['percentage'] for holding in portfolio if holding['ticker'].upper() == 'CASH')
    
    risk_level = "moderate"
    if total_equity > 70:
        risk_level = "aggressive"
    elif total_equity < 30:
        risk_level = "conservative"
    
    return {
        'equity_percentage': total_equity,
        'fixed_income_percentage': total_fixed_income,
        'cash_percentage': total_cash,
        'risk_level': risk_level,
        'expected_return': portfolio_return,
        'volatility': portfolio_volatility,
        'sharpe_ratio': sharpe_ratio
    }

def generate_summary(analysis):
    summary = f"""
    This portfolio is designed with a {analysis['risk_level']} approach to investing. 
    It consists of {analysis['equity_percentage']:.1f}% in stocks, {analysis['fixed_income_percentage']:.1f}% in bonds, 
    and {analysis['cash_percentage']:.1f}% in cash.
    
    Based on historical data and Modern Portfolio Theory:
    - The expected annual return is {analysis['expected_return']*100:.2f}%
    - The annual volatility (risk) is {analysis['volatility']*100:.2f}%
    - The Sharpe ratio is {analysis['sharpe_ratio']:.2f}
    
    This mix aims to balance potential returns with risk. The Sharpe ratio indicates the portfolio's risk-adjusted 
    performance, with higher values suggesting better risk-adjusted returns.
    
    Remember, all investments carry risk, and past performance doesn't guarantee future results. 
    Consider your personal financial goals and risk tolerance when making investment decisions.
    """
    return summary.strip()

def parse_portfolio_input(input_text):
    portfolio = []
    lines = input_text.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            ticker = parts[0]
            try:
                percentage = float(parts[1])
                if ticker.lower() == 'cash':
                    security_type = 'Cash'
                elif any(bond in ticker.upper() for bond in ['BOND', 'TREASURY', 'TIPS']):
                    security_type = 'Fixed Income'
                else:
                    security_type = 'Equity'
                portfolio.append({
                    'ticker': ticker,
                    'percentage': percentage,
                    'type': security_type
                })
            except ValueError:
                st.error(f"Invalid percentage for ticker {ticker}")
    return portfolio

st.title('Portfolio Analysis App')

st.write("""
Enter your portfolio details below. Each line should contain a ticker symbol followed by its percentage in the portfolio.
For example:
AAPL 10
GOOGL 15
BND 30
CASH 5
""")

sample_portfolio = """SPY 30
QQQ 20
AGG 25
VEU 15
CASH 10"""

st.subheader('Sample Portfolio')
st.code(sample_portfolio)
st.write("You can copy the above sample portfolio and paste it into the text area below.")

portfolio_input = st.text_area('Enter your portfolio (ticker and percentage on each line):')

if st.button('Analyze Portfolio'):
    if portfolio_input:
        portfolio = parse_portfolio_input(portfolio_input)
        total_percentage = sum(holding['percentage'] for holding in portfolio)
        
        if abs(total_percentage - 100) > 0.01:
            st.error(f'Error: Your total portfolio percentage is {total_percentage:.2f}%. It should add up to 100%.')
        else:
            try:
                analysis = analyze_portfolio(portfolio)
                summary = generate_summary(analysis)
                
                st.subheader('Portfolio Summary')
                st.write(summary)
                
                st.subheader('Portfolio Breakdown')
                df = pd.DataFrame(portfolio)
                st.dataframe(df)
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.error('Please enter your portfolio details before analyzing.')

st.write("""
Note: This analysis uses historical data and Modern Portfolio Theory concepts. 
It should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.
""")