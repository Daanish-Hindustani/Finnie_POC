import requests
import yfinance as yf
from yahooquery import Ticker
from crewai.tools import tool 
import ollama

def get_competitors_from_llm(ticker: str, sector: str, industry: str):
    """
    Query the LLM to get competitors for the given stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        sector (str): The sector the company operates in.
        industry (str): The industry the company operates in.
    
    Returns:
        list: A list of competitors' ticker symbols.
    """
    query = f"Identify the top 3 competitors for the company with ticker symbol {ticker}, which is in the {sector} sector and {industry} industry. Return three indicators nothing else"
    
    # Sending the query to the LLM
    response = ollama.chat(model='deepseek-r1:1.5b', messages=[
      { 'role': 'user', 'content': query},
    ])
    print(response)
    if response.status_code == 200:
        # Assuming the LLM returns a list of competitors as a string
        competitors = response.json().get('output', '').split('\n')
        return competitors
    else:
        print(f"Error: {response.status_code}")
        return []

def competitor_analysis(ticker: str, num_competitors: int = 3):
    """
    Retrieves key financial metrics for a stock and its top competitors in the same industry using an LLM.

    Args:
        ticker (str): The stock ticker symbol.
        num_competitors (int): Number of competitors to return (default: 3).

    Returns:
        dict: A dictionary containing industry details and competitor financials.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get('sector')
    industry = info.get('industry')

    # Get competitors using the LLM
    competitors = get_competitors_from_llm(ticker, sector, industry)

    # Fetch competitor financial data
    competitor_data = []
    for comp in competitors[:num_competitors]:
        try:
            comp_stock = yf.Ticker(comp)
            comp_info = comp_stock.info

            competitor_data.append({
                "ticker": comp,
                "name": comp_info.get('longName', "N/A"),
                "market_cap": comp_info.get('marketCap', "N/A"),
                "pe_ratio": comp_info.get('trailingPE', "N/A"),
                "revenue_growth": comp_info.get('revenueGrowth', "N/A"),
                "profit_margins": comp_info.get('profitMargins', "N/A"),
            })
        except Exception as e:
            competitor_data.append({
                "ticker": comp,
                "error": str(e)
            })

    return {
        "main_stock": ticker,
        "sector": sector,
        "industry": industry,
        "competitors": competitor_data
    }


def main():
    result = competitor_analysis("AAPL")
    print(result)


if __name__ == "__main__":
    main()
