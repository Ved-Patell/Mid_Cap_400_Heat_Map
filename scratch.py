import pandas as pd
import chart

companies = pd.DataFrame({
    "Symbol": ["AA","AAL"],
    "Security":["Alcoa","American Airlines Group"],
    "GICS Sector":["Materials","Industrials"],
})
returns = pd.DataFrame({"Symbol":["AA","AAL"],"Return":[2.0,-1.0]})

merged = chart.merge_returns(returns, companies)
print(merged)
print(chart.summarize(merged, pd.Timestamp("2026-08-12")))