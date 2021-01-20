import logging
from .content_blocks import ContentBlock, Image, Map

log = logging.getLogger(__name__)


class Page:

    def __init__(self, journal_id, original_id, original_html):
        self.journal_id = journal_id
        self.original_id = original_id

        self.original_html = original_html
        self.postprocessed_html = None

        self.additional_html_pages = []
        self.additional_postprocessed_html = []

        self.title = None
        self.date_statement = None
        self.page_distance = None
        self.total_distance = None

        self.contents = []
        self.maps = []

    def add_additional_html(self, additional_html):
        self.additional_html_pages.append(additional_html)

    def add_content(self, content_block: ContentBlock):
        self.contents.append(content_block)

    def parse_distance_statement(self, distance_statement):
        if not distance_statement: return

        if 'Total so far: ' in distance_statement:
            self.total_distance = distance_statement[distance_statement.find('Total so far: ')+14:].strip()

            self.page_distance = distance_statement[:distance_statement.find(' - ')]
            self.page_distance = self.page_distance[self.page_distance.rfind(', ')+2:].strip()
            self.date_statement = distance_statement[:distance_statement.find(self.page_distance)][:-3].strip()
        else:
            self.date_statement = distance_statement

    def _persist_resources(self, persist_image, persist_map):
        self.maps = []

        # Iterate over content and upload
        for content in self.contents:
            if isinstance(content, Image):
                persist_image(content)
            elif isinstance(content, Map):
                persist_map(content)

    def save_resources(self, local_handler):
        self._persist_resources(local_handler.save_image_resource, local_handler.save_map_resource)

    def save_originals(self, local_handler):
        # Save the page HTML, including any additional sections
        local_handler.save_html_original(self.original_id + '.html', self.postprocessed_html if self.postprocessed_html else self.original_html)
        part = 2

        additional_html_pages = self.additional_postprocessed_html if self.additional_postprocessed_html else self.additional_html_pages
        for additional_html in additional_html_pages:
            filename = '{0}_{1}.html'.format(self.original_id, part)
            local_handler.save_html_original(filename, additional_html)
            part += 1

        # Save the associated image and map originals
        self._persist_resources(local_handler.save_image_original, local_handler.save_map_original)

    def clear_resources(self):
        for content in self.contents:
            content.clear_resources()
