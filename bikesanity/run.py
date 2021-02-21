"""
This is the main entry point for the command-line runner
"""

import os
from pathlib import Path
import click

from bikesanity.io_utils.log_handler import init_logging, log

from bikesanity.processing.download_journal import DownloadJournal
from bikesanity.processing.load_disk_journal import LoadDiskJournal
from bikesanity.processing.publish_journal import PublishJournal, PublicationFormats


BASE_DIRECTORY = 'CycleSanityJournals'

base_path = os.path.join(Path.home(), BASE_DIRECTORY)

@click.group()
def run():
    init_logging()
    os.makedirs(base_path, exist_ok=True)


@run.command()
@click.argument('journal_link')
@click.option('--do-process', is_flag=True, help="Interpret journal content and process resources")
@click.option('--location', default=None, help="Custom download location for journal files")
@click.option('--no-local-readability-postprocessing', is_flag=True, help="Interpret journal content and process resources")
@click.option('--from-page', default=0, help="Pick up a download from the specified page")
def download(journal_link, do_process=False, location=None, no_local_readability_postprocessing=False, from_page=0):
    log.info('Starting download task...')

    download_path = location if location else base_path
    journal = None

    # Download the journal
    try:
        journal_downloader = DownloadJournal(download_path, postprocess_html=not no_local_readability_postprocessing)
        journal = journal_downloader.download_journal_url(journal_link, from_page)

        log.info('Completed download task! Journal downloaded to {0}'.format(journal_downloader.get_download_location(journal)))
    except Exception:
        log.exception('Critical error on downloading journal')

    if do_process and journal:
        process(journal.journal_id, location)


@run.command()
@click.argument('journal_id')
@click.option('--input-location', default=None, help="Custom download location of journal")
@click.option('--output-location', default=None, help="Custom output for processed journals")
def process(journal_id, input_location=None, output_location=None):
    log.info('Processing journal id {0}'.format(journal_id))

    input_path = input_location if input_location else base_path
    output_path = output_location if output_location else base_path

    try:
        journal_processor = LoadDiskJournal(input_path, output_path, journal_id, exported=False)
        journal = journal_processor.load_journal_from_disk()
        log.info('Completed processing task! Processed journal available in {0}'.format(journal_processor.get_process_location()))

    except Exception:
        log.exception('Critical error on processing journal')



@run.command()
@click.argument('journal_id')
@click.option('--location', help="Custom location of exported journal")
@click.option('--output-location', default=None, help="Custom output for processed journals")
def process_exported(journal_id, location, output_location):
    log.info('Processing previously exported journal {0}'.format(journal_id))

    input_path = location if location else base_path
    output_path = output_location if output_location else base_path

    try:
        journal_processor = LoadDiskJournal(input_path, output_path, journal_id, exported=True)
        journal = journal_processor.load_journal_from_disk()
        log.info('Completed processing task! Processed journal available in {0}'.format(journal_processor.get_process_location()))

    except Exception:
        log.exception('Critical error on processing journal')


@run.command()
@click.argument('journal_id')
@click.option('--input-location', default=None, help="Custom download location of journal")
@click.option('--output-location', default=None, help="Custom output for processed journals")
@click.option('--html', is_flag=True, default=False, help="Export as HTML")
@click.option('--json', is_flag=True, default=False, help="Export as JSON")
@click.option('--pdf', is_flag=True, default=False, help="Export as PDF")
@click.option('--reduced', is_flag=True, default=False, help="Create a PDF with reduced image and text size")
@click.option('--epub', is_flag=True, default=False, help="Export as EPUB")
def publish(journal_id, input_location, output_location, html, json, pdf, reduced, epub):
    input_path = input_location if input_location else base_path
    output_path = output_location if output_location else base_path

    if not html and not json and not pdf and not epub: html = True

    formats = []
    if html: formats.append('html')
    if json: formats.append('json')
    if pdf: formats.append('pdf')

    log.info('Outputting journal id {0} to formats: {1}'.format(journal_id, ', '.join(formats)))

    try:
        journal_publisher = PublishJournal(input_path, output_path, journal_id)

        if html:
            journal_publisher.publish_journal_id(PublicationFormats.TEMPLATED_HTML)
            log.info('Completed publishing to HTML! Published journal available in {0}'.format(journal_publisher.get_publication_location()))
        if json:
            journal_publisher.publish_journal_id(PublicationFormats.JSON_MODEL)
            log.info('Completed publishing to JSON! Published journal available in {0}'.format(journal_publisher.get_publication_location()))
        if pdf:
            journal_publisher.publish_journal_id(PublicationFormats.PDF, reduced=reduced)
            log.info('Completed publishing to PDF! Published journal available in {0}'.format(journal_publisher.get_publication_location()))

    except Exception:
        log.exception('Critical error on publishing journal')

@run.command()
def version():
    print('BikeSanity script v1.1.6')


if __name__ == '__main__':
    run()
