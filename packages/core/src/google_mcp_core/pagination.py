from __future__ import annotations

from typing import Any, Callable, Generator, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def paginate(
    request_fn: Callable[[Optional[str], Optional[int]], Tuple[Sequence[T], Optional[str]]],
    page_token: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[list[T], Optional[str]]:
    items, next_token = request_fn(page_token, limit)
    return list(items), next_token


def paginate_google_api(
    api_method: Callable[..., Any],
    **kwargs
) -> Generator[dict[str, Any], None, None]:
    """
    Generator that handles pagination for Google API methods.
    Yields individual items from paginated API responses.
    """
    page_token = kwargs.pop('pageToken', None)
    
    while True:
        if page_token:
            kwargs['pageToken'] = page_token
        
        response = api_method(**kwargs).execute()
        
        # Try common pagination patterns
        items = None
        for key in ['items', 'files', 'messages', 'events', 'connections', 'results', 'entries']:
            if key in response:
                items = response[key]
                break
        
        if items:
            for item in items:
                yield item
        
        # Check for next page token
        page_token = response.get('nextPageToken') or response.get('pageToken')
        if not page_token:
            break
