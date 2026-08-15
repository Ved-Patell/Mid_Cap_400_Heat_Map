"""Turns the merged data into a treemap and a set of summary numbers."""

import plotly.express as px

from config import COLOR_DOWN, COLOR_FLAT, COLOR_RANGE, COLOR_UP

SIZE_COLUMN = "Size"


def merge_returns(returns, companies):
    """Join returns onto the company list, keeping only rows with a sector.

    A ticker with no matching sector cannot be placed in a sector block, so
    it is dropped rather than grouped under a blank heading.
    """
    merged = returns.merge(companies, on="Symbol", how="left")
    merged = merged.dropna(subset=["GICS Sector"])
    merged[SIZE_COLUMN] = 1  # equal-sized boxes; see README for the alternative
    return merged.reset_index(drop=True)


def summarize(merged, as_of, benchmark=None):
    """Build the plain-language numbers shown above the chart."""
    advancers = int((merged["Return"] > 0).sum())
    by_sector = merged.groupby("GICS Sector")["Return"].mean().sort_values()

    return {
        "as_of": as_of.strftime("%B %d, %Y"),
        "total": len(merged),
        "advancers": advancers,
        "decliners": len(merged) - advancers,
        "median": round(float(merged["Return"].median()), 2),
        "leading_sector": by_sector.index[-1],
        "leading_value": round(float(by_sector.iloc[-1]), 2),
        "lagging_sector": by_sector.index[0],
        "lagging_value": round(float(by_sector.iloc[0]), 2),
        "benchmark": benchmark,
    }


def build_treemap(merged):
    """Build the Plotly treemap figure."""
    figure = px.treemap(
        merged,
        path=["GICS Sector", "Symbol"],
        values=SIZE_COLUMN,
        color="Return",
        color_continuous_scale=[
            [0.0, COLOR_DOWN],
            [0.5, COLOR_FLAT],
            [1.0, COLOR_UP],
        ],
        color_continuous_midpoint=0,
        range_color=[-COLOR_RANGE, COLOR_RANGE],
        custom_data=["Security", "Return"],
    )
    figure.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>%{customdata[0]}"
            "<br>%{customdata[1]:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(width=1, color="#14161a")),
    )
    figure.update_layout(
        margin=dict(t=4, l=4, r=4, b=4),
        height=640,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def render_chart_html(merged):
    """Return the chart as an HTML fragment to drop into the page."""
    figure = build_treemap(merged)
    # include_plotlyjs="cdn" loads the Plotly library from the internet
    # instead of pasting all of it into our page.
    return figure.to_html(full_html=False, include_plotlyjs="cdn")
