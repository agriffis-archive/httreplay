import os
import json


class ReplayRecording(object):
    """
    Holds on to a set of request keys and their response values.
    Can be used to reproduce HTTP/HTTPS responses without using
    the network.
    """
    def __init__(self, jsonable=None):
        self.request_responses = []
        if jsonable:
            self._from_jsonable(jsonable)

    def _from_jsonable(self, jsonable):
        self.request_responses = [
            (r['request'], r['response']) for r in jsonable ]

    def to_jsonable(self):
        return [dict(request=request, response=response)
                for request, response in self.request_responses]

    def __contains__(self, request):
        return any(rr[0] == request for rr in self.request_responses)

    def __getitem__(self, request):
        try:
            return next(rr[1] for rr in self.request_responses if rr[0] == request)
        except StopIteration:
            raise KeyError

    def __setitem__(self, request, response):
        self.request_responses.append((request, response))

    def get(self, request, default=None):
        try:
            return self[request]
        except KeyError:
            return default


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
