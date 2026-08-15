import pandas as pd
import pytest

from chart import build_treemap, merge_returns, summarize

AS_OF = pd.Timestamp("2026-08-12")


class TestMergeReturns:

    def test_attaches_sectors(self, returns, companies):
        merged = merge_returns(returns, companies)
        row = merged.loc[merged["Symbol"] == "ZION"].iloc[0]
        assert row["GICS Sector"] == "Financials"

    def test_keeps_every_matching_company(self, returns, companies):
        assert len(merge_returns(returns, companies)) == 4

    def test_drops_symbols_with_no_sector(self, companies):
        # A ticker Yahoo returns but Wikipedia has never heard of cannot be placed in a sector block, so it should be left out.
        returns = pd.DataFrame({"Symbol": ["AAON", "MYSTERY"],
                                "Return": [1.0, 2.0]})
        merged = merge_returns(returns, companies)
        assert merged["Symbol"].tolist() == ["AAON"]

    def test_adds_an_equal_size_column(self, returns, companies):
        merged = merge_returns(returns, companies)
        assert set(merged["Size"]) == {1}


class TestSummarize:

    def test_counts_advancers_and_decliners(self, returns, companies):
        # AAON +10, MOG-A -5, ZION 0, CELH +2.5
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["advancers"] == 2
        assert stats["decliners"] == 2

    def test_flat_stocks_are_not_advancers(self, returns, companies):
        # Zero is not a gain. That's a judgment call, so it is pinned down
        # by a test rather than left to whoever reads the code next.
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["advancers"] == 2

    def test_totals_match_the_row_count(self, returns, companies):
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["advancers"] + stats["decliners"] == stats["total"]

    def test_calculates_the_median(self, returns, companies):
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["median"] == pytest.approx(1.25)

    def test_identifies_leading_and_lagging_sectors(self, returns, companies):
        # Industrials averages (10 + -5) / 2 = 2.5, Financials 0.0,
        # Consumer Staples 2.5.
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["lagging_sector"] == "Financials"
        assert stats["leading_value"] >= stats["lagging_value"]

    def test_formats_the_date_readably(self, returns, companies):
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["as_of"] == "August 12, 2026"

    def test_benchmark_is_none_when_not_supplied(self, returns, companies):
        stats = summarize(merge_returns(returns, companies), AS_OF)
        assert stats["benchmark"] is None

    def test_benchmark_is_included_when_supplied(self, returns, companies):
        stats = summarize(merge_returns(returns, companies), AS_OF,
                          benchmark=0.42)
        assert stats["benchmark"] == 0.42


class TestBuildTreemap:

    def test_produces_a_treemap(self, returns, companies):
        figure = build_treemap(merge_returns(returns, companies))
        assert figure.data[0].type == "treemap"

    def test_includes_every_company_and_sector(self, returns, companies):
        figure = build_treemap(merge_returns(returns, companies))
        labels = list(figure.data[0].labels)
        assert "AAON" in labels
        assert "Financials" in labels
