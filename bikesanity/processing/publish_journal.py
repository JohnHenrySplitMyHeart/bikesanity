from enum import Enum, auto
import os

import bikesanity.io_utils.log_handler as log_handler
from bikesanity.entities.journal import Journal
from bikesanity.io_utils.local_journal import LocalJournalHandler
from bikesanity.output_transformers.templated_html_output import TemplatedHtmlOutput


class PublicationFormats(Enum):
    TEMPLATED_HTML = auto()


class PublishJournal:

    PROCESSED_DIRECTORY = 'processed'
    TEMPLATES_DIRECTORY = '../templates/'

    def __init__(self, input_location, output_location, journal_id):
        self.journal_id = journal_id

        self.input_location = os.path.join(input_location, self.PROCESSED_DIRECTORY)
        self.output_location = os.path.join(output_location, self.PROCESSED_DIRECTORY)

        self.input_handler = LocalJournalHandler(self.input_location, journal_id)
        self.output_handler = LocalJournalHandler(self.output_location, journal_id)

    def get_publication_location(self):
        return self.output_handler.get_html_path('index.html')

    def publish_journal_id(self, format: PublicationFormats, progress_callback=None):
        # Load the journal by unpickling from the processed form
        journal = self.input_handler.load_serialized_journal()
        if not journal:
            log_handler.log.error('Failure to load any journal with ID {0} - have you processed it?'.format(self.journal_id))
            return

        # Switch based on journal format required
        if format == PublicationFormats.TEMPLATED_HTML:
            self.publish_journal_templated_html(journal, progress_callback)


    def publish_journal_templated_html(self, journal: Journal, progress_callback=None):
        templated_output = TemplatedHtmlOutput(self.output_handler, progress_callback)
        templated_output.output_journal(journal)
