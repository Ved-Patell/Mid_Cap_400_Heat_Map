import pandas as pd
import pytest

from datasets import daily_returns, normalize_symbol, parse_constituents


class TestNormalizeSymbol:
    """The dot-to-hyphen fix, which fails silently if we get it wrong."""

    def test_converts_dotted_share_class(self):
        assert normalize_symbol("MOG.A") == "MOG-A"

    def test_leaves_ordinary_tickers_alone(self):
        assert normalize_symbol("AAON") == "AAON"

    def test_strips_surrounding_whitespace(self):
        assert normalize_symbol("  ZION  ") == "ZION"

    def test_accepts_non_string_input(self):
        # read_html sometimes hands back numbers for stray cells.
        assert normalize_symbol(123) == "123"


class TestParseConstituents:

    def test_returns_expected_columns(self, wiki_html):
        companies = parse_constituents(wiki_html)
        assert list(companies.columns) == ["Symbol", "Security", "GICS Sector"]

    def test_reads_every_row(self, wiki_html):
        assert len(parse_constituents(wiki_html)) == 4

    def test_normalizes_symbols_while_parsing(self, wiki_html):
        symbols = parse_constituents(wiki_html)["Symbol"].tolist()
        assert "MOG-A" in symbols
        assert "MOG.A" not in symbols

    def test_keeps_sector_labels(self, wiki_html):
        sectors = set(parse_constituents(wiki_html)["GICS Sector"])
        assert sectors == {"Industrials", "Financials", "Consumer Staples"}

    def test_raises_when_table_is_missing(self):
        html = "<html><body><table><tr><th>Nope</th></tr></table></body></html>"
        with pytest.raises(ValueError):
            parse_constituents(html)


class TestDailyReturns:

    def test_calculates_a_gain(self, closes):
        returns, _ = daily_returns(closes)
        aaon = returns.loc[returns["Symbol"] == "AAON", "Return"].iloc[0]
        assert aaon == pytest.approx(10.0)

    def test_calculates_a_loss(self, closes):
        returns, _ = daily_returns(closes)
        moog = returns.loc[returns["Symbol"] == "MOG-A", "Return"].iloc[0]
        assert moog == pytest.approx(-5.0)

    def test_unchanged_price_is_zero(self, closes):
        returns, _ = daily_returns(closes)
        zion = returns.loc[returns["Symbol"] == "ZION", "Return"].iloc[0]
        assert zion == pytest.approx(0.0)

    def test_drops_tickers_with_no_data(self, closes):
        # A ticker Yahoo knows nothing about should be left out entirely,
        # not drawn as a flat box that looks like a real result.
        returns, _ = daily_returns(closes)
        assert "DEAD" not in returns["Symbol"].tolist()
        assert len(returns) == 3

    def test_reports_the_latest_date(self, closes):
        _, as_of = daily_returns(closes)
        assert as_of == pd.Timestamp("2026-08-12")

    def test_uses_the_two_most_recent_days(self):
        # Given three days, compare day 3 to day 2 and ignore day 1.
        closes = pd.DataFrame(
            {"AAON": [1.0, 100.0, 150.0]},
            index=pd.to_datetime(["2026-08-10", "2026-08-11", "2026-08-12"]),
        )
        returns, _ = daily_returns(closes)
        assert returns["Return"].iloc[0] == pytest.approx(50.0)

    def test_raises_with_only_one_day(self):
        # This is what a Sunday or a holiday would look like if we only asked for two calendar days of history.
        closes = pd.DataFrame(
            {"AAON": [100.0]}, index=pd.to_datetime(["2026-08-12"])
        )
        with pytest.raises(ValueError):
            daily_returns(closes)
