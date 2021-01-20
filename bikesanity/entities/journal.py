from .content_blocks import Image
from .page import Page


class TocEntry:
    def __init__(self, original_id, title, url):
        self.original_id = original_id
        self.title = title
        self.url = url
        self.page = None

    def set_page(self, page):
        self.page = page


class Journal:

    def __init__(self, journal_id, original_html):
        self.journal_id = journal_id

        self.original_html = original_html
        self.postprocessed_html = None

        self.journal_title = None
        self.journal_subtitle = None
        self.journal_author = None
        self.distance_statement = None
        self.locales = []

        self.cover_image = None

        self.toc = []
        self.single_page = False

        self.js = {}
        self.css = {}

    def add_toc_entry(self, original_id, title, url):
        toc_entry = TocEntry(original_id, title, url)
        self.toc.append(toc_entry)

    def add_single_page(self, page: Page):
        toc_entry = TocEntry(self.journal_id, self.journal_title, None)
        toc_entry.set_page(page)
        self.toc.append(toc_entry)

    def add_cover_image(self, image: Image):
        self.cover_image = image

    def save_original_source(self, local_handler):
        # Save the HTML itself
        local_handler.save_html_original('index.html', self.postprocessed_html if self.postprocessed_html else self.original_html)

        # Save the cover image if one exists
        if self.cover_image: local_handler.save_image_original(self.cover_image)

        # Save the JS and CSS
        for js, content in self.js.items():
            local_handler.save_js_resource(js, content)
        for css, content in self.css.items():
            local_handler.save_css_resource(css, content)

    def save_resources(self, local_handler):
        # Save the cover image if one exists
        if self.cover_image: local_handler.save_image_resource(self.cover_image)

    def clear_resources(self):
        if self.cover_image: self.cover_image.clear_resources()

        for js in self.js.values():
            if js:
                js.close()
        for css in self.css.values():
            if css:
                css.close()

    def update_data_model(self):
        if not hasattr(self, 'single_page'): self.single_page = False
