import streamlit as st
import pandas as pd
import numpy as np

# [Previous code for ASSET_CLASSES, map_ticker_to_asset_class, analyze_portfolio, and parse_portfolio_input remains the same]

def generate_summary(analysis):
    summary = f"""Your investment portfolio is structured with a {analysis['risk_level']} approach. Here's what that means:

Asset Allocation (how your money is divided up):
• Stocks: {analysis['equity_percentage']:.1f}%
  Stocks represent ownership in companies and can offer growth potential but can be more volatile.
• Bonds: {analysis['fixed_income_percentage']:.1f}%
  Bonds are loans to governments or companies, typically offering steady income but lower growth potential.
• Cash: {analysis['cash_percentage']:.1f}%
  Cash includes money market funds and savings, offering high safety but low returns.

Based on historical performance of these types of investments:

1. Expected Annual Return: {analysis['expected_return']*100:.2f}%
   This is how much your portfolio might grow in a year, on average. Remember, actual returns can vary greatly from year to year.

2. Estimated Annual Risk: {analysis['risk']*100:.2f}%
   Risk, also called volatility, measures how much your portfolio's value might go up or down. Higher risk often comes with potential for higher returns, but also larger losses.

3. Sharpe Ratio: {analysis['sharpe_ratio']:.2f}
   The Sharpe ratio helps compare investments by considering both return and risk. A higher number suggests better returns for the risk taken. Generally, a Sharpe ratio above 1 is considered good.

Your portfolio is divided into these investment categories:"""

    for ac, weight in analysis['asset_class_weights'].items():
        if weight > 0:
            summary += f"\n• {ac.replace('_', ' ').title()}: {weight*100:.1f}%"

    summary += """

What does this all mean?
• If your portfolio is "aggressive", it aims for higher growth but might have bigger ups and downs.
• If it's "moderate", it tries to balance growth and stability.
• If it's "conservative", it prioritizes protecting your money over growing it quickly.

Remember:
1. Past performance doesn't guarantee future results. The market can be unpredictable.
2. This analysis is based on general historical data and is just for educational purposes.
3. As your life circumstances change, your ideal investment mix might change too.
4. It's always a good idea to talk to a qualified financial advisor for personalized advice."""

    return summary

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
                st.markdown(summary)  # Using markdown for better formatting
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.error('Please enter your portfolio details before analyzing.')

st.write("""
Note: This analysis uses predefined asset class characteristics based on historical performance. 
It's a simplified model and should not be considered financial advice. 
Always consult with a qualified financial advisor before making investment decisions.
""")