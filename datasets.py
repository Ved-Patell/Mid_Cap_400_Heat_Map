#Gets the data we need
#1. Wikipedia - list of companies in the S&P 400 Mid Cap Index 
#2. Yahoo Finance - recent stock prices, we convert to returns

import io

import pandas as pd
import requests
import yfinance as yf

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
#WIKI API returns data as HTML and offers no advantage, so we scraped the data. Wikipedia requires us to identify using user agent.
USER_AGENT = "student-project"
COLUMNS = ["Symbol", "Security", "GICS Sector"]
IJH_URL = "https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appType=PRODUCT_PAGE&appSubType=ISHARES&targetSite=us-ishares&locale=en_US&portfolioId=239763&userType=individual&asOfDate=20260813&component=holdings"
#Ask Yahoo Finance for 10 calendar days of price history to account for holidays
HISTORY_PERIOD = "10D"

#How long to wait
REQUEST_TIMEOUT = 30

def normalize_symbol(symbol):

    return str(symbol).strip().replace(".","-")
    #need this to make tickers consistent across Wiki and Yahoo Finance, learned
    #str() first to avoid blank cells, .strip() removes stray spaces, .replace() does the fix.

def parse_constituents(html):
    #Find company table in Wiki

    tables = pd.read_html(io.StringIO(html))
    #learned - read_html finds every table and returns as DataFrame. StringIO wraps our string on pandas and treats it as a file rather than filename to look up.

    #Wiki page has lots of tables, but we ask it below to check for only the ones with the COLUMNS we stated above.
    for table in tables:
        if set(COLUMNS).issubset(table.columns):
            companies = table[COLUMNS].copy()
            companies["Symbol"] = companies ["Symbol"].apply(normalize_symbol)
            return companies.reset_index(drop=True)
    raise ValueError("No table with the expected columns was found.") #Quality Control in case the table is changed later.

#Downloading Wikipedia and getting the company table
def fetch_constituents():
    response =requests.get(
        WIKI_URL,
        headers={"User-Agent": USER_AGENT}, #DEFINED EARLIER SO EACH PROJECT CAN BE IDENTIFIED SEPARATELY
        timeout=REQUEST_TIMEOUT,  #DEFINED EARLIER IN CASE OF NEED TO CHANGE
    )
    response.raise_for_status() #In case of error

    return parse_constituents(response.text)  
#.text is the page's HTML as a string, which is handed to the parser.

def daily_returns(closes):
    closes = closes.dropna(axis=1, how="all")

    if len(closes) < 2:
        raise ValueError("Need at least two trading days to compute a return.")

#using iloc to return last 2 days return and converting to percentage
    change = (closes.iloc[-1] / closes.iloc[-2] -1) * 100

    change = change.dropna()  #drops anything still missing

    returns = pd.DataFrame({"Symbol": change.index, "Return": change.values})
#change is a series with tickers as labels, we turn into two-column table.

    return returns.reset_index(drop=True), closes.index[-1]

def fetch_prices(symbols):
    data = yf.download(   #yf.download allows us to take the whole list rather than one ticker at a time
        symbols,
        period=HISTORY_PERIOD,
        interval="1d",
        auto_adjust=True,  #adjusts for stock splits
        progress=False, #no progress bar in web server log
        threads=True, #fetch several tickers at a time
    )
   
    if data.empty:
        raise ValueError("Yahoo Finance returned no data.")  #In case Yahoo limits us
    return daily_returns(data["Close"])

def parse_index_weights(raw):
    #Pull the ticker and index weight out of the IJH holdings CSV. 

    lines = raw.splitlines()

    # Find the real header rather than hard-coding a row number, since the number of metadata rows could change. The line may start with a quote or a space, so strip those before checking.
    try:
        start = next(
            i for i, line in enumerate(lines)
            if line.lstrip().strip('"').startswith("Ticker")
        )
    except StopIteration:
        raise ValueError("No header row found in the holdings file.")

    holdings = pd.read_csv(io.StringIO("\n".join(lines[start:])))

    weights = holdings[["Ticker", "Weight (%)"]].copy()
    weights.columns = ["Symbol", "Weight"]
    weights["Symbol"] = weights["Symbol"].apply(normalize_symbol)

    # Values arrive as quoted text, and larger numbers would carry commas,so strip those before converting. errors="coerce" turns anything unparseable into NaN instead of raising.
    weights["Weight"] = pd.to_numeric(
        weights["Weight"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Drops the cash and futures rows, which have no real weight.
    return weights.dropna(subset=["Weight"]).reset_index(drop=True)


def fetch_index_weights():
    #Downloads the IJH holdings file and returns each company's weight.
    response = requests.get(
        IJH_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return parse_index_weights(response.text)     