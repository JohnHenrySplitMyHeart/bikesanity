from abc import ABC, abstractmethod
import logging
import requests
import random
import math

from .custom_retry import CustomRetry
from .timeout_http_adaptor import TimeoutHTTPAdapter


log = logging.getLogger(__name__)


class BaseSession(ABC):

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577",
        "Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763,"
        "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    ]

    HEADERS = {
        "Host": "www.crazyguyonabike.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    BACKOFF_FACTOR = 10
    TOTAL_RETRIES = 2
    REQUEST_TIMEOUT = 20

    def __init__(self):
        self.session = None
        self.user_agent = random.choice(self.USER_AGENTS)

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
        self.HEADERS["User-Agent"] = self.user_agent
        self.handle_cookies()

    @abstractmethod
    def make_stream_request(self, url):
        self.HEADERS["User-Agent"] = self.user_agent
        self.handle_cookies()
