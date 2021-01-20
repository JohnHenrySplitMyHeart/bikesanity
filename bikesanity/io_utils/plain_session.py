from .base_session import BaseSession


class PlainSession(BaseSession):

    BACKOFF_FACTOR = 1
    TOTAL_RETRIES = 3
    REQUEST_TIMEOUT = 4

    def make_request(self, url):
        super().make_request(url)
        return self.session.get(url, headers=self.headers)

    def make_stream_request(self, url):
        super().make_stream_request(url)
        return self.session.get(url, headers=self.headers, stream=True)
