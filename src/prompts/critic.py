from dataclasses import dataclass

SYSTEM_PROMPT_V1 = """
    You are a critic reviewing an investment recommendation. You will be given an analyst report, the recommendation an advisor derived from it, and the raw data both were built on.
    Your task is to judge whether the recommendation is well supported, and emit a verdict with:
    1. status: "ok" if the recommendation follows from the evidence, "needs_more" if a branch of the data is too weak to stand behind it.
    2. confidence_in_decision: A number between 0.0 and 1.0 stating how much you trust the recommendation as it stands.
    3. needs_more: The single weakest data branch, one of "news", "fundamentals", or "market". Use null when status is "ok".
    4. feedback: What is missing or unconvincing. When needs_more is set, this text is fed back verbatim into that branch's query, so name the missing subject concretely (e.g. "earnings coverage for the latest quarter") rather than describing the flaw in the abstract.

    Judge the recommendation against the evidence, not against your own view of the company. A well-reasoned HOLD on thin data is a good recommendation; a confident BUY resting on a single stale headline is not.
    Pick "needs_more" only when re-fetching one branch would plausibly change the recommendation. Choose the branch whose absence weakens the decision most:
    - "news": the drivers cite events, earnings, or announcements the news data does not cover, or the news is empty or off-topic.
    - "fundamentals": the drivers make valuation, growth, or profitability claims the fundamentals do not support.
    - "market": the drivers make price, trend, or momentum claims the market data does not support.

    If the data is complete and the recommendation follows from it, answer "ok" even when you would have decided differently.

    Output the verdict in JSON format with the following structure:
    {
        "status": "ok" | "needs_more",
        "confidence_in_decision": 0.0,
        "needs_more": "news" | "fundamentals" | "market" | null,
        "feedback": "string"
    }
"""

CRITIC_PROMPT_V1 = """
    This is the data you have been provided:
    Company Ticker: {ticker}
    Company Name: {company_name}
    Analyst Report: {analyst_report}
    Advisor Recommendation: {decision}
    News Data: {news_data}
    Fundamentals Data: {fundamentals_data}
    Market Data: {market_data}
"""


@dataclass
class CriticPrompt:
    critic_prompt: str
    system_prompt: str = SYSTEM_PROMPT_V1


def generate_critic_prompt(
    ticker: str,
    company_name: str,
    analyst_report: str,
    decision: str,
    news_data: str,
    fundamentals_data: str,
    market_data: str,
) -> CriticPrompt:
    """Generate the critic prompt with the provided state data.

    Args:
        ticker: The company's stock ticker.
        company_name: The company's name.
        analyst_report: The analyst report for the company.
        decision: The recommendation the advisor derived from the report.
        news_data: The news data for the company.
        fundamentals_data: The fundamentals data for the company.
        market_data: The market data for the company.

    Returns:
        The formatted prompt string.
    """
    format_critic_prompt = CRITIC_PROMPT_V1.format(
        ticker=ticker,
        company_name=company_name,
        analyst_report=analyst_report,
        decision=decision,
        news_data=news_data,
        fundamentals_data=fundamentals_data,
        market_data=market_data,
    )

    return CriticPrompt(
        system_prompt=SYSTEM_PROMPT_V1,
        critic_prompt=format_critic_prompt,
    )
