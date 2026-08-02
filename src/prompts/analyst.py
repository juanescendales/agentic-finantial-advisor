SYSTEM_PROMPT_V1 = """
    You are a financial analyst, expert in determinig stock trends and providing investment advice. You will be given a company's stock ticker, news articles, fundamentals data, and market data. 
    Your task is to synthesize this information into a concise analyst report that includes:
    1. summary: A brief overview of the company's current situation based on the provided data.
    2. bull_case: A list of reasons why the stock might perform well in the future. (e.g., strong fundamentals, positive news, favorable market trends).
    3. bear_case: A list of reasons why the stock might perform poorly in the future. (e.g., weak fundamentals, negative news, unfavorable market trends)
    4. notable_signals: A list of any significant signals or indicators that stand out from the data.
    5. data_quality_flags: A list of any concerns or limitations regarding the quality or completeness of the data provided.

    Please ensure that your report is clear, concise, and based solely on the information provided. Avoid speculation or external information. 
    If any data is missing or unclear, note it in the data_quality_flags section.

    Output the report in JSON format with the following structure:
    {
        "summary": "string",
        "bull_case": ["string"],
        "bear_case": ["string"],
        "notable_signals": ["string"], 
        "data_quality_flags": ["string"]
    }
"""

ANALYST_PROMPT_V1 = """
    This is the data you have been provided:
    Company Ticker: {ticker}
    Company Name: {company_name}
    News Data: {news_data}
    Fundamentals Data: {fundamentals_data}
    Market Data: {market_data}
""" 

from dataclasses import dataclass

@dataclass
class AnalystPrompt:
    system_prompt: str = SYSTEM_PROMPT_V1
    analyst_prompt: str = None

def generate_analyst_prompt(ticker: str, company_name: str, news_data: str, fundamentals_data: str, market_data: str) -> AnalystPrompt:
    """Generate the analyst prompt with the provided state data.

    Args:
        ticker: The company's stock ticker.
        company_name: The company's name.
        news_data: The news data for the company.
        fundamentals_data: The fundamentals data for the company.
        market_data: The market data for the company.

    Returns:
        The formatted prompt string.
    """
    format_analyst_prompt = ANALYST_PROMPT_V1.format(
        ticker=ticker,
        company_name=company_name,
        news_data=news_data,
        fundamentals_data=fundamentals_data,
        market_data=market_data
    )

    return AnalystPrompt(
        system_prompt=SYSTEM_PROMPT_V1,
        analyst_prompt=format_analyst_prompt
    )





