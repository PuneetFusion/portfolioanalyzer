import random

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

# Update the Streamlit app section to use this new function
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