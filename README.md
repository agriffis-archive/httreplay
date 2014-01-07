# httreplay

A Python HTTP (and HTTPS!) record-and-replay library for testing.

The library supports network requests made via `httplib`, `requests >= 1.2.3` (including `requests 2.x`), and `urllib3 >= 0.6`.


## Installation

Simply `pip install httreplay` to get going.


## Basic usage

The easiest way to get going is to use the context manager:

```python
import requests
from httreplay import replay

with replay('/tmp/recording_file.json'):
    result = requests.get("http://example.com/")
    # ... issue as many requests as you like ...
    # ... repeat requests won't hit the network ...
```

When a request is issued that is not found in the recording file, `httreplay` will let the request go through the network. Once the response is available, it will automatically be written to the recording file.

When the same request is issued a second time, `httreplay` simply returns the pre-recorded response &mdash; no network for you!

If you can't use the context manager for some reason, you can use the `start_replay` and `stop_replay` methods instead:

```python
import requests
from httreplay import start_replay, stop_replay

start_replay('/tmp/recording_file.json')
result = requests.get("http://example.com/")
stop_replay()
```

As you've probably noticed, all recordings are to `json` files. They're easy to inspect, modify, and generate!


## Slightly more advanced usage

There are two problems that most people who use HTTP recording and replay encounter pretty quickly:

1. HTTP requests can contain sensitive information not suitable for storing in recordings
2. HTTP requests can contain inconsequential information or can vary in ways that are inconsequential for the purposes of replay

Luckily, `httreplay` provides some simple tools to deal with these. Under the hood, `httreplay` turns the many portions of a request into a "key" &mdash; effectively, a tuple that uniquely identifies the request. You can write custom code to decide how three important bits of the key are generated: the `url_key` value from the request's URL, the `body_key` value from the body content, and the `headers_key` from the headers dictionary.

The `replay` context manager and the `start_replay` method both take the following additional parameters:

- `url_key`: a function that consumes a URL (string) and returns its key. By default, the URL is used directly.
- `body_key`: a function that consumes a request body (bytes) and returns its key. By default, the body is used directly.
- `headers_key`: a function that consumes headers (dict) and returns a new key (usually, another dict). By default, the headers dict is used directly.

There are some common things you might want to do in each of these cases; the `httreplay.utils.*` methods are a (very random) grab-bag of useful utility methods. These include:

- `sort_string(s)`: a stupid method to sort a string. You'd be surprised how often a simple URL or body-content sort is sufficient for building a key!
- `sort_string_key()`: returns a key function that sorts a string; suitable for use with the `url_key` and `body_key` parameters
- `filter_query_params(url, remove_params)`: given an absolute URL, remove any query params with names in the `remove_params` list. Very handy for scrubbing sensitive or inconsequential data.
- `filter_query_params_key(remove_params)`: returns a key function that removes params from all presented URLs; suitable for use with the `url_key` parameter
- `filter_headers(headers, remove_headers)`: given a header dict, remove any keys found in the `remove_headers` list and return the dict.
- `filter_headers_key(remove_headers)`: returns a key function that removes headers from all presented headers dict; suitable for use with the `headers_key` parameter.

Your exact needs will probably vary, but hopefully these three methods (and their corresponding key functions) will get you started. Putting it all together, here's an example:

```python
from httreplay import replay, sort_string_key, filter_query_params_key, filter_headers_key

with replay(
        '/tmp/recording_file.json',
        url_key=filter_query_params_key(['apiSecret']),
        body_key=sort_string_key,
        headers_key=filter_headers_key(['timeStamp', 'nonce'])):
    result = requests.get("http://example.com/?apiSecret=SUPER_SECRET")
```


## Using in Django tests

I use `httreplay` extensively in my current app, [Cloak](https://www.getcloak.com/), the website for which is a fairly standard Django app. Here's (roughly) how I've integrated `httreplay` into my tests:

```python
from django.test import TestCase
from django.conf import settings
from httreplay import start_replay, stop_replay, filter_headers_key
import os


class ReplayTestCase(TestCase):
    def _test_name_for_replay_file(self):
        """
        A hack to figure out the current test's name.

        In this configuration, each *test method* gets its own
        recording file -- probably what you typically want.
        """
        return self.__str__().split(' ')[0]

    def _replay_file_name(self):
        """
        A hack to determine where the test's recording should
        be placed.

        We typically use a relative directory for HTTREPLAY_RECORDS_BASE_DIRECTORY,
        but it's entirely up to you.

        The final directory path looks like:

            base_directory/test_class_name/test_method_name.json

        Pretty handy!
        """
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                settings.HTTREPLAY_RECORDINGS_BASE_DIRECTORY,
                self.__class__.__name__,
                "{0}.json".format(self._test_name_for_replay_file())))

    def setUp(self):
        """Start replay recording."""
        super(ReplayTestCase, self).setUp()
        start_replay(
            replay_file_name=self._replay_file_name(),
            url_key=self._custom_replay_url_key,
            body_key=self._custom_replay_body_key,
            headers_key=filter_headers_key(["Authorization", "User-Agent"]),
        )

    def tearDown(self):
        """Stop replay recording."""
        super(ReplayTestCase, self).tearDown()
        stop_replay()
```


## Genealogy

In early 2002, I forked [`vcr.py`](https://github.com/kevin1024/vcrpy) into my project-of-the-moment, [Cloak](https://www.getcloak.com/).

I did this because `vcr.py` was partway there, but (1) didn't have all the features I needed, (2) was completely broken where multiple-requests-per-recording was concerned, and (3) didn't seem to be maintained.

I just noticed that `vcr.py` is a once again alive, but I'm not sure *how* alive. In any case, this fork has diverged significantly enough that it's effectively its own library now.


## Other notes

This is released under the MIT license.

Contributors:

- [Aron Griffis](https://github.com/agriffis/)
- [Dave Peck](https://github.com/davepeck/)

Pull requests are *most* welcome. Here are some of the many things I'd like to tackle:

- proper testing
- continuous integration
- Python 3.x support (currently we support Python 2.7 only)
- clean up the `*_key` parameters, and the generation of request keys in general, so that the signatures are more consistent and there are hooks for _all_ parts of the request
- provide response header and content filtering hooks, primarily for sensitive information
- actual mock-then-assert functionality





