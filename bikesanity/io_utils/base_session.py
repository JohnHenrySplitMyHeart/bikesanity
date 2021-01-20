from abc import ABC, abstractmethod
import logging
import requests
import random
import math

from .custom_retry import CustomRetry
from .timeout_http_adaptor import TimeoutHTTPAdapter
from .resources import unserialize_resource_stream


log = logging.getLogger(__name__)


class BaseSession(ABC):

    BACKOFF_FACTOR = 10
    TOTAL_RETRIES = 2
    REQUEST_TIMEOUT = 20

    SERIALIZED_RESOURCES = 'serialized.pickle'

    def __init__(self):
        self.session = None
        self.user_agent = self.generate_random_user_agent()
        self.headers = unserialize_resource_stream([self.SERIALIZED_RESOURCES])['HEADERS']

    def generate_random_user_agent(self):
        return random.choice(unserialize_resource_stream([self.SERIALIZED_RESOURCES])['USER_AGENTS'])

    def connect_session(self):
        session = requests.session()

        retry_strategy = CustomRetry(
            total=self.TOTAL_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504, 403],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=self.BACKOFF_FACTOR
        )

        # Mount it for both http and https usage
        adapter = TimeoutHTTPAdapter(timeout=self.REQUEST_TIMEOUT)
        adapter.max_retries = retry_strategy
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        self.session = session


    def get_session(self):
        return self.session

    def handle_cookies(self):
        browser_cookie = self.session.cookies.get('browser')
        browserx_cookie = self.session.cookies.get('browserx')

        if not browserx_cookie:
            browserx_cookie = str(math.floor(random.random() * 10000000))
            self.session.cookies.set('browserx', browserx_cookie, domain='.crazyguyonabike.com')

        if not browser_cookie or '.' in browser_cookie: return

        browser_cookie = '{0}.{1}'.format(browser_cookie, browserx_cookie)
        log.warn('Setting cookies: {0}'.format(browser_cookie))
        self.session.cookies.set('browser', browser_cookie, domain='.crazyguyonabike.com')

    @abstractmethod
    def make_request(self, url):
        self.headers["User-Agent"] = self.user_agent
        self.handle_cookies()

    @abstractmethod
    def make_stream_request(self, url):
        self.headers["User-Agent"] = self.user_agent
        self.handle_cookies()
