import io
import os
from abc import ABC, abstractmethod

from bikesanity.io_utils import log_handler
from bikesanity.io_utils.plain_session import PlainSession
from bikesanity.io_utils.throttled import ThrottledSession


class BaseRetriever(ABC):

    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def retrieve_index(self, url, error_message):
        pass

    @abstractmethod
    def retrieve_page(self, url, original_id, error_message):
        pass

    @abstractmethod
    def retrieve_image_large(self, path, error_message):
        pass

    def retrieve_image_small(self, path, error_message='{0}'):
        return self.retrieve_image_large(path, error_message)

    def retrieve_js(self, path):
        pass

    def retrieve_css(self, path):
        pass


class DownloadingRetriever(BaseRetriever):

    BASE_URL = 'https://www.crazyguyonabike.com'

    def __init__(self):
        super().__init__(self.BASE_URL)
        self.session = self._get_working_session(throttled=True)
        self.fast_session = self._get_working_session(throttled=False)

    def _get_working_session(self, throttled=True):
        session = None
        while not session:
            try:
                log_handler.log.warning('Attempting to create new session')
                session = ThrottledSession() if throttled else PlainSession()
                session.connect_session()
            except Exception as exc:
                log_handler.log.warning('Session creation failure - retrying: {0}'.format(exc))
                session = None
        return session

    def retrieve_index(self, url, error_message="{0}"):
        return self._retrieve_page(url, error_message)

    def retrieve_page(self, url, original_id, error_message="{0}"):
        page, resolved_url = self._retrieve_page(url, error_message)
        return page

    def _retrieve_page(self, url, error_message):
        try:
            response = self.session.make_request(url)
            if response.status_code == 200:
                return response.content, response.url
            else:
                message = error_message.format(url) + str(response.status_code)
                log_handler.log.error(message)
                raise RuntimeError(message)
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))
            raise

    def retrieve_image_large(self, path, error_message="{0}"):
        try:
            url = self.base_url + path
            return self.download_binary(self.fast_session, url)
        except Exception as exc:
            log_handler.log.warn(error_message.format(exc))

    def retrieve_js(self, path):
        url = self.base_url + '/javascript/' + path
        return self.download_binary(self.fast_session, url)

    def retrieve_css(self, path):
        url = self.base_url + '/css/' + path
        return self.download_binary(self.fast_session, url)

    def download_binary(self, session, url):
        try:
            log_handler.log.info("Downloading {0}".format(url))
            with session.make_stream_request(url) as response:
                bin_bytes = io.BytesIO(response.raw.read())
            return bin_bytes
        except Exception as exc:
            log_handler.log.error("Failure to download: {0}".format(url))
            raise




class LocalRetriever(BaseRetriever):

    def __init__(self, local_handler):
        super().__init__('')
        self.local_handler = local_handler

    def retrieve_index(self, url, error_message="{0}"):
        return self.local_handler.get_index(), self.local_handler.journal_id

    def retrieve_page(self, url, original_id, error_message="{0}"):
        try:
            return self.local_handler.get_html_page_id(original_id)
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))

    def retrieve_image_large(self, path, error_message="{0}"):
        try:
            # Remove any trailing querystrings from the url, or leading slashes
            if path.startswith('/'): path = path[1:]
            if '?' in path: path = path[:path.rfind('?')]

            return self.local_handler.get_image_binary(path)
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))


class ExportRetriever(BaseRetriever):

    def __init__(self, local_handler):
        super().__init__('')
        self.local_handler = local_handler

    def retrieve_index(self, url, error_message='{0}'):
        try:
            return self.local_handler.get_html_page_id('index', additional_path='small'), self.local_handler.journal_id
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))

    def retrieve_page(self, url, original_id, error_message='{0}'):
        try:
            return self.local_handler.get_html_page_id(original_id, additional_path='small/page')
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))

    def retrieve_image_large(self, path, error_message='{0}'):
        try:
            # Take just the filename
            filename = os.path.basename(path)
            return self.local_handler.get_image_binary(filename, additional_path='large/pics')
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))

    def retrieve_image_small(self, path, error_message='{0}'):
        try:
            # Take just the filename
            filename = os.path.basename(path)
            return self.local_handler.get_image_binary(filename, additional_path='small/pics')
        except Exception as exc:
            log_handler.log.error(error_message.format(exc))
