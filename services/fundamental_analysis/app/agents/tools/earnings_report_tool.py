from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import yfinance as yf
from typing import Dict



class IncomeStatement(BaseModel):
    """Income Statement for a company."""
    total_revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    cost_of_revenue: float

class BalanceSheet(BaseModel):
    """Balance Sheet for a company."""
    total_assets: float
    total_liabilities: float
    total_equity: float
    current_assets: float
    current_liabilities: float

class CashFlowStatement(BaseModel):
    """Cash Flow Statement for a company."""
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float
    free_cash_flow: float
    capital_expenditures: float
    repurchase_of_stock: float
    long_term_debt_issuance: float
    long_term_debt_repayment: float
    end_cash_position: float

class HistroicCashFlow(BaseModel):
    historic_balance_sheets: Dict[str, CashFlowStatement]

class EarningsCallToolInput(BaseModel):
    """Input schema for EarningsCallTool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")

class EarningsCallTool(BaseTool):
    name: str = "Earnings Call Analysis Tool"
    description: str = "Fetches detailed earnings report data, including income statement, balance sheet, and cash flow statement."
    args_schema: Type[BaseModel] = EarningsCallToolInput

    def _run(self, stock_symbol: str) -> dict:
        """Main function to get earnings report data."""
        try:
            earnings_report = self.get_earning_report(stock_symbol)
            return earnings_report
        except Exception as e:
            return {"error": f"Error fetching earnings data: {str(e)}"}

    def get_earning_report(self, stock_symbol: str) -> dict:
        """Get the full earnings report (income statement, balance sheet, cash flow)."""
        #income_statement = self.get_income_statement(stock_symbol)
        #balance_sheet = self.get_balance_sheet(stock_symbol)
        cash_flow_statement = self.get_cash_flow_statement(stock_symbol)

        return {
            "stock_symbol": stock_symbol,
            #"income_statement": income_statement.dict(),
            #"balance_sheet": balance_sheet.model_dump(),
            "cash_flow_statement": cash_flow_statement
        }

    def get_income_statement(self, stock_symbol: str) -> IncomeStatement:
        """Fetch the income statement for the given stock."""
        ticker = yf.Ticker(stock_symbol)
        income_statement_data = ticker.financials.to_dict()
        print(income_statement_data)
        # Safely fetch the values using .iloc() for positional access
        try:
            total_revenue = income_statement_data.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_statement_data.index else None
            gross_profit = income_statement_data.loc['Gross Profit'].iloc[0] if 'Gross Profit' in income_statement_data.index else None
            operating_income = income_statement_data.loc['Operating Income'].iloc[0] if 'Operating Income' in income_statement_data.index else None
            net_income = income_statement_data.loc['Net Income'].iloc[0] if 'Net Income' in income_statement_data.index else None
            cost_of_revenue = income_statement_data.loc['Cost of Revenue'].iloc[0] if 'Cost of Revenue' in income_statement_data.index else None
            
            return IncomeStatement(
                total_revenue=total_revenue,
                gross_profit=gross_profit,
                operating_income=operating_income,
                net_income=net_income,
                cost_of_revenue=cost_of_revenue
            )
        except KeyError as e:
            return {"error": f"Missing data in income statement: {str(e)}"}
        except Exception as e:
            return {"error": f"Error fetching income statement: {str(e)}"}

    def get_balance_sheet(self, stock_symbol: str) -> BalanceSheet:
        """Fetch the balance sheet for the given stock."""
        ticker = yf.Ticker(stock_symbol)
        balance_sheet_data = ticker.balance_sheet
        
        return BalanceSheet(
            total_assets=balance_sheet_data.loc['Total Assets'][0],
            total_liabilities=balance_sheet_data.loc['Total Liabilities Net Minority Interest'][0],
            total_equity=balance_sheet_data.loc['Total Equity Gross Minority Interest'][0],
            current_assets=balance_sheet_data.loc['Total Current Assets'][0],
            current_liabilities=balance_sheet_data.loc['Total Current Liabilities'][0]
        )

    def get_cash_flow_statement(self, stock_symbol: str) -> Dict[str, CashFlowStatement]:
        """Fetch the cash flow statement for the given stock."""
        ticker = yf.Ticker(stock_symbol)
        cash_flow_data = ticker.cash_flow.to_dict()
        
        cash_flow_statements = {}
        for date, data in cash_flow_data.items():
            formatted_date = str(date).split(" ")[0]
            cash_flow_statements[formatted_date] = self._parse_cash_flow_item(data)
        
        return cash_flow_statements

    def _parse_cash_flow_item(self, cash_flow_data: Dict) -> CashFlowStatement:
        """Parse raw cash flow data into a structured CashFlowStatement."""
        return CashFlowStatement(
            operating_cash_flow=cash_flow_data['Operating Cash Flow'],
            investing_cash_flow=cash_flow_data['Investing Cash Flow'],
            financing_cash_flow=cash_flow_data['Financing Cash Flow'],
            free_cash_flow=cash_flow_data['Operating Cash Flow'] + cash_flow_data['Capital Expenditure'],
            capital_expenditures=cash_flow_data['Capital Expenditure'],
            repurchase_of_stock=cash_flow_data['Repurchase Of Capital Stock'],
            long_term_debt_issuance=cash_flow_data['Issuance Of Debt'],
            long_term_debt_repayment=cash_flow_data['Repayment Of Debt'],
            end_cash_position=cash_flow_data['End Cash Position']
        )

print(EarningsCallTool()._run('GOOGL'))