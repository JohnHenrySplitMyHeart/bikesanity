import re

from bikesanity.entities.content_blocks import Image
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page


class HtmlPostProcessor:

    def __init__(self):
        pass

    def postprocess_journal(self, journal: Journal):
        if not journal.original_html: return

        html = journal.original_html.decode()

        # Cover image
        if journal.cover_image:
            html = self.replace_image(html, journal.cover_image)

        # Table of contents links
        for toc in journal.toc:
            if toc.original_id:
                html = self.replace_toc_link(html, toc)

        journal.postprocessed_html = html.encode()

    def postprocess_page(self, page: Page):
        # Postprocess the page itself
        page_html = page.original_html.decode()
        page.postprocessed_html = self.postprocess_page_html(page, page_html)

        # Postprocess additional page HTML, if any
        page.additional_postprocessed_html = []
        for additional_page in page.additional_html_pages:
            additional_html = additional_page.decode()
            page.additional_postprocessed_html.append(self.postprocess_page_html(page, additional_html))


    def postprocess_page_html(self, page: Page, page_html):
        # Fix JS and CSS links
        page_html = self.fix_js_css_links(page_html)

        # Fix multipage links
        page_html = self.replace_multipage_part_links(page_html, page)

        # Switch maps to use the OSM basemap so they work locally
        page_html = self.switch_maps_to_osm(page_html)

        # Post process images and links
        for content in page.contents:
            if isinstance(content, Image):
                page_html = self.replace_image(page_html, content)

        return page_html.encode()


    def replace_toc_link(self, html, toc) -> str:
        pattern = '<a href=\\"/doc/page/.*?ID=\\"{0}\\">'.format(toc.original_id)
        replacement = '<a href="{0}.html" ID="{1}">'.format(toc.original_id, toc.original_id)
        return re.sub(pattern, replacement, html)

    def replace_image(self, html, image: Image):
        image_path = re.escape(image.original_path_small)
        pattern = '<a href=\\".*\\">\\s*<img src=\\"/{0}.*?\\"'.format(image_path)
        replacement = '<a href="{0}"><img src="{1}"'.format(image.original_path_fullsize, image.original_path_small)
        return re.sub(pattern, replacement, html)

    def switch_maps_to_osm(self, page_html):
        return re.sub('\"basemap\":\"stadia\"', '"basemap":"osm"', page_html)

    def fix_js_css_links(self, page_html):
        page_html = re.sub('<script src=\\"/javascript', '<script src="javascript', page_html)
        page_html = re.sub("<script src='/javascript", "<script src='javascript", page_html) # Yes, really. NG is an idiot.
        page_html = re.sub('<script type=\\"text/javascript\\" src=\\"/javascript', '<script type="text/javascript" src="javascript', page_html)
        page_html = re.sub('<link rel=\\"stylesheet\\" href=\\"/css/', '<link rel="stylesheet" href="css/', page_html)
        page_html = re.sub("<link href='/css", "<link href='css", page_html)
        return page_html

    def replace_multipage_part_links(self, page_html, page: Page):
        page_html = re.sub(r'(>>> <A HREF=\")(.*?)(\d+)(\">)', r'\g<1>{0}_\g<3>.html\g<4>'.format(page.original_id), page_html)
        page_html = re.sub(r'(<<< <A HREF=\")(.*?)(\">)', r'\g<1>{0}.html\g<3>'.format(page.original_id), page_html)
        page_html = re.sub(r'(<<< <A HREF=\")(.*?)(\d+)(\">)', r'\g<1>{0}_\g<3>.html\g<4>'.format(page.original_id), page_html)
        return page_html
