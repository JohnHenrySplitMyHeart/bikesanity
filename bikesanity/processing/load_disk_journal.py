import os
import bikesanity.io_utils.log_handler as log_handler
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page
from bikesanity.io_utils.local_journal import LocalJournalHandler
from bikesanity.services.retrievers import LocalRetriever, ExportRetriever

from bikesanity.interpreter.journal_content import JournalContent
from bikesanity.interpreter.page_interpreter import PageInterpreter


class LoadDiskJournal:

    DOWNLOAD_DIRECTORY = 'downloads'
    EXPORTED_DIRECTORY = 'exported'
    PROCESSED_DIRECTORY = 'processed'

    def __init__(self, input_location, output_location, journal_id, exported=False, progress_callback=None):

        self.input_location = os.path.join(input_location, self.EXPORTED_DIRECTORY if exported else self.DOWNLOAD_DIRECTORY)
        self.output_location = os.path.join(output_location, self.PROCESSED_DIRECTORY)
        self.progress_callback = progress_callback

        self.journal_id = journal_id
        self.input_handler = LocalJournalHandler(self.input_location, journal_id)
        self.output_handler = LocalJournalHandler(self.output_location, journal_id)

        # Ensure the output is clear
        self.output_handler.remove_directory('')
        os.makedirs(self.output_location, exist_ok=True)

        self.retriever = ExportRetriever(self.input_handler) if exported else LocalRetriever(self.input_handler)
        self.outputter = LocalRetriever(self.output_handler)

        self.journal_crawler = JournalContent(self.retriever)
        self.page_crawler = PageInterpreter(self.retriever)

    def progress_update(self, percent):
        if self.progress_callback:
            self.progress_callback(progress=percent)

    def get_process_location(self):
        return self.output_handler.get_base_path()

    def load_journal_from_disk(self):
        # Retrieve and process the journal content
        journal = self.journal_crawler.retrieve_journal(None, self.journal_id)
        self.progress_update(percent=10)
        journal = self._process_journal(journal)
        return journal

    def _process_journal(self, journal: Journal):
        journal_id = journal.journal_id

        # Handle standard multi-page journals with a ToC
        if journal.toc:
            log_handler.log.warning('Processing multiple pages for {0}'.format(journal_id))

            # Iterate over all the retrieved pages and pull them separately.
            page_count = 0
            for toc in journal.toc:
                if toc.url:
                    page = self._process_page(toc.original_id)
                    toc.set_page(page)

                # Calculate percentage per page, to keep consumers updated
                self.progress_update(((page_count / len(journal.toc)) * 80) + 10)
                page_count += 1

        else:
            log_handler.log.warning('Processing single page for {0}'.format(journal_id))

            # Handle single-page journals/articles that have all the content on the title page
            journal.single_page = True

            # Create a single new page and set with the title page html
            content_page = Page(journal_id=journal_id, original_id=journal_id, original_html=journal.original_html)

            # Process it as a normal page and add it to the ToC
            content_page = self._process_page(content_page, single=True)
            journal.add_single_page(content_page)
            self.progress_update(percent=90)

        # Save and clear any resources not associated with pages
        journal.save_resources(self.output_handler)
        journal.clear_resources()

        # Finally serialize the parsed data structure and output
        log_handler.log.info('Serializing data for {0}'.format(journal_id), extra={'journal_id': journal_id})
        self.output_handler.serialize_and_save_journal(journal)

        self.progress_update(percent=100)
        log_handler.log.info('Completed {0}'.format(journal_id), extra={'journal_id': journal_id})
        return journal

    def _process_page(self, page_id, single=False):
        log_handler.log.warning('Processing page {0} for {1}'.format(page_id, self.journal_id))

        # Process the page and associated pics and maps
        page = self.page_crawler.retrieve_page(self.journal_id, page_id, None)
        page = self.page_crawler.parse_page(page, single=single)

        # Save locally and clear resources loaded into the page
        page.save_resources(self.output_handler)
        page.clear_resources()

        return page
