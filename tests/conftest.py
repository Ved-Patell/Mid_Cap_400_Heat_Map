import pandas as pd
import pytest


# A trimmed copy of the Wikipedia table, including MOG.A because that dotted ticker is the case most likely to break.
WIKI_HTML = """
<html><body>
<table class="wikitable">
  <tr>
    <th>Symbol</th><th>Security</th><th>GICS Sector</th>
    <th>GICS Sub-Industry</th><th>Headquarters Location</th>
  </tr>
  <tr><td>AAON</td><td>AAON</td><td>Industrials</td>
      <td>Building Products</td><td>Tulsa, Oklahoma</td></tr>
  <tr><td>MOG.A</td><td>Moog Inc.</td><td>Industrials</td>
      <td>Aerospace &amp; Defense</td><td>Elma, New York</td></tr>
  <tr><td>ZION</td><td>Zions Bancorporation</td><td>Financials</td>
      <td>Regional Banks</td><td>Salt Lake City, Utah</td></tr>
  <tr><td>CELH</td><td>Celsius Holdings</td><td>Consumer Staples</td>
      <td>Soft Drinks</td><td>Boca Raton, Florida</td></tr>
</table>
</body></html>
"""


# A trimmed copy of the IJH holdings file, keeping the real shape.
HOLDINGS_CSV = '''iShares Core S&P Mid-Cap ETF
Fund Holdings as of,"Aug 13, 2026"
Inception Date,"May 22, 2000"
Shares Outstanding,"1,636,450,000.00"
Stock,"-"
Bond,"-"
Cash,"-"
Other,"-"

Ticker,Name,Type,Sector,Asset Class,Market Value,Weight (%)
"AAON","AAON INC","EQUITY","Industrials","Equity","500,000,000.00","0.40"
"MOG.A","MOOG INC CLASS A","EQUITY","Industrials","Equity","400,000,000.00","0.32"
"ZION","ZIONS BANCORP","EQUITY","Financials","Equity","600,000,000.00","0.48"
"CELH","CELSIUS HOLDINGS","EQUITY","Consumer Staples","Equity","300,000,000.00","0.24"
"USD","USD CASH","CASH","Cash and/or Derivatives","Cash","1,000,000.00","-"
'''

@pytest.fixture
def holdings_csv():
    """Sample IJH holdings file contents."""
    return HOLDINGS_CSV


@pytest.fixture
def weights():
    """Index weights as parse_index_weights would return them."""
    return pd.DataFrame({
        "Symbol": ["AAON", "MOG-A", "ZION", "CELH"],
        "Weight": [0.40, 0.32, 0.48, 0.24],
    })

@pytest.fixture
def wiki_html():
    #Sample Wikipedia page HTML.
    return WIKI_HTML


@pytest.fixture
def companies():
    return pd.DataFrame({
        "Symbol": ["AAON", "MOG-A", "ZION", "CELH"],
        "Security": ["AAON", "Moog Inc.", "Zions Bancorporation",
                     "Celsius Holdings"],
        "GICS Sector": ["Industrials", "Industrials", "Financials",
                        "Consumer Staples"],
    })
    #The company table as parse_constituents would return it.

@pytest.fixture
def closes():
    #Two days of closing prices for four tickers.

    #AAON rises 10%, MOG-A falls 5%, ZION is unchanged, and DEAD has nodata at all, which is what a delisted or mistyped ticker looks like.
    
    return pd.DataFrame(
        {
            "AAON":  [100.0, 110.0],
            "MOG-A": [200.0, 190.0],
            "ZION":  [50.0, 50.0],
            "DEAD":  [float("nan"), float("nan")],
        },
        index=pd.to_datetime(["2026-08-11", "2026-08-12"]),
    )


@pytest.fixture
def returns():
    """Daily returns as daily_returns would return them."""
    return pd.DataFrame({
        "Symbol": ["AAON", "MOG-A", "ZION", "CELH"],
        "Return": [10.0, -5.0, 0.0, 2.5],
    })