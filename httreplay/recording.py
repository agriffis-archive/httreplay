import os
import json


class ReplayRecording(object):
    """
    Holds on to a set of request keys and their response values.
    Can be used to reproduce HTTP/HTTPS responses without using
    the network.
    """
    def __init__(self, jsonable=None):
        super(ReplayRecording, self).__init__()
        self.requests = []
        self.responses = []
        if jsonable:
            self._from_jsonable(jsonable)

    def _from_jsonable(self, jsonable):
        self.requests = [r['request'] for r in jsonable]
        self.responses = [r['response'] for r in jsonable]

    def to_jsonable(self):
        assert len(self.requests) == len(self.responses)
        return [dict(request=request, response=response)
                for request, response in zip(self.requests, self.responses)]

    def has_request(self, request_signature):
        return self.get_request(request_signature) is not None

    def get_request(self, request_signature):
        try:
            return self.requests[self.requests.index(request_signature)]
        except ValueError:
            return None

    def get_response(self, request_signature):
        try:
            return self.responses[self.requests.index(request_signature)]
        except ValueError:
            return None


class ReplayRecordingManager(object):
    """
    Loads and saves replay recordings as to json files.
    """
    @classmethod
    def load(cls, recording_file_name):
        try:
            with open(recording_file_name) as recording_file:
                recording = ReplayRecording(json.load(recording_file))
        except IOError:
            recording = None
        if recording is None:
            recording = ReplayRecording()
        return recording

    @classmethod
    def save(cls, recording, recording_file_name):
        dirname, _ = os.path.split(recording_file_name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(recording_file_name, 'w') as recording_file:
            json.dump(
                recording.to_jsonable(),
                recording_file,
                indent=4,
                sort_keys=True)
