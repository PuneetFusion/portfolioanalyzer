import streamlit as st
import pandas as pd
import pyperclip

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

def parse_portfolio_input(input_text):
    portfolio = []
    lines = input_text.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            ticker = parts[0]
            try:
                percentage = float(parts[1])
                # Simple logic to determine security type based on ticker
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

sample_portfolio = """IVV 12.5
SPDW 10.0
VONG 7.5
VTV 7.5
SCHA 5.0
SCHE 3.75
IWR 3.75
HYG 2.4
BND 43.2
BNDX 2.4
CASH 2.0"""

if st.button('Copy Sample Portfolio to Clipboard'):
    pyperclip.copy(sample_portfolio)
    st.success('Sample portfolio copied to clipboard!')

portfolio_input = st.text_area('Enter your portfolio (ticker and percentage on each line):')

if st.button('Analyze Portfolio'):
    if portfolio_input:
        portfolio = parse_portfolio_input(portfolio_input)
        total_percentage = sum(holding['percentage'] for holding in portfolio)
        
        if abs(total_percentage - 100) > 0.01:
            st.error(f'Error: Your total portfolio percentage is {total_percentage:.2f}%. It should add up to 100%.')
        else:
            analysis = analyze_portfolio(portfolio)
            summary = generate_summary(analysis)
            
            st.subheader('Portfolio Summary')
            st.write(summary)
            
            st.subheader('Portfolio Breakdown')
            df = pd.DataFrame(portfolio)
            st.dataframe(df)
    else:
        st.error('Please enter your portfolio details before analyzing.')

st.write("""
Note: This is a simplified analysis and should not be considered financial advice. 
Always consult with a qualified financial advisor before making investment decisions.
""")