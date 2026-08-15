import os
import time

from flask import Flask, render_template

import chart
import datasets
from benchmark import fetch_benchmark

app = Flask(__name__)

CACHE_SECONDS = int(os.getenv("CACHE_SECONDS","900")) #how long to wait to rebuild chart

cache = {"chart": None, "stats": None, "built_at": 0.0}

def cache_is_fresh(now):
    return cache ["chart"] is not None and now - cache["built_at"] < CACHE_SECONDS

def build_page():
    companies = datasets.fetch_constituents()
    returns, as_of = datasets.fetch_prices(companies["Symbol"].tolist())

    try:
        weights = datasets.fetch_index_weights()
    except Exception:
        app.logger.warning("Could not load index weights; using equal sizes")
        weights = None

    merged = chart.merge_returns(returns, companies, weights=weights)

    if merged.empty:
        raise ValueError("No companies had usable price data.")
    
    stats = chart.summarize(merged, as_of, benchmark=fetch_benchmark())

    return chart.render_chart_html(merged), stats

@app.route("/")
def home():
    now = time.time()

    if not cache_is_fresh(now):
        try:
            cache["chart"], cache["stats"] = build_page()
            cache["built_at"] = now
        except Exception as error:
            app.logger.exception("Could not build the heatmap.")
            return render_template(
                "index.html",
                error=f"{type(error).__name__}: {error}",
            )
    return render_template(
        "index.html", chart=cache["chart"], stats=cache["stats"]
    )

@app.route("/health")
def health():
    return {"status": "ok", "cached": cache["chart"] is not None}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
