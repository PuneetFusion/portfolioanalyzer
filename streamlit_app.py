import streamlit as st
import pandas as pd
import numpy as np

# Define asset class characteristics
# These are example values and should be updated with more accurate data
ASSET_CLASSES = {
    'US_LARGE_CAP': {'return': 0.10, 'risk': 0.15, 'type': 'Equity'},
    'US_MID_CAP': {'return': 0.12, 'risk': 0.18, 'type': 'Equity'},
    'US_SMALL_CAP': {'return': 0.13, 'risk': 0.20, 'type': 'Equity'},
    'INTERNATIONAL_DEVELOPED': {'return': 0.09, 'risk': 0.16, 'type': 'Equity'},
    'EMERGING_MARKETS': {'return': 0.11, 'risk': 0.22, 'type': 'Equity'},
    'US_AGGREGATE_BOND': {'return': 0.04, 'risk': 0.05, 'type': 'Fixed Income'},
    'HIGH_YIELD_BOND': {'return': 0.06, 'risk': 0.10, 'type': 'Fixed Income'},
    'INTERNATIONAL_BOND': {'return': 0.03, 'risk': 0.07, 'type': 'Fixed Income'},
    'CASH': {'return': 0.01, 'risk': 0.01, 'type': 'Cash'}
}

def map_ticker_to_asset_class(ticker):
    ticker = ticker.upper()
    if ticker in ['SPY', 'IVV', 'VOO']:
        return 'US_LARGE_CAP'
    elif ticker in ['IJH', 'VO']:
        return 'US_MID_CAP'
    elif ticker in ['IJR', 'VB']:
        return 'US_SMALL_CAP'
    elif ticker in ['EFA', 'VEA']:
        return 'INTERNATIONAL_DEVELOPED'
    elif ticker in ['EEM', 'VWO']:
        return 'EMERGING_MARKETS'
    elif ticker in ['AGG', 'BND']:
        return 'US_AGGREGATE_BOND'
    elif ticker in ['HYG', 'JNK']:
        return 'HIGH_YIELD_BOND'
    elif ticker in ['BNDX', 'IAGG']:
        return 'INTERNATIONAL_BOND'
    elif ticker == 'CASH':
        return 'CASH'
    else:
        return 'US_LARGE_CAP'  # Default to US Large Cap if unknown

def analyze_portfolio(portfolio):
    total_weight = 0
    weighted_return = 0
    weighted_risk = 0
    asset_class_weights = {ac: 0 for ac in ASSET_CLASSES}

    for holding in portfolio:
        asset_class = map_ticker_to_asset_class(holding['ticker'])
        weight = holding['percentage'] / 100
        total_weight += weight
        asset_class_weights[asset_class] += weight
        weighted_return += ASSET_CLASSES[asset_class]['return'] * weight
        weighted_risk += ASSET_CLASSES[asset_class]['risk'] * weight

    if abs(total_weight - 1) > 0.0001:
        raise ValueError("Portfolio weights do not sum to 100%")

    portfolio_return = weighted_return
    portfolio_risk = weighted_risk  # This is a simplification; actual portfolio risk would consider correlations

    # Calculate asset type percentages
    equity_percentage = sum(asset_class_weights[ac] for ac, info in ASSET_CLASSES.items() if info['type'] == 'Equity') * 100
    fixed_income_percentage = sum(asset_class_weights[ac] for ac, info in ASSET_CLASSES.items() if info['type'] == 'Fixed Income') * 100
    cash_percentage = asset_class_weights['CASH'] * 100

    # Determine risk level
    if equity_percentage > 70:
        risk_level = "aggressive"
    elif equity_percentage < 30:
        risk_level = "conservative"
    else:
        risk_level = "moderate"

    sharpe_ratio = (portfolio_return - ASSET_CLASSES['CASH']['return']) / portfolio_risk

    return {
        'expected_return': portfolio_return,
        'risk': portfolio_risk,
        'sharpe_ratio': sharpe_ratio,
        'equity_percentage': equity_percentage,
        'fixed_income_percentage': fixed_income_percentage,
        'cash_percentage': cash_percentage,
        'risk_level': risk_level,
        'asset_class_weights': asset_class_weights
    }

# [Previous code remains the same]

def generate_summary(analysis):
    summary = f"""
    Your investment portfolio is structured with a {analysis['risk_level']} approach. Here's what that means:

    Asset Allocation (how your money is divided up):
    - Stocks: {analysis['equity_percentage']:.1f}%
      Stocks represent ownership in companies and can offer growth potential but can be more volatile.
    - Bonds: {analysis['fixed_income_percentage']:.1f}%
      Bonds are loans to governments or companies, typically offering steady income but lower growth potential.
    - Cash: {analysis['cash_percentage']:.1f}%
      Cash includes money market funds and savings, offering high safety but low returns.

    Based on historical performance of these types of investments:
    
    1. Expected Annual Return: {analysis['expected_return']*100:.2f}%
       This is how much your portfolio might grow in a year, on average. Remember, actual returns can vary greatly from year to year.

    2. Estimated Annual Risk: {analysis['risk']*100:.2f}%
       Risk, also called volatility, measures how much your portfolio's value might go up or down. Higher risk often comes with potential for higher returns, but also larger losses.

    3. Sharpe Ratio: {analysis['sharpe_ratio']:.2f}
       The Sharpe ratio helps compare investments by considering both return and risk. A higher number suggests better returns for the risk taken. Generally, a Sharpe ratio above 1 is considered good.

    Your portfolio is divided into these investment categories:
    """
    for ac, weight in analysis['asset_class_weights'].items():
        if weight > 0:
            summary += f"\n    - {ac.replace('_', ' ').title()}: {weight*100:.1f}%"
    
    summary += """

    What does this all mean?
    - If your portfolio is "aggressive", it aims for higher growth but might have bigger ups and downs.
    - If it's "moderate", it tries to balance growth and stability.
    - If it's "conservative", it prioritizes protecting your money over growing it quickly.

    Remember:
    1. Past performance doesn't guarantee future results. The market can be unpredictable.
    2. This analysis is based on general historical data and is just for educational purposes.
    3. As your life circumstances change, your ideal investment mix might change too.
    4. It's always a good idea to talk to a qualified financial advisor for personalized advice.
    """
    return summary.strip()

# [Rest of the code remains the same]

def parse_portfolio_input(input_text):
    portfolio = []
    lines = input_text.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            ticker = parts[0]
            try:
                percentage = float(parts[1])
                portfolio.append({
                    'ticker': ticker,
                    'percentage': percentage
                })
            except ValueError:
                st.error(f"Invalid percentage for ticker {ticker}")
    return portfolio

st.title('Portfolio Analysis App')

st.write("""
Enter your portfolio details below. Each line should contain a ticker symbol followed by its percentage in the portfolio.
For example:
SPY 30
AGG 40
EFA 20
CASH 10
""")

sample_portfolio = """SPY 30
AGG 40
EFA 20
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
Note: This analysis uses predefined asset class characteristics based on historical performance. 
It's a simplified model and should not be considered financial advice. 
Always consult with a qualified financial advisor before making investment decisions.
""")