# S&P MidCap 400 Sector Heatmap


A web app that shows every company in the S&P MidCap 400 as a box on a single
screen. Boxes are grouped into blocks by sector, sized by how much each company
weighs in the index, and colored by how much the stock moved that day. Green is
up, red is down, and the deeper the color the bigger the move.

**Live site:** (https://sandp400-mid-cap-heatmap-bw8b.onrender.com/)

---

## What it does and why

An investor looking at the mid-cap segment has no quick way to see *where* a
day's movement is concentrated. A list of 400 tickers and percentages is
unreadable. Sector averages hide the outliers inside each sector.

This shows both at once. You can tell in about five seconds whether a green day
was broad-based or carried by two sectors, and which companies drove it.

It also answers something a plain index quote can't: **breadth versus
direction.** A day where 300 companies rise slightly while 100 heavyweights
fall hard gives a mostly green chart and a red index. So alongside our own
count of advancers and decliners, the page quotes MDY, the ETF tracking this
index for comparison.

---

## Before you start

You'll need two things installed:

- **Anaconda** -  https://www.anaconda.com/download
- **GitHub Desktop** - https://desktop.github.com 

---

## Setup

### 1. Get the code

**Using GitHub Desktop:**

1. Open GitHub Desktop.
2. **File -> Clone Repository**.
3. Choose the **URL** tab and paste
   `https://github.com/Ved-Patell/Mid_Cap_400_Heat_Map`.
4. Note the **Local Path** shown as that's where the files land,
5. Click **Clone**.


### 2. Open a terminal in the project folder

Every command from here on assumes your terminal is inside the project folder.

**From GitHub Desktop:** **Repository -> Open in Command Prompt** (or Git Bash,
depending on what you have installed). 

### 3. Create and activate a virtual environment

A virtual environment keeps this project's packages separate from everything
else on your computer, so installing our dependencies can't break your other
projects.

```sh
conda create -n heatmap-env python=3.11
conda activate heatmap-env
```

You'll need to run `conda activate heatmap-env` **again in every new terminal
session**. Your prompt
shows `(heatmap-env)` at the front when it's active.


### 4. Install the dependencies

```sh
pip install -r requirements.txt
```


### 5. Set up environment variables

The app reads its API key from a file named `.env`, which is listed in
`.gitignore` and must **never** be committed. 

Create a new file called `.env` in VS Code.

Open `.env` in a text editor and fill it in with any secret keys.

To get an AlphaVantage key, go to https://www.alphavantage.co/support/#api-key and enter an
email address. It's issued instantly, and no payment details are required.

**The key is optional.** Without it the heatmap works exactly as normal.


### 6. Run the app

```sh
python app.py
```

Then open **http://localhost:5000** in a browser.

**The first load takes up to 40 seconds.** 

Press `Ctrl+C` in the terminal to stop the server.

### 7. Run the tests

```sh
pytest
```

You should see **~60 passed**. For a list of every test by name:

```sh
pytest -v
```

**None of the tests make network requests.** Every one uses saved sample
Wikipedia HTML, a small hand-built price table, a trimmed copy of the holdings
file, or a fake API response. This means the suite:

- runs identically with no internet connection,
- gives the same result every time rather than changing with the market,
- never uses up API quota,
- and can test failure cases like a rate-limited API, a delisted ticker, a
  timeout which would be impossible to trigger on purpose against the
  live services.

---

### Checking the live data sources

The tests above deliberately avoid the network, so these commands verify the real
connections:

```sh
# Wikipedia: expect roughly (401, 3)
python -c "import datasets; print(datasets.fetch_constituents().shape)"

# Yahoo Finance: expect two rows with percentages
python -c "import datasets; print(datasets.fetch_prices(['AAON','ZION'])[0])"

# iShares holdings: expect ~400 rows and a weight sum near 100
python -c "import datasets; w=datasets.fetch_index_weights(); print(w.shape, w['Weight'].sum())"
```

---
## Where the data comes from

| What | Source | Why this one |
|---|---|---|
| Company list and GICS sectors | Wikipedia, "List of S&P 400 companies" | No free API exists for index membership which companies belong to the index is S&P Dow Jones Indices' intellectual property. We evaluated the MediaWiki API and rejected it: it returns page content as HTML rather than structured data, so we'd still parse the table with `pandas.read_html` for no benefit. We request the rendered page with a descriptive User-Agent header, since Wikimedia requires clients to identify themselves and refuses default library agents. |
| Daily prices | Yahoo Finance, via `yfinance` | One request covers all ~400 tickers. We tested Alpha Vantage here first and rejected it: the free tier allows  only 25 requests per day at one symbol per request. |
| Index weights (box sizes) | iShares IJH ETF holdings file | IJH tracks this index, so its holdings *are* the index weights.  
| Index benchmark quote (MDY) | Alpha Vantage `GLOBAL_QUOTE` | 
---





