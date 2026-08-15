import benchmark
from benchmark import parse_quote


class TestParseQuote:

    def test_reads_a_positive_change(self):
        payload = {"Global Quote": {"10. change percent": "1.2345%"}}
        assert parse_quote(payload) == 1.2345

    def test_reads_a_negative_change(self):
        payload = {"Global Quote": {"10. change percent": "-0.8700%"}}
        assert parse_quote(payload) == -0.87

    def test_handles_a_missing_percent_sign(self):
        payload = {"Global Quote": {"10. change percent": "1.50"}}
        assert parse_quote(payload) == 1.5

    def test_returns_none_on_rate_limit_message(self):
        # This is what the free tier sends once the daily cap is reached.
        payload = {"Information": "Thank you for using Alpha Vantage!"}
        assert parse_quote(payload) is None

    def test_returns_none_on_empty_quote(self):
        assert parse_quote({"Global Quote": {}}) is None

    def test_returns_none_on_unparseable_number(self):
        payload = {"Global Quote": {"10. change percent": "not a number"}}
        assert parse_quote(payload) is None

    def test_returns_none_on_wrong_type(self):
        assert parse_quote("unexpected string") is None
        assert parse_quote(None) is None


class TestFetchBenchmark:

    def test_returns_none_without_an_api_key(self, monkeypatch):
        # The benchmark is optional. With no key configured the app should skip it quietly, not crash and not make a pointless request.
        monkeypatch.setattr(benchmark, "ALPHAVANTAGE_KEY", None)
        assert benchmark.fetch_benchmark() is None

    def test_returns_none_when_the_request_fails(self, monkeypatch):
        import requests

        def explode(*args, **kwargs):
            raise requests.RequestException("network down")

        monkeypatch.setattr(benchmark, "ALPHAVANTAGE_KEY", "fake-key")
        monkeypatch.setattr(benchmark.requests, "get", explode)
        assert benchmark.fetch_benchmark() is None
