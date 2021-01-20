import datetime
import random
import time

from bikesanity.io_utils import log_handler as log_handler
from .base_session import BaseSession


class ThrottledSession(BaseSession):

    STANDARD_REQUEST_RATE_LIMITER = 25
    STANDARD_REQUEST_RATE_LIMITER_MIN = 25
    STANDARD_REQUEST_RATE_LIMITER_MAX = 30
    FAILED_REQUEST_RATE_LIMITER = 5

    def __init__(self):
        super().__init__()
        self.last_request = None
        self.current_rate_limit = self.STANDARD_REQUEST_RATE_LIMITER

    def _stochastic_delay(self):
        return random.randrange(self.STANDARD_REQUEST_RATE_LIMITER_MIN, self.STANDARD_REQUEST_RATE_LIMITER_MAX)

    def _wait_since_last_request(self):
        rate_limit_delay = self._stochastic_delay()

        if not self.last_request:
            self.last_request = datetime.datetime.now()
        while (datetime.datetime.now() - self.last_request).total_seconds() < rate_limit_delay:
            time.sleep(0.2)
        self.last_request = datetime.datetime.now()

    def make_request(self, url):
        super().make_request(url)
        try:
            self._wait_since_last_request()
            return self.session.get(url, headers=self.headers)
        except Exception as exc:
            # Log the exception, delay a while, then raise
            log_handler.log.error("Error connecting when downloading {0}".format(url))
            time.sleep(self.FAILED_REQUEST_RATE_LIMITER)
            raise

    def make_stream_request(self, url):
        super().make_stream_request(url)
        return self.session.get(url, headers=self.headers, stream=True)
