from enum import Enum, auto
import os

import bikesanity.io_utils.log_handler as log_handler
from bikesanity.entities.journal import Journal
from bikesanity.io_utils.local_journal import LocalJournalHandler

from bikesanity.output_transformers.templated_html_output import TemplatedHtmlOutput
from bikesanity.output_transformers.json_output import JsonOutput
from bikesanity.output_transformers.pdf_output import PdfOutput


class PublicationFormats(Enum):
    TEMPLATED_HTML = auto()
    JSON_MODEL = auto()
    PDF = auto()


class PublishJournal:

    PROCESSED_DIRECTORY = 'processed'
    TEMPLATES_DIRECTORY = '../templates/'

    def __init__(self, input_location, output_location, journal_id):
        self.journal_id = journal_id

        self.input_location = os.path.join(input_location, self.PROCESSED_DIRECTORY)
        self.output_location = os.path.join(output_location, self.PROCESSED_DIRECTORY)

        self.input_handler = LocalJournalHandler(self.input_location, journal_id)
        self.output_handler = LocalJournalHandler(self.output_location, journal_id)

        self.publication_location = None

    def get_publication_location(self):
        return self.publication_location

    def publish_journal_id(self, format: PublicationFormats, progress_callback=None):
        # Load the journal by unpickling from the processed form
        journal = self.input_handler.load_serialized_journal()
        if not journal:
            log_handler.log.error('Failure to load any journal with ID {0} - have you processed it?'.format(self.journal_id))
            return

        # Switch based on journal format required
        if format == PublicationFormats.TEMPLATED_HTML:
            self.publish_journal_templated_html(journal, progress_callback)
        elif format == PublicationFormats.JSON_MODEL:
            self.export_json_model(journal, progress_callback)
        elif format == PublicationFormats.PDF:
            self.publish_pdf(journal, progress_callback)


    def publish_journal_templated_html(self, journal: Journal, progress_callback=None):
        templated_output = TemplatedHtmlOutput(self.output_handler, progress_callback)
        templated_output.output_journal(journal)
        self.publication_location = self.output_handler.get_html_path('index.html')

    def export_json_model(self, journal: Journal, progress_callback=None):
        json_output = JsonOutput(self.output_handler, progress_callback)
        json_output.output_journal(journal)
        self.publication_location = self.output_handler.get_path('journal.json')

    def publish_pdf(self, journal: Journal, progress_callback=None):
        pdf_output = PdfOutput(self.output_handler, progress_callback)
        pdf_output.output_journal(journal)
        self.publication_location = self.output_handler.get_pdf_path('journal.pdf')
