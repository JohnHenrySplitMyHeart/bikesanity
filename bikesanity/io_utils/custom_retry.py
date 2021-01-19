from itertools import takewhile

from requests.packages.urllib3.util.retry import Retry

from bikesanity.io_utils import log_handler as log_handler


class CustomRetry(Retry):

    def get_backoff_time(self):
        # Modification here - remove instant retry
        consecutive_errors_len = len(
            list(
                takewhile(lambda x: x.redirect_location is None, reversed(self.history))
            )
        )
        backoff_value = self.backoff_factor * (2 ** (consecutive_errors_len-1))
        log_handler.log.warn('Backing off retry for {0} seconds'.format(backoff_value))
        return min(self.BACKOFF_MAX, backoff_value)

    def increment(self, method=None, url=None, response=None, error=None, _pool=None, _stacktrace=None, ):
        log_handler.log.warn('Retrying through custom retrier')
        if response and response.status == 429:
            log_handler.log.error('Received 429 - off we go')
            raise RuntimeError('Have been rate limited')
        if response and response.status == 403:
            log_handler.log.error('Received 403 - off we go')
            raise RuntimeError('Got an unauthorized')

        return super().increment(method, url, response, error, _pool, _stacktrace)
