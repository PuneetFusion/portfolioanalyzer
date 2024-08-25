import streamlit as st
import pandas as pd
import numpy as np
from transformers import pipeline

# [Previous code for ASSET_CLASSES, map_ticker_to_asset_class, analyze_portfolio, parse_portfolio_input remains the same]

@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

def generate_llm_summary(analysis):
    # Prepare the input text for the LLM
    input_text = f"""
    Investment portfolio summary:
    - Risk approach: {analysis['risk_level']}
    - Stocks: {analysis['equity_percentage']:.1f}%
    - Bonds: {analysis['fixed_income_percentage']:.1f}%
    - Cash: {analysis['cash_percentage']:.1f}%
    - Expected Annual Return: {analysis['expected_return']*100:.2f}%
    - Estimated Annual Risk: {analysis['risk']*100:.2f}%
    - Sharpe Ratio: {analysis['sharpe_ratio']:.2f}

    Asset class breakdown:
    {' '.join([f"- {ac.replace('_', ' ').title()}: {weight*100:.1f}%" for ac, weight in analysis['asset_class_weights'].items() if weight > 0])}

    Provide a summary of this investment portfolio for a novice investor. Explain the portfolio's composition, its risk level, and what the numbers mean in simple terms. Include a brief explanation of stocks, bonds, and cash. Mention that past performance doesn't guarantee future results and suggest consulting with a financial advisor.
    """

    # Generate summary using the LLM
    summary = summarizer(input_text, max_length=300, min_length=200, do_sample=False)[0]['summary_text']
    
    return summary

def generate_summary(analysis):
    # [Keep the original generate_summary function as a fallback]
    # ... [Original generate_summary code] ...

st.title('Portfolio Analysis App with AI-Generated Summary')

# [Rest of the Streamlit app code remains largely the same]

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