from dataclasses import dataclass

SYSTEM_PROMPT_V1 = """
    You are an investment advisor. You will be given a company's stock ticker and an analyst report covering that company.
    Your task is to turn that report into a single actionable recommendation that includes:
    1. action: One of "BUY", "HOLD", or "SELL".
    2. confidence: A number between 0.0 and 1.0 reflecting how strongly the report supports your action.
    3. time_horizon: One of "short", "medium", or "long", the period over which you expect the action to pay off.
    4. key_drivers: A list of 3 to 5 short reasons that drove your action, each traceable to the report.
    5. reasoning: A free-form explanation of at most 500 words, weighing the bull case against the bear case.

    Base your decision solely on the analyst report. Do not introduce external information or price targets that are not supported by it.
    Weigh the report's data_quality_flags: weak or incomplete data should lower your confidence, and when the evidence is thin "HOLD" is a legitimate answer.

    Output the recommendation in JSON format with the following structure:
    {
        "action": "BUY" | "HOLD" | "SELL",
        "confidence": 0.0,
        "time_horizon": "short" | "medium" | "long",
        "key_drivers": ["string"],
        "reasoning": "string"
    }
"""

ADVISOR_PROMPT_V1 = """
    This is the data you have been provided:
    Company Ticker: {ticker}
    Company Name: {company_name}
    Analyst Report: {analyst_report}
"""


@dataclass
class AdvisorPrompt:
    advisor_prompt: str
    system_prompt: str = SYSTEM_PROMPT_V1


def generate_advisor_prompt(
    ticker: str, company_name: str, analyst_report: str
) -> AdvisorPrompt:
    """Generate the advisor prompt with the provided state data.

    Args:
        ticker: The company's stock ticker.
        company_name: The company's name.
        analyst_report: The analyst report for the company.

    Returns:
        The formatted prompt string.
    """
    format_advisor_prompt = ADVISOR_PROMPT_V1.format(
        ticker=ticker,
        company_name=company_name,
        analyst_report=analyst_report,
    )

    return AdvisorPrompt(
        system_prompt=SYSTEM_PROMPT_V1,
        advisor_prompt=format_advisor_prompt,
    )
