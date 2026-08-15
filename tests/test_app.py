import pandas as pd
import pytest

import app as web
from chart import merge_returns, render_chart_html, summarize

AS_OF = pd.Timestamp("2026-08-12")


@pytest.fixture
def client():
    web.app.config["TESTING"] = True
    web.cache.update({"chart": None, "stats": None, "built_at": 0.0})
    return web.app.test_client()


@pytest.fixture
def working_page(monkeypatch, returns, companies):
    #Make build_page succeed without any network calls.
    merged = merge_returns(returns, companies)
    page = (render_chart_html(merged), summarize(merged, AS_OF))
    monkeypatch.setattr(web, "build_page", lambda: page)
    return page


class TestHomePage:

    def test_responds_successfully(self, client, working_page):
        assert client.get("/").status_code == 200

    def test_shows_the_heading(self, client, working_page):
        assert b"S&amp;P MidCap 400" in client.get("/").data

    def test_embeds_the_chart(self, client, working_page):
        assert b"plotly" in client.get("/").data.lower()

    def test_shows_the_summary_numbers(self, client, working_page):
        body = client.get("/").data.decode()
        assert "August 12, 2026" in body
        assert "Advancing" in body

    def test_hides_the_benchmark_when_unavailable(self, client, working_page):
        # Without an API key there is no MDY quote, and that box should not appear at all rather than showing a blank value.
        assert "Index (MDY)" not in client.get("/").data.decode()


class TestBenchmarkDisplay:

    def test_shows_the_benchmark_when_available(self, client, monkeypatch,
                                                returns, companies):
        merged = merge_returns(returns, companies)
        page = (render_chart_html(merged),
                summarize(merged, AS_OF, benchmark=1.23))
        monkeypatch.setattr(web, "build_page", lambda: page)

        body = client.get("/").data.decode()
        assert "Index (MDY)" in body
        assert "+1.23%" in body


class TestErrorHandling:

    def test_shows_a_message_instead_of_crashing(self, client, monkeypatch):
        def explode():
            raise ConnectionError("Yahoo timed out")

        monkeypatch.setattr(web, "build_page", explode)
        response = client.get("/")

        # The visitor gets a readable page.
        assert response.status_code == 200
        assert b"load market data" in response.data

    def test_names_the_underlying_problem(self, client, monkeypatch):
        def explode():
            raise ConnectionError("Yahoo timed out")

        monkeypatch.setattr(web, "build_page", explode)
        assert b"Yahoo timed out" in client.get("/").data


class TestCaching:

    def test_builds_only_once_within_the_cache_window(self, client,
                                                      monkeypatch, returns,
                                                      companies):
        merged = merge_returns(returns, companies)
        page = (render_chart_html(merged), summarize(merged, AS_OF))
        calls = []

        def counted():
            calls.append(1)
            return page

        monkeypatch.setattr(web, "build_page", counted)

        client.get("/")
        client.get("/")
        client.get("/")

        assert len(calls) == 1, "the cached chart should be reused"

    def test_stale_cache_triggers_a_rebuild(self):
        web.cache.update({"chart": "<div></div>", "built_at": 0.0})
        # built_at of 0 means 1970, so any time now is far past the window.
        assert web.cache_is_fresh(1_000_000_000) is False

    def test_empty_cache_is_never_fresh(self):
        web.cache.update({"chart": None, "built_at": 9_999_999_999})
        assert web.cache_is_fresh(9_999_999_999) is False


class TestHealthEndpoint:

    def test_reports_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"