import re

from bs4 import BeautifulSoup

from bikesanity.entities.content_blocks import Image, Map, TextBlock
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page
from bikesanity.io_utils.resources import get_resource_string


class TemplatedHtmlOutput:

    TEMPLATES_DIRECTORY = 'templates'

    def __init__(self, local_handler, progress_callback=None):
        self.local_handler = local_handler
        self.progress_callback = progress_callback

    def progress_update(self, percent):
        if self.progress_callback:
            self.progress_callback(progress=percent)

    def open_index_template(self):
        template_html = get_resource_string([self.TEMPLATES_DIRECTORY, 'index.html'])
        return BeautifulSoup(template_html, 'html5lib')

    def open_page_template(self):
        template_html = get_resource_string([self.TEMPLATES_DIRECTORY, 'page.html'])
        return BeautifulSoup(template_html, 'html5lib')


    def set_title(self, soup, title):
        soup.title.string.replace_with(title)

    def generate_logo(self, soup, author, journal_title):
        logo = soup.find(id='logo')
        if author:
            logo.append(soup.new_string(author))
        logo_span = soup.new_tag('span')
        if journal_title:
            logo_span.append(soup.new_string(' - {0}'.format(journal_title)))
        logo.append(logo_span)


    def output_journal(self, journal: Journal):
        soup = self.open_index_template()

        self.set_title(soup, journal.journal_title)

        self.generate_logo(soup, journal.journal_author, journal.journal_title)

        index_header = soup.find(id='index_header')

        # Add title and distance statement
        self.output_title(soup, index_header, journal.journal_title)

        self.output_subtitle(soup, index_header, journal.journal_subtitle)
        subtitle = self.output_subtitle(soup, index_header, 'By ')
        strong_tag = soup.new_tag('strong')
        if journal.journal_author:
            strong_tag.append(soup.new_string(journal.journal_author))
        subtitle.append(strong_tag)

        locations = [location for location in journal.locales]
        self.output_p(soup, index_header, 'Locations: {0}'.format(', '.join(locations)))

        index_body = soup.find(id='index_page')

        if journal.cover_image:
            self.output_picture(soup, index_body, journal.cover_image, fullsize_only=True, prepend=True)

        # Update progress
        self.progress_update(percent=10)

        toc_div = soup.find(id='toc_container')

        # Iterate over the ToC and process every page
        page_idx = 1
        ul_tag = None

        toc_pages = [toc for toc in journal.toc if toc.page]
        last_toc = toc_pages[-1]

        for toc_item in journal.toc:

            if toc_item.page:
                if not ul_tag:
                    ul_tag = soup.new_tag('ul')

                li_tag = soup.new_tag('li')

                html_filename = self.output_page(journal, toc_item.page, page_idx, last=toc_item == last_toc)
                a_tag = soup.new_tag('a', attrs={
                    'href': html_filename
                })
                a_tag.append(soup.new_string(toc_item.page.title))
                li_tag.append(a_tag)
                ul_tag.append(li_tag)

                page_idx += 1
            elif toc_item.title:
                if ul_tag:
                    toc_div.append(ul_tag)
                    ul_tag = None

                self.output_subtitle(soup, toc_div, toc_item.title)

            # Calculate and update progress
            self.progress_update(((page_idx / len(toc_pages)) * 80) + 10)

        if ul_tag:
            toc_div.append(ul_tag)

        # Save the generated HTML
        self.local_handler.save_generated_html(soup, 'index')

        # Copy the resources to the output as well
        self.local_handler.copy_resource_stream(['templates', 'css', 'journal.css'], ['css', 'journal.css'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'responsive.css'], ['css', 'responsive.css'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'fontawesome-all.min.css'], ['css', 'fontawesome-all.min.css'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'images', 'dark-tl.svg'], ['css', 'images', 'dark-tl.svg'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'images', 'dark-tr.svg'], ['css', 'images', 'dark-tr.svg'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'images', 'dark-br.svg'], ['css', 'images', 'dark-br.svg'])
        self.local_handler.copy_resource_stream(['templates', 'css', 'images', 'dark-bl.svg'], ['css', 'images', 'dark-bl.svg'])

        # Update progress
        self.progress_update(percent=100)


    def add_nav_link(self, soup, nav_ul, idx, text):
        a_tag = soup.new_tag('a', attrs= {
         'href': '{0}.html'.format(idx)
        })
        a_tag.append(soup.new_string(text))
        li_tag = soup.new_tag('li')
        li_tag.append(a_tag)
        nav_ul.append(li_tag)


    def output_page(self, journal: Journal, page: Page, page_idx: int, last=False):
        soup = self.open_page_template()
        self.set_title(soup, page.title)

        self.generate_logo(soup, journal.journal_author, journal.journal_title)

        header = soup.find(id='header')
        nav_ul = header.find('ul')
        if page_idx > 1:
            self.add_nav_link(soup, nav_ul, page_idx-1, 'Previous')
        if not last:
            self.add_nav_link(soup, nav_ul, page_idx+1, 'Next')

        page_header = soup.find(id='page_header')

        title_words = page.title.split(' ')
        title_strong = ' '.join(title_words[:2] if len(title_words) > 2 else title_words)
        title_weak = ' '.join(title_words[2:] if len(title_words) > 2 else [])
        header_title = self.output_title(soup, page_header, title_weak)
        if title_strong:
            strong = soup.new_tag('strong')
            strong.append(soup.new_string(title_strong + ' '))
            header_title.insert(0, strong)

        page_div = soup.find(id='journal_page')

        # Add title and distance statement
        if page.date_statement:
            h4_tag = soup.new_tag('h4')
            h4_tag.append(soup.new_string('Date: {0}'.format(page.date_statement)))
            page_div.append(h4_tag)
        if page.page_distance:
            h4_tag = soup.new_tag('h4')
            h4_tag.append(soup.new_string('Distance: {0}'.format(page.page_distance)))
            page_div.append(h4_tag)
        if page.total_distance:
            h4_tag = soup.new_tag('h4')
            h4_tag.append(soup.new_string('Total distance: {0}'.format(page.total_distance)))
            page_div.append(h4_tag)

        for content in page.contents:
            if isinstance(content, TextBlock):
                for para in content.content_text:
                    self.output_para(soup, page_div, para)
            elif isinstance(content, Image):
                self.output_picture(soup, page_div, content)
            elif isinstance(content, Map):
                self.output_map(soup, page_div, content)

        page_filename = self.local_handler.save_generated_html(soup, page_idx)
        return page_filename

    def output_para(self, soup, page_div, para):
        # Split every paragraph by explicit newlines
        for p in para.split('\n'):
            # Don't write out the previous page section dividers, as they're no longer needed
            if p.startswith('>>>') or p.startswith('<<<'):
                continue

            p_tag = soup.new_tag('p')

            # Links will be separated in their own paragraphs. Convert them into proper links
            if p.startswith('http://') or p.startswith('https://') and ' ' not in p:
                a_tag = soup.new_tag('a', attrs= {
                    'href': p
                })
                a_tag.append(soup.new_string(p))
                p_tag.append(a_tag)
            else:
                p_tag.append(soup.new_string(p))
            page_div.append(p_tag)


    MAP_SCRIPT = """
        <!--
        var mapGpx = '{1}';

        var map = L.map('{0}');

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
        }}).addTo(map);

        new L.GPX(mapGpx, {{
          async: true,
          marker_options: {{
            startIconUrl: null,
            endIconUrl: null,
            shadowUrl: null
          }}
        }})
          .on('loaded', function(e) {{
            map.fitBounds(e.target.getBounds());
          }}).addTo(map);
    """

    def sanitize_gpx(self, gpx):
        gpx = gpx.replace('\n', '')
        return re.sub(r'\s{2,}', ' ', gpx)

    def output_map(self, soup, page_div, map: Map):
        map_container_div_tag = soup.new_tag('div', attrs={
            'class': 'map_container'
        })

        gpx_url = self.get_map_url(map)
        gpx_span_tag = soup.new_tag('span', attrs={
            'class': 'map_link'
        })
        gpx_a_tag = soup.new_tag('a', attrs= {
            'href': gpx_url
        })
        gpx_a_tag.append(soup.new_string("Map GPX"))
        gpx_span_tag.append(gpx_a_tag)
        map_container_div_tag.append(gpx_span_tag)

        map_id = 'map_{0}'.format(map.map_id)
        map_div = soup.new_tag('div', attrs={
            'id': map_id,
            'class': 'map'
        })
        map_container_div_tag.append(map_div)

        if map.caption:
            caption_tag = soup.new_tag('p')
            caption_tag.append(soup.new_string(map.caption))
            map_container_div_tag.append(caption_tag)

        # Add the JavaScript for the map
        map_gpx = self.local_handler.load_map_gpx(map)
        map_gpx = self.sanitize_gpx(map_gpx)

        script_tag = soup.new_tag('script', attrs={
            'language': 'JavaScript',
            'type': 'text/javascript'
        })
        script = self.MAP_SCRIPT.format(map_id, map_gpx)
        script_tag.append(soup.new_string(script))
        map_container_div_tag.append(script_tag)

        page_div.append(map_container_div_tag)


    def output_picture(self, soup, body, image: Image, fullsize_only=False, prepend=False):
        url_small, url_fullsize = self.output_pic(image)

        div_tag = soup.new_tag('div', attrs={
            'class': 'pic_container'
        })
        wrapper = soup.new_tag('div', attrs={
            'class': 'image-wrapper'
        })
        a_tag = soup.new_tag('a', attrs={
            'href': url_fullsize
        })
        img_tag = soup.new_tag('img', attrs={
            'src': url_fullsize if fullsize_only else url_small
        })
        a_tag.append(img_tag)
        wrapper.append(a_tag)

        div_tag.append(wrapper)

        if image.caption:
            caption_tag = soup.new_tag('p')
            caption_tag.append(soup.new_string(image.caption))
            div_tag.append(caption_tag)

        if prepend:
            body.insert(0, div_tag)
        else:
            body.append(div_tag)

    def output_pic(self, image: Image):
        return '../resources/{0}.{1}.{2}'.format(image.image_id, 'small', image.extension), \
               '../resources/{0}.{1}'.format(image.image_id, image.extension)


    def get_map_url(self, map: Map):
        return '../resources/{0}.{1}'.format(map.map_id, 'gpx')

    def output_title(self, soup, body, text):
        h2_tag = soup.new_tag('h2')
        h2_tag.append(soup.new_string(text))
        body.append(h2_tag)
        return h2_tag

    def output_subtitle(self, soup, body, text):
        h4_tag = soup.new_tag('h4')
        h4_tag.append(soup.new_string(text))
        body.append(h4_tag)
        return h4_tag

    def output_p(self, soup, body, text):
        p_tag = soup.new_tag('p')
        p_tag.append(soup.new_string(text))
        body.append(p_tag)
