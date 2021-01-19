from bs4 import BeautifulSoup
from io_utils.local_journal import LocalJournalHandler

from bikesanity.entities.content_blocks import Image, Map, TextBlock
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page


class DiskHtmlOutput:

    OUTPUT_DIRECTORY = 'output/'

    def __init__(self, base_directory, journal_id):
        self.journal_id = journal_id
        self.base_directory = base_directory
        self.local_handler = LocalJournalHandler(base_directory, journal_id)

    def process_journal(self):
        # Remove existing files
        self.local_handler.remove_directory(self.OUTPUT_DIRECTORY)

        journal = self.local_handler.load_serialized_journal()

        if journal:
            self.output_journal(journal)

    def output_html(self, soup, filename):
        html = str(soup)
        filename = '{0}.html'.format(filename)
        path = self.local_handler.get_path(self.OUTPUT_DIRECTORY + filename)
        self.local_handler.output_text_to_file(path, html)
        return filename

    def output_journal(self, journal: Journal):
        soup = BeautifulSoup('', 'html5lib')

        body = soup.find('body')

        # Add title and distance statement
        self.output_title(soup, body, journal.journal_title)

        self.output_subtitle(soup, body, journal.journal_subtitle)
        self.output_subtitle(soup, body, 'By {0}'.format(journal.journal_author))

        locations = [location for location in journal.locales]
        self.output_para(soup, body, 'Locations: {0}'.format(', '.join(locations)))

        if journal.cover_image:
            self.output_picture(soup, body, journal.cover_image)

        toc_div = soup.new_tag('div', attrs={
            'class': 'toc_container'
        })

        # Iterate over the ToC and process every page
        page_idx = 1
        for toc_item in journal.toc:
            p_tag = soup.new_tag('p')
            toc_tag = p_tag

            if toc_item.page:
                html_filename = self.output_page(toc_item.page, page_idx)
                toc_tag = soup.new_tag('a', attrs={
                    'href': html_filename
                })
                p_tag.append(toc_tag)
                toc_tag.append(soup.new_string(toc_item.page.title))

                page_idx += 1
            elif toc_item.subtitle:
                toc_tag.append(soup.new_string(toc_item.subtitle))
            toc_div.append(p_tag)

        body.append(toc_div)
        self.output_html(soup, 'index')

    def output_page(self, page: Page, page_idx: int):
        soup = BeautifulSoup('', 'html5lib')

        body = soup.find('body')

        # Add title and distance statement
        h2_tag = soup.new_tag('h2')
        h2_tag.append(soup.new_string(page.title))
        body.append(h2_tag)

        h4_tag = soup.new_tag('h4')
        h4_tag.append(soup.new_string('Date: {0}'.format(page.date_statement)))
        body.append(h4_tag)
        h4_tag = soup.new_tag('h4')
        h4_tag.append(soup.new_string('Distance: {0}'.format(page.page_distance)))
        body.append(h4_tag)
        h4_tag = soup.new_tag('h4')
        h4_tag.append(soup.new_string('Total distance: {0}'.format(page.total_distance)))
        body.append(h4_tag)

        for content in page.contents:
            if isinstance(content, TextBlock):
                for para in content.content_text:
                    # Split every paragraph by explicit newlines
                    for p in para.split('\n'):
                        p_tag = soup.new_tag('p')
                        p_tag.append(soup.new_string(p))
                        body.append(p_tag)
            elif isinstance(content, Image):
                self.output_picture(soup, body, content)
            elif isinstance(content, Map):
                gpx_url = self.output_map(content)

                div_tag = soup.new_tag('div', attrs={
                    'class': 'map_container'
                })
                a_tag = soup.new_tag('a', attrs= {
                    'href': gpx_url
                })
                a_tag.append(soup.new_string("Map GPX"))
                div_tag.append(a_tag)

                if content.caption:
                    caption_tag = soup.new_tag('p')
                    caption_tag.append(soup.new_string(content.caption))
                    div_tag.append(caption_tag)

                body.append(div_tag)


        page_filename = self.output_html(soup, page_idx)
        return page_filename

    def output_picture(self, soup, body, image: Image):
        url_small, url_fullsize = self.output_pic(image)

        div_tag = soup.new_tag('div', attrs={
            'class': 'pic_container'
        })
        a_tag = soup.new_tag('a', attrs={
            'href': url_fullsize
        })
        img_tag = soup.new_tag('img', attrs={
            'src': url_small
        })
        a_tag.append(img_tag)
        div_tag.append(a_tag)

        if image.caption:
            caption_tag = soup.new_tag('p')
            caption_tag.append(soup.new_string(image.caption))
            div_tag.append(caption_tag)

        body.append(div_tag)

    def output_pic(self, image: Image):
        return '../resources/{0}.{1}.{2}'.format(image.image_id, 'small', image.extension), \
               '../resources/{0}.{1}'.format(image.image_id, image.extension)

    def output_map(self, map: Map):
        return '../resources/{0}.{1}'.format(map.map_id, 'gpx')

    def output_title(self, soup, body, text):
        h2_tag = soup.new_tag('h2')
        h2_tag.append(soup.new_string(text))
        body.append(h2_tag)

    def output_subtitle(self, soup, body, text):
        h4_tag = soup.new_tag('h4')
        h4_tag.append(soup.new_string(text))
        body.append(h4_tag)

    def output_para(self, soup, body, text):
        p_tag = soup.new_tag('p')
        p_tag.append(soup.new_string(text))
        body.append(p_tag)
