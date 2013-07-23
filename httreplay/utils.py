import urllib
import urlparse


# XXX this is an odd grab-bag. Something more principled?


def sort_string(s):
    """A simple little toy to sort a string."""
    return ''.join(sorted(list(s))) if s else s


def sort_string_key():
    """Returns a key function that produces a key by sorting a string."""
    return sort_string


def filter_query_params(url, remove_params):
    """
    Remove all provided parameters from the query section of the ``url``.

    :param remove_params: A list of query parameters to scrub from the URL.
    :type remove_params: list
    """
    if not url:
        return url

    parsed_url = urlparse.urlparse(url)
    parsed_qs = urlparse.parse_qs(parsed_url.query)
    for filter_query_param in remove_params:
        if filter_query_param in parsed_qs:
            del parsed_qs[filter_query_param]
    filtered_qs = urllib.urlencode(parsed_qs)
    filtered_parse_result = urlparse.ParseResult(
        scheme=parsed_url.scheme,
        netloc=parsed_url.netloc,
        path=parsed_url.path,
        params=parsed_url.params,
        query=filtered_qs,
        fragment=parsed_url.fragment)
    filtered_url = urlparse.urlunparse(filtered_parse_result)
    return filtered_url


def filter_query_params_key(remove_params):
    """
    Returns a key function that produces a key by removing params from a URL.

    :param remove_params: A list of query params to scrub from provided URLs.
    :type remove_params: list
    """
    def filter(url):
        return filter_query_params(url, remove_params)
    return filter


def filter_headers(headers, remove_headers):
    """
    Remove all desired headers from the provided ``headers`` dict.

    :param remove_headers: A list of header names to remove.
    :type remove_headers: list
    """
    for remove_header in remove_headers:
        if remove_header in headers:
            del headers[remove_header]
    return headers


def filter_headers_key(remove_headers):
    """
    Returns a key function that produces a key by removing headers from a dict.

    :param remove_headers: A list of header names to remove.
    :type remove_headers: list
    """
    def filter(headers):
        return filter_headers(headers, remove_headers)
    return filter
