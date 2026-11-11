import pytest
from googleapiclient.errors import HttpError

from google_mcp_core.retry import execute_with_retry


def _flaky(*outcomes):
    """Callable returning/raising each outcome in turn; `.calls` counts invocations."""
    it = iter(outcomes)

    def fn():
        fn.calls += 1
        outcome = next(it)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    fn.calls = 0
    return fn


@pytest.mark.parametrize("status", [429, 503])
def test_retries_transient_status_then_succeeds(status, http_error, sleeps):
    fn = _flaky(http_error(status), http_error(status), {"ok": True})
    assert execute_with_retry(fn) == {"ok": True}
    assert fn.calls == 3
    assert len(sleeps) == 2


@pytest.mark.parametrize("status", [500, 502, 504])
def test_other_5xx_are_retried_too(status, http_error):
    fn = _flaky(http_error(status), "done")
    assert execute_with_retry(fn) == "done"
    assert fn.calls == 2


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_client_errors_are_not_retried(status, http_error, sleeps):
    fn = _flaky(http_error(status), "never reached")
    with pytest.raises(HttpError) as exc:
        execute_with_retry(fn)
    assert exc.value.resp.status == status
    assert fn.calls == 1
    assert sleeps == []


def test_gives_up_after_configured_retries(http_error, sleeps):
    fn = _flaky(*[http_error(503) for _ in range(10)])
    with pytest.raises(HttpError) as exc:
        execute_with_retry(fn, retries=3)
    assert exc.value.resp.status == 503
    assert fn.calls == 4  # first try + 3 retries
    assert len(sleeps) == 3


def test_zero_retries_raises_immediately(http_error, sleeps):
    fn = _flaky(http_error(429))
    with pytest.raises(HttpError):
        execute_with_retry(fn, retries=0)
    assert fn.calls == 1
    assert sleeps == []


def test_backoff_grows_exponentially(http_error, sleeps, monkeypatch):
    monkeypatch.setattr("google_mcp_core.retry.random.random", lambda: 0.0)  # no jitter
    fn = _flaky(http_error(429), http_error(429), http_error(429), "ok")
    execute_with_retry(fn, initial_backoff=0.5, backoff_multiplier=2.0)
    assert sleeps == [0.5, 1.0, 2.0]


def test_backoff_jitter_stays_within_bounds(http_error, sleeps):
    fn = _flaky(http_error(503), http_error(503), "ok")
    execute_with_retry(fn, initial_backoff=1.0, backoff_multiplier=2.0)
    assert 1.0 <= sleeps[0] < 2.0
    assert 2.0 <= sleeps[1] < 4.0


def test_success_on_first_try_does_not_sleep(sleeps):
    assert execute_with_retry(lambda: 42) == 42
    assert sleeps == []
