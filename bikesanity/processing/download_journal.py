import os

import bikesanity.io_utils.log_handler as log_handler
from bikesanity.interpreter.journal_content import JournalContent
from bikesanity.interpreter.page_interpreter import PageInterpreter
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page
from bikesanity.io_utils.local_journal import LocalJournalHandler
from bikesanity.io_utils.serializer import Serializer
from bikesanity.services.retrievers import DownloadingRetriever
from bikesanity.services.html_postprocessor import HtmlPostProcessor


class DownloadJournal:

    DOWNLOAD_DIRECTORY = 'downloads'

    def __init__(self, base_location, postprocess_html=True, progress_callback=None):
        self.base_location = os.path.join(base_location, self.DOWNLOAD_DIRECTORY)
        os.makedirs(self.base_location, exist_ok=True)

        self.serializer = Serializer()
        self.retriever = DownloadingRetriever()
        self.html_postprocessor = HtmlPostProcessor()

        self.journal_indexer = JournalContent(self.retriever)
        self.page_crawler = PageInterpreter(self.retriever, progress_callback=progress_callback)

        self.postprocess_html = postprocess_html
        self.progress_callback = progress_callback

    def progress_update(self, percent):
        if self.progress_callback:
            self.progress_callback(progress=percent)

    def get_download_location(self, journal) -> str:
        return os.path.join(self.base_location, journal.journal_id)

    def download_journal_url(self, url, from_page=0):
        try:
            # Retrieve the journal ID from the URL
            log_handler.log.info('Downloading journal {0}'.format(url))
            return self._download_journal_url(url, from_page)
        except Exception as exc:
            log_handler.log.exception('----> Error when processing journal {0}'.format(url))
            raise

    def _download_journal_url(self, url, from_page):

        log_handler.log.info('Resolving index page...')
        self.progress_update(percent=0)

        # Pull the title page and ToC
        journal = self.journal_indexer.retrieve_journal(url, None)
        if not journal: return None
        journal_id = journal.journal_id

        # Update progress
        self.progress_update(percent=5)
        log_handler.log.info('Successfully retrieved journal index. Processing journal ID {0}'.format(journal_id))

        local_journal_handler = LocalJournalHandler(base_path=self.base_location, journal_id=journal_id)

        # Retrieve the JS and CSS resources too
        journal = self.journal_indexer.retrieve_js_css_resources(journal)

        # Update progress
        self.progress_update(percent=10)
        log_handler.log.info('Successfully pulled JS and CSS resources')

        # Apply HTML post-processing for local browsability, if enabled
        if self.postprocess_html:
            self.html_postprocessor.postprocess_journal(journal)

        # Save original sources and clear resources
        journal.save_original_source(local_journal_handler)
        journal.clear_resources()

        # Download all the table of contents
        journal = self._process_journal(journal, local_journal_handler, from_page)

        self.progress_update(percent=100)

        return journal

    def _process_journal(self, journal: Journal, local_journal_handler, from_page):
        journal_id = journal.journal_id

        # Handle standard multi-page journals with a ToC
        if journal.toc:
            log_handler.log.info('Processing multiple pages for {0}'.format(journal_id))
            # Iterate over all the retrieved pages and pull them separately.
            page_num = 1

            for toc in journal.toc:

                # Skip pages previously downloaded if specified
                if page_num < from_page:
                    log_handler.log.info('Skipping page {0}'.format(page_num))
                    page_num += 1
                    continue

                if toc.url:
                    log_handler.log.info('Processing content {0} of {1}'.format(page_num, len(journal.toc)))

                    page = self.page_crawler.retrieve_page(journal_id, toc.original_id, toc.url)
                    toc.set_page(page)

                    # Calculate percentage per page, to keep consumers updated
                    self.progress_update(((page_num / len(journal.toc)) * 80) + 10)

                    self._process_page(toc.page, local_journal_handler)
                    # Calculate percentage per page, to keep consumers updated
                    self.progress_update((((page_num + 0.5) / len(journal.toc)) * 80) + 10)

                page_num += 1
        else:
            log_handler.log.warning('Processing single page for {0}'.format(journal_id))

            # Handle single-page journals/articles that have all the content on the title page
            journal.single_page = True

            # Create a single new page and set with the title page html
            content_page = Page(journal_id=journal_id, original_id=journal_id, original_html=journal.original_html)

            # Process it as a normal page and add it to the ToC
            content_page = self._process_page(content_page, local_journal_handler, single=True)
            journal.add_single_page(content_page)

            # Calculate percentage per page, to keep consumers updated
            self.progress_update(90)

        log_handler.log.info('Completed {0}'.format(journal_id), extra={'journal_id': journal_id})
        return journal

    def _process_page(self, page: Page, local_journal_handler, single=False):

        # Process the page and associated pics and maps
        page = self.page_crawler.parse_page(page, single=single)

        # Apply HTML post-processing for local browsability, if enabled
        if self.postprocess_html:
            self.html_postprocessor.postprocess_page(page)

        # Save original source and newly formatted resources
        page.save_originals(local_journal_handler)
        # Clear resources loaded into the page
        page.clear_resources()
        return page
