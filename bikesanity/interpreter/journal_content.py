from itertools import takewhile
import unicodedata

from bs4 import BeautifulSoup, NavigableString

import bikesanity.io_utils.log_handler as log_handler
from bikesanity.services.retrievers import BaseRetriever
from bikesanity.entities.content_blocks import Image
from bikesanity.entities.journal import Journal
from .interpreter_base import InterpreterBase


class JournalContent(InterpreterBase):

    MAX_PAGE_DOWNLOAD_ATTEMPTS = 2


    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever

    def find_title(self, doc):
        title = doc.find(name="h1")
        self.remove_everything_before(title)
        return title

    def get_subtitle(self, doc):
        subtitle_elem = doc.find('h3')
        if subtitle_elem:
            self.remove_everything_before(subtitle_elem)
            return subtitle_elem.get_text()
        return None

    def get_distance_statement(self, doc):
        subtitle_elem = doc.find('h3')
        if subtitle_elem and isinstance(subtitle_elem.next_sibling, NavigableString):
            return subtitle_elem.next_sibling.replace('\n', '').replace('\t', '').strip()

    def get_locales(self, doc):
        locales_elem = doc.find('b', string="Locales:")
        locales = []
        if locales_elem:
            for sibling in locales_elem.find_next_siblings():
                if sibling.name != 'a': break
                locale_name = sibling.get_text()
                locale_name = unicodedata.normalize("NFKD", locale_name)
                locales.append(locale_name)
        return locales

    def get_cover_pic(self, doc):
        pic_containers = doc.findAll("table", {"bgcolor" : lambda l: l and l == 'gainsboro'})
        for pic_container in pic_containers:
            img_elem = pic_container.find('img', {'src': lambda l: l and 'pics/' in l})
            if img_elem:
                img_path = img_elem.attrs['src']
                cover_pic_data = self.retriever.retrieve_image_large(img_path)

                caption_elem = pic_container.find('b')
                caption = caption_elem.get_text() if caption_elem else ''

                return Image(img_path, img_path, caption, cover_pic_data, cover_pic_data)


    def get_contents_table(self, doc, journal: Journal):
        content_list_elem = doc.find('dl')

        # Handle empty documents with no ToC gracefully
        if not content_list_elem:
            log_handler.log.warn('Empty table of contents - continuing')
            return

        # Replace all the <dd> tags which are completely invalid, well done Neil!
        self.replace_invalid_tag(content_list_elem, 'dd')

        for child in takewhile(lambda x: x, content_list_elem.children):
            # Ignore basic strings
            if isinstance(child, NavigableString): continue

            # Find whether the ToC entry has a link, or if it's just a title
            toc_link = child if 'a' == child.name else child.find('a')

            # Any element that doesn't have an id attribute can be skipped
            if (not 'id' in child.attrs) and (not toc_link or not 'id' in toc_link.attrs): continue

            # Get the URL and ID
            toc_link_url = self.retriever.base_url + toc_link.attrs['href'] if toc_link else None
            toc_id = toc_link.attrs['id'] if toc_link else child.attrs['id']

            # Get the title text, and any other text following it
            toc_title = child.get_text()
            toc_title = toc_title + child.next_sibling if isinstance(child.next_sibling, NavigableString) else toc_title
            toc_title = toc_title.strip()

            journal.add_toc_entry(toc_id, toc_title, toc_link_url)

    def journal_from_html(self, journal_id, html) -> Journal:
        journal = Journal(journal_id, html)
        doc = BeautifulSoup(html, features="lxml")

        # Title
        title = self.find_title(doc)
        journal.journal_title = title.get_text()

        #  Subtitle
        journal.journal_subtitle = self.get_subtitle(doc)

        # Distance statement
        journal.distance_statement = self.get_distance_statement(doc)

        # Author user
        author_elem = doc.find('a', {"href" : lambda l: l and '&user' in l})
        journal.journal_author = author_elem.get_text() if author_elem else None

        # Fix for exported journals
        if not author_elem:
            title = doc.find('title')
            if title and 'by' in title.get_text():
                title_text = title.get_text()
                author = title_text[title_text.rfind('by')+3:]
                journal.journal_author = author


        # Locales
        journal.locales = self.get_locales(doc)

        # Cover pic
        journal.add_cover_image(self.get_cover_pic(doc))

        # Parse the ToC
        self.get_contents_table(doc, journal)

        return journal


    def _get_journal_id_from_url(self, url):
        tokens = url.split('&')
        for token in tokens:
            if token.startswith('doc_id='):
                return token[7:]

    def retrieve_journal(self, url, journal_id) -> Journal:
        # Resolve the full URL against the server and retrieve the journal index
        retrieved_html, resolved_url = self.retriever.retrieve_index(url, error_message="Error getting journal: {0}")

        # Determine the journal ID from the resolved URL
        if not journal_id: journal_id = self._get_journal_id_from_url(resolved_url)

        return self.journal_from_html(journal_id, retrieved_html)

    JS = [
        'leaflet.js',
        'Polyline.encoded.js',
        'plotly-latest.min.js',
        'Leaflet.fullscreen.min.js',
        'json2.js'
    ]
    CSS = [
        'leaflet.css',
        'leaflet.fullscreen.css'
    ]

    def retrieve_js_css_resources(self, journal) -> Journal:
        for js in self.JS:
            journal.js[js] = self.retriever.retrieve_js(js)
        for css in self.CSS:
            journal.css[css] = self.retriever.retrieve_css(css)
        return journal

