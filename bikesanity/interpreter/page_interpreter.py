from itertools import takewhile
from bs4 import BeautifulSoup, NavigableString

import bikesanity.io_utils.log_handler as log_handler
from bikesanity.entities.content_blocks import TextBlock, Heading, Image, Map
from bikesanity.entities.page import Page
from bikesanity.services.retrievers import BaseRetriever

from bikesanity.services.map_extractor import MapExtractor, LineExtractor
from .interpreter_base import InterpreterBase


class PageInterpreter(InterpreterBase):
    def __init__(self, retriever: BaseRetriever, progress_callback=None):
        self.retriever = retriever
        self.progress_callback = progress_callback

    def update_progress(self):
        if self.progress_callback: self.progress_callback()


    def get_title(self, title):
        title_elem = title.find(name='h1')
        return title_elem.text.strip() if title_elem else ''

    def get_distance_statement(self, title):
        distance_elem = title.find(name='h3')
        if not distance_elem or distance_elem.parent.name != 'body': return ''
        distance_statement = distance_elem.text.strip()
        return distance_statement

    def get_main_content(self, title):
        content_elem = title.find(name='div')
        return content_elem

    def is_picture_or_map(self, div_elem):
        table_elem = div_elem.find('table')
        return table_elem and 'id' in table_elem.attrs and 'pic' in table_elem.attrs['id']

    def is_map(self, div_elem):
        return any(div_elem.findAll("div", {"id" : lambda l: l and l.startswith('div_map')}))

    def remove_children(self, children):
        for child in children:
            if isinstance(child, NavigableString):
                child.extract()
            else:
                child.decompose()

    def get_text_before_next_element(self, content):
        for dodgy_center in content.find_all(name="center", recursive=False):
            dodgy_center.unwrap()

        div_elem = content.find(name='div')

        if div_elem == next(content.children, None):
            return None, div_elem

        text_content = []
        to_remove = []
        for child in takewhile(lambda x: x != div_elem, content.children):
            # Convert any <br> into newlines
            if hasattr(child, 'find_all'):
                for br in child.find_all('br'):
                    br.replace_with('\n' + br.text)

            if hasattr(child, 'get_text'):
                text_content.append( child.get_text().strip())
                to_remove.append(child)
            else:
                text_content.append(str(child).strip())
                to_remove.append(child)

        self.remove_children(to_remove)
        return text_content, div_elem


    def process_pic(self, div_elem):
        pic_elem = div_elem.find(name='center')
        if not pic_elem: return None

        # Get image
        img_elem = pic_elem.find(name='img')
        if not img_elem: return None

        img_path = img_elem.attrs['src']
        img_path_fullsize = img_path.replace('/small/', '/large/')

        # Download the pics
        pic_small = self.retriever.retrieve_image_small(img_path)
        pic_fullsize = self.retriever.retrieve_image_large(img_path_fullsize)

        # Get caption
        caption_elem = pic_elem.find(name='b')
        caption = caption_elem.text if caption_elem else ''

        return Image(img_path, img_path_fullsize, caption, pic_small, pic_fullsize)

    def _get_map_id_from_path(self, map_path):
        for token in map_path.split('?'):
            if token.startswith('line_id='):
                return token[8:]


    def process_map(self, div_elem):
        map_elem = div_elem.find(name='center')
        if not map_elem: return None

        # Retrieve the map resource path
        gpx_download_elem = div_elem.find('a', {'title' : lambda l: l and l.startswith('Download GPX')})
        if gpx_download_elem:
            gpx_path = gpx_download_elem.attrs['href']
            gpx_url = self.retriever.base_url + gpx_path
            # Get the map ID from the path
            map_id = self._get_map_id_from_path(gpx_path)
        else:
            gpx_url = None
            map_id = None

        # Get caption
        caption_elem = map_elem.find(name='b')
        caption = caption_elem.text if caption_elem else ''

        # Now parse out the data directly from the HTML representation of the map
        gpx_data, json_data = None, None
        try:
            map_extractor = MapExtractor(map_elem)
            map_data = next(map_extractor.iterate_map_data(), None)
            if map_data:
                line_extractor = LineExtractor(map_data)
                gpx_data, json_data = line_extractor.generate_map_binary_data()
        except Exception as exc:
            log_handler.log.exception('Error extracting map', exc)

        log_handler.log.info('Successfully extracted map {0}'.format(map_id))
        return Map(map_id, caption, gpx_data=gpx_data, json_data=json_data, url=gpx_url)


    def process_next_bloc(self, main_content, page: Page):
        text_content, elem = self.get_text_before_next_element(main_content)
        if text_content: page.add_content(TextBlock(text_content))

        if not elem: return False

        if self.is_picture_or_map(elem):
            if self.is_map(elem):
                map_block = self.process_map(elem)
                if map_block: page.add_content(map_block)
            else:
                image_block = self.process_pic(elem)
                if image_block: page.add_content(image_block)

        self.remove_everything_before(elem, including=True)
        self.update_progress()
        return True


    def process_title(self, title, page: Page, include_metadata=True, include_title=False):

        if include_metadata:
            page.title = self.get_title(title)
            page.parse_distance_statement(self.get_distance_statement(title))

        if include_title:
            title_text = self.get_title(title)
            if title_text: page.add_content(Heading(title_text))

        main_content = self.get_main_content(title)
        while(main_content):
            if not self.process_next_bloc(main_content, page): break

    def process_titles(self, doc, page: Page, include_metadata=True):
        titles = doc.find_all(name="big")
        for title in titles:
            parent = title.parent
            if parent and parent.name == 'body':
                self.remove_everything_before(title)
                self.process_title(parent, page, include_metadata=include_metadata)

    def process_titles_single_page(self, doc, page: Page):
        titles = doc.find_all(name="hr")
        for title in titles:
            parent = title.parent
            if parent and parent.name == 'td':
                body = self.remove_everything_before_body_level(title, including=True)
                self.process_title(body, page, include_metadata=False, include_title=True)

    def parse_page(self, page: Page, single=False):
        log_handler.log.info('Processing page {0} for journal {1}'.format(page.original_id, page.journal_id))

        doc = BeautifulSoup(page.original_html, features="lxml")
        titles_processor = self.process_titles_single_page if single else self.process_titles
        titles_processor(doc, page)

        # If additional pages exist, process these as well
        for additional_html in page.additional_html_pages:
            log_handler.log.info('Processing additional page for journal {0}'.format(page.journal_id))
            doc = BeautifulSoup(additional_html, features="lxml")
            self.process_titles(doc, page, include_metadata=False)

        return page

    def get_additional_part_id(self, url):
        for term in url.split('&'):
            if term.startswith('part='):
                return term[5:]

    def find_additional_pages(self, page_html):
        doc = BeautifulSoup(page_html, features="lxml")

        titles = doc.find_all(name='big')
        for title in titles:
            page_link_elem = title.find(name='a')
            if page_link_elem and '>>>' in title.get_text():
                url = self.retriever.base_url + page_link_elem.attrs['href']
                yield url, self.get_additional_part_id(url)


    def retrieve_page(self, journal_id, original_id, url):
        log_handler.log.info('Retrieving page {0} for journal {1}'.format(original_id, journal_id), extra={'journal_id': journal_id})
        self.update_progress()

        # Download the page HTML
        page_html = self.retriever.retrieve_page(url, original_id, error_message="Error code in retrieving journal page html: {0}")
        self.update_progress()

        page = Page(journal_id, original_id, page_html)

        # Download any additional other pages
        for url, part_id in self.find_additional_pages(page_html):
            log_handler.log.info('Additional page for {0} detected: {1}'.format(original_id, url), extra={'journal_id': journal_id})
            self.update_progress()

            # Lack of a parsed part number means this has already been postprocessed (and then just use the whole path)
            additional_filename = '{0}_{1}'.format(original_id, part_id) if part_id else url.replace('.html', '')

            additional_html = self.retriever.retrieve_page(url, additional_filename, error_message="Error code in retrieving additional page html: {0}")
            page.add_additional_html(additional_html)
            self.update_progress()

        return page
