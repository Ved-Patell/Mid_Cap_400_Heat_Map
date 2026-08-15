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