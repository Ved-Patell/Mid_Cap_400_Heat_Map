"""Quotes the ETF that tracks the S&P MidCap 400, using Alpha Vantage.

Our own numbers say how many companies rose and fell, which is market
breadth. That is not the same as how the index moved: a day where 300
companies rise slightly while 100 large ones fall hard gives a green chart
and a red index. So we also quote MDY, the SPDR S&P MidCap 400 ETF.

The API key is read from the ALPHAVANTAGE_API_KEY environment variable and
never written into the code. If the key is missing or the request fails,
these functions return None and the page simply leaves the benchmark out.
A missing extra should not take down the whole site.
"""

import os

import requests
from dotenv import load_dotenv

# Reads the .env file into the environment. That file holds the real key
# and is listed in .gitignore, so it never reaches GitHub.
load_dotenv()

ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
ALPHAVANTAGE_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

# The SPDR S&P MidCap 400 ETF, which tracks our index.
BENCHMARK_SYMBOL = "MDY"

REQUEST_TIMEOUT = 30


def parse_quote(payload):
    """Read the percent change out of an Alpha Vantage response.

    Returns a float, or None if the response isn't a usable quote. Alpha
    Vantage answers with HTTP 200 even when refusing the request and puts
    the refusal in the body, so checking the status code is not enough.
    """
    if not isinstance(payload, dict):
        return None

    quote = payload.get("Global Quote")
    if not quote:
        # Either a rate limit message or an unexpected shape.
        return None

    # The field arrives as text like "1.2345%", so strip the sign off.
    raw = str(quote.get("10. change percent", "")).strip().rstrip("%")

    try:
        return float(raw)
    except ValueError:
        return None


def fetch_benchmark():
    """Get MDY's percent change today, or None if it isn't available."""
    # No key configured, so skip it quietly rather than making a pointless
    # request. This is also what happens on the CI server.
    if not ALPHAVANTAGE_KEY:
        return None

    try:
        response = requests.get(
            ALPHAVANTAGE_URL,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": BENCHMARK_SYMBOL,
                "apikey": ALPHAVANTAGE_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )
        return parse_quote(response.json())
    except (requests.RequestException, ValueError):
        # A network failure or unreadable response. The benchmark is
        # optional, so give up on it rather than breaking the page.
        return None
