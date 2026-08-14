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

