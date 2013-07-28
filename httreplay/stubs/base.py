from __future__ import print_function
from httplib import HTTPConnection, HTTPSConnection, HTTPMessage
from cStringIO import StringIO
from ..recording import ReplayRecording, ReplayRecordingManager


class ReplayError(Exception):
    """Generic error base class for the httreplay library."""
    pass


class ReplayConnectionHelper:
    """
    Mixin that provides the ability to serialize and deserialize
    requests and responses into a recording.
    """
    def __init__(self):
        self.__replay_recording = None

    @property
    def _replay_recording(self):
        """Provide the current recording, or create a new one if needed."""
        if self.__replay_recording is None:
            self.__replay_recording = ReplayRecordingManager.load(
                self._replay_settings.replay_file_name)
        return self.__replay_recording

    def request(self, method, url, body=None, headers={}):
        """Process a request, and generate a 'key' for future lookups."""
        # If a key generator for the body is provided, use it.
        # Otherwise, simply use the body itself as the body key.
        if body is not None and self._replay_settings.body_key:
            body_key = self._replay_settings.body_key(body)
        else:
            body_key = body

        # If a key generator for the URL is provided, use it.
        # Otherwise, simply use the URL itself as the URL key.
        if url is not None and self._replay_settings.url_key:
            url_key = self._replay_settings.url_key(url)
        else:
            url_key = url

        # If a key generator for the headers is provided, use it.
        # Otherwise, simply use the headers directly.
        if self._replay_settings.headers_key:
            headers_key = self._replay_settings.headers_key(dict(headers))
        else:
            headers_key = headers

        # Form the current request
        self._replay_current_request = request = dict(
            method=method,
            url=url_key,
            body=body_key,
            headers=headers_key,
            host=self.host,
            port=self.port)

        if request not in self._replay_recording:
            self._baseclass.request(
                self,
                method,
                url,
                body=body,
                headers=headers)

    def getresponse(self, buffering=False):
        """
        Provide a response from the current recording if possible.
        Otherwise, perform an account network request.
        """
        request = self._replay_current_request
        replay_response = self._replay_recording.get(request)
        if replay_response is None:
            response = self._baseclass.getresponse(self)
            status = dict(code=response.status, message=response.reason)
            headers = dict(response.getheaders())
            replay_response = dict(
                status=status,
                headers=headers,
                body=response.read().encode('base64'))
            self._replay_recording[request] = replay_response
            ReplayRecordingManager.save(
                self._replay_recording,
                self._replay_settings.replay_file_name)
        return ReplayHTTPResponse(replay_response)


class ReplayHTTPConnection(ReplayConnectionHelper, HTTPConnection):
    """Generic HTTPConnection with replay."""
    _baseclass = HTTPConnection

    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)
        ReplayConnectionHelper.__init__(self)


class ReplayHTTPSConnection(ReplayConnectionHelper, HTTPSConnection):
    """Generic HTTPSConnection with replay."""
    _baseclass = HTTPSConnection

    def __init__(self, *args, **kwargs):
        # I overrode the init and copied a lot of the code from the parent
        # class because when this happens, HTTPConnection has been replaced
        # by ReplayHTTPConnection,  but doing it here lets us use the original
        # one.
        HTTPConnection.__init__(self, *args, **kwargs)
        ReplayConnectionHelper.__init__(self)
        self.key_file = kwargs.pop('key_file', None)
        self.cert_file = kwargs.pop('cert_file', None)


class ReplayHTTPResponse(object):
    """
    A replay response object, with just enough functionality to make
    the various HTTP/URL libraries out there happy.
    """
    def __init__(self, response):
        self.__replay_current_response = response
        self.reason = self.__replay_current_response['status']['message']
        self.status = self.__replay_current_response['status']['code']
        self.version = None
        self._content = self.__replay_current_response['body'].decode('base64')

        self.msg = HTTPMessage(StringIO(''))
        for k, v in self.__replay_current_response['headers'].iteritems():
            self.msg.addheader(k, v)

        self.length = self.msg.getheader('content-length') or None

    def read(self, chunked=False):
        # XXX what is chunked
        return self._content

    def isclosed(self):
        # XXX what is this -- urllib3 uses it?
        return True

    def getheaders(self):
        return self.__replay_current_response['headers'].iteritems()
