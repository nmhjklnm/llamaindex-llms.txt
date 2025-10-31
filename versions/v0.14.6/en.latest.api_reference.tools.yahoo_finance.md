# Yahoo finance
##  YahooFinanceToolSpec #
Bases: `BaseToolSpec`
Yahoo Finance tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
class YahooFinanceToolSpec(BaseToolSpec):
    """Yahoo Finance tool spec."""

    spec_functions = [
        "balance_sheet",
        "income_statement",
        "cash_flow",
        "stock_basic_info",
        "stock_analyst_recommendations",
        "stock_news",
    ]

    def __init__(self) -> None:
        """Initialize the Yahoo Finance tool spec."""

    def balance_sheet(self, ticker: str) -> str:
        """
        Return the balance sheet of the stock.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        balance_sheet = pd.DataFrame(stock.balance_sheet)
        return "Balance Sheet: \n" + balance_sheet.to_string()

    def income_statement(self, ticker: str) -> str:
        """
        Return the income statement of the stock.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        income_statement = pd.DataFrame(stock.income_stmt)
        return "Income Statement: \n" + income_statement.to_string()

    def cash_flow(self, ticker: str) -> str:
        """
        Return the cash flow of the stock.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        cash_flow = pd.DataFrame(stock.cashflow)
        return "Cash Flow: \n" + cash_flow.to_string()

    def stock_basic_info(self, ticker: str) -> str:
        """
        Return the basic info of the stock. Ex: price, description, name.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        return "Info: \n" + str(stock.info)

    def stock_analyst_recommendations(self, ticker: str) -> str:
        """
        Get the analyst recommendations for a stock.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        return "Recommendations: \n" + str(stock.recommendations)

    def stock_news(self, ticker: str) -> str:
        """
        Get the most recent news titles of a stock.

        Args:
          ticker (str): the stock ticker to be given to yfinance

        """
        stock = yf.Ticker(ticker)
        news = stock.news
        out = "News: \n"
        for i in news:
            out += i["title"] + "\n"
        return out

```
  
---|---  
###  balance_sheet #
```
balance_sheet(ticker: str) -> str

```

Return the balance sheet of the stock.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def balance_sheet(self, ticker: str) -> str:
    """
    Return the balance sheet of the stock.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    balance_sheet = pd.DataFrame(stock.balance_sheet)
    return "Balance Sheet: \n" + balance_sheet.to_string()

```
  
---|---  
###  income_statement #
```
income_statement(ticker: str) -> str

```

Return the income statement of the stock.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def income_statement(self, ticker: str) -> str:
    """
    Return the income statement of the stock.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    income_statement = pd.DataFrame(stock.income_stmt)
    return "Income Statement: \n" + income_statement.to_string()

```
  
---|---  
###  cash_flow #
```
cash_flow(ticker: str) -> str

```

Return the cash flow of the stock.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def cash_flow(self, ticker: str) -> str:
    """
    Return the cash flow of the stock.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    cash_flow = pd.DataFrame(stock.cashflow)
    return "Cash Flow: \n" + cash_flow.to_string()

```
  
---|---  
###  stock_basic_info #
```
stock_basic_info(ticker: str) -> str

```

Return the basic info of the stock. Ex: price, description, name.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def stock_basic_info(self, ticker: str) -> str:
    """
    Return the basic info of the stock. Ex: price, description, name.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    return "Info: \n" + str(stock.info)

```
  
---|---  
###  stock_analyst_recommendations #
```
stock_analyst_recommendations(ticker: str) -> str

```

Get the analyst recommendations for a stock.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def stock_analyst_recommendations(self, ticker: str) -> str:
    """
    Get the analyst recommendations for a stock.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    return "Recommendations: \n" + str(stock.recommendations)

```
  
---|---  
###  stock_news #
```
stock_news(ticker: str) -> str

```

Get the most recent news titles of a stock.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ticker` |  `str` |  the stock ticker to be given to yfinance |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-yahoo-finance/llama_index/tools/yahoo_finance/base.py`

| ```
def stock_news(self, ticker: str) -> str:
    """
    Get the most recent news titles of a stock.

    Args:
      ticker (str): the stock ticker to be given to yfinance

    """
    stock = yf.Ticker(ticker)
    news = stock.news
    out = "News: \n"
    for i in news:
        out += i["title"] + "\n"
    return out

```
  
---|---
