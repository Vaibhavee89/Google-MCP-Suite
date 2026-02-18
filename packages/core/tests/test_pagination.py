from google_mcp_core.pagination import paginate


def test_paginate_returns_items_and_token():
    def request_fn(page_token, limit):
        assert page_token is None
        assert limit == 3
        return ([{"id": 1}, {"id": 2}], "next")

    items, token = paginate(request_fn, page_token=None, limit=3)
    assert items == [{"id": 1}, {"id": 2}]
    assert token == "next"
