import streamlit as st
import pandas as pd
import numpy as np
from transformers import pipeline
import random

# Define asset class characteristics
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

@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

def generate_llm_summary(analysis):
    # Prepare a more structured input for the LLM
    input_text = f"""
    Summarize the following investment portfolio for a novice investor:

    Portfolio Composition:
    - Stocks: {analysis['equity_percentage']:.1f}%
    - Bonds: {analysis['fixed_income_percentage']:.1f}%
    - Cash: {analysis['cash_percentage']:.1f}%

    Key Metrics:
    - Expected Annual Return: {analysis['expected_return']*100:.2f}%
    - Estimated Annual Risk: {analysis['risk']*100:.2f}%
    - Sharpe Ratio: {analysis['sharpe_ratio']:.2f}

    Asset Class Breakdown:
    {' '.join([f"- {ac.replace('_', ' ').title()}: {weight*100:.1f}%" for ac, weight in analysis['asset_class_weights'].items() if weight > 0])}

    Instructions:
    1. Explain what stocks, bonds, and cash are in simple terms.
    2. Describe the portfolio's risk level ({analysis['risk_level']}) and what it means for the investor.
    3. Explain what the Expected Annual Return and Estimated Annual Risk mean in practical terms.
    4. Briefly explain the Sharpe Ratio and its significance.
    5. Provide a cautionary note about past performance and suggest consulting a financial advisor.
    6. Keep the language simple and avoid jargon.
    """

    # Generate summary using the LLM
    summary = summarizer(input_text, max_length=400, min_length=300, do_sample=False)[0]['summary_text']
    
    # Post-process the summary
    summary = post_process_summary(summary)
    
    # If the summary still doesn't look good, fall back to a template-based approach
    if not is_summary_satisfactory(summary):
        summary = generate_fallback_summary(analysis)
    
    return summary

def post_process_summary(summary):
    # Remove any repeated phrases or sentences
    lines = summary.split('\n')
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)
    
    # Join the unique lines back into a paragraph
    cleaned_summary = ' '.join(unique_lines)
    
    # Ensure the summary ends with a proper sentence
    if not cleaned_summary.endswith('.'):
        cleaned_summary += '.'
    
    return cleaned_summary

def is_summary_satisfactory(summary):
    # Check if the summary contains key phrases we expect
    required_phrases = ['stocks', 'bonds', 'cash', 'risk', 'return', 'Sharpe ratio', 'financial advisor']
    return all(phrase in summary.lower() for phrase in required_phrases)

def generate_fallback_summary(analysis):
    templates = [
        "This {risk_level} portfolio consists of {stocks}% stocks, {bonds}% bonds, and {cash}% cash. Stocks offer growth potential but can be volatile, bonds provide steady income with lower risk, and cash offers stability. The expected annual return is {return_}%, with an estimated risk of {risk}%. The Sharpe ratio of {sharpe:.2f} indicates the portfolio's risk-adjusted performance. Remember, past performance doesn't guarantee future results. Consider consulting a financial advisor for personalized advice.",
        "Your investment portfolio has a {risk_level} approach, with {stocks}% in stocks for growth, {bonds}% in bonds for stability, and {cash}% in cash for security. It aims for an annual return of {return_}%, with a risk level of {risk}%. The Sharpe ratio ({sharpe:.2f}) suggests {sharpe_description}. Always keep in mind that investments can go up or down, and it's wise to seek professional financial advice.",
        "This {risk_level} portfolio balances {stocks}% stocks, {bonds}% bonds, and {cash}% cash. Stocks can grow but fluctuate, bonds offer steadier returns, and cash provides a safety net. Aiming for a {return_}% annual return with {risk}% risk, it has a Sharpe ratio of {sharpe:.2f}, indicating its efficiency. Remember, financial markets can be unpredictable, so consider talking to a financial advisor about your specific goals."
    ]
    
    template = random.choice(templates)
    
    sharpe_description = "a good balance of return for the risk taken" if analysis['sharpe_ratio'] > 0.5 else "room for improvement in balancing return and risk"
    
    return template.format(
        risk_level=analysis['risk_level'],
        stocks=f"{analysis['equity_percentage']:.1f}",
        bonds=f"{analysis['fixed_income_percentage']:.1f}",
        cash=f"{analysis['cash_percentage']:.1f}",
        return_=f"{analysis['expected_return']*100:.2f}",
        risk=f"{analysis['risk']*100:.2f}",
        sharpe=analysis['sharpe_ratio'],
        sharpe_description=sharpe_description
    )

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
            summary += f"\n    • {ac.replace('_', ' ').title()}: {weight*100:.1f}%"

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

# Streamlit app code starts here
st.title('Portfolio Analysis App with AI-Generated Summary')

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
                
                st.subheader('AI-Generated Portfolio Summary')
                with st.spinner('Generating AI summary...'):
                    llm_summary = generate_llm_summary(analysis)
                st.markdown(llm_summary)
                
                st.subheader('Detailed Portfolio Analysis')
                original_summary = generate_summary(analysis)
                st.markdown(original_summary)
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.error('Please enter your portfolio details before analyzing.')

st.write("""
Note: This analysis uses predefined asset class characteristics and AI-generated summaries. 
It's a simplified model and should not be considered financial advice. 
Always consult with a qualified financial advisor before making investment decisions.
""")