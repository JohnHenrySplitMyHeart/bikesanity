import os
import shutil
from fpdf import FPDF
from bikesanity.io_utils.resources import create_temp_from_resource


class BasePdfTemplate(FPDF):

    DEJAVU_FONT = 'DejaVu'

    A4_WIDTH = 210
    A4_HEIGHT = 297

    MARGIN = 20
    TOP_MARGIN = 10
    PAGE_WIDTH = A4_WIDTH - (MARGIN*2)

    IMAGE_DPI = 200
    MM_PER_INCH = 25.4
    CAPTION_WIDTH = 150

    def __init__(self, title, author, part=None):
        self.draw_header = False
        self.journal_title = title
        self.author = author
        self.part = part

        super().__init__(orientation='P', unit='mm', format='A4')

        self.tmp_files = []
        self.load_font_resource('DejaVuSans.ttf', '')
        self.load_font_resource('DejaVuSans-Bold.ttf', 'B')
        self.load_font_resource('DejaVuSans-Oblique.ttf', 'I')
        self.page_title = title
        self.setup_pages()
        self.image_pair = False
        self.page_added = True
        self.image_path = None

    def load_font_resource(self, font_name, weight):
        # Get a temporary file from the named resource
        temp_font_file = create_temp_from_resource(['fonts', font_name])
        # Add the font from this temporary file (only method FPDF supports)
        self.add_font(self.DEJAVU_FONT, weight, temp_font_file, uni=True)
        # Remove the temp file once its loaded
        self.tmp_files.append(temp_font_file)

    def setup_pages(self):
        self.set_font(self.DEJAVU_FONT, '', 14)
        self.set_margins(self.MARGIN, self.TOP_MARGIN, self.MARGIN)
        self.add_page()

    def update_page_title(self, name):
        self.draw_header = False
        self.page_title = name

    def limit_title(self, title, max_width=PAGE_WIDTH):
        terms = title.split(' ')

        terms_to_use = []
        for i in range(0, len(terms)):
            terms_to_use.append(terms[i])
            title = ' '.join(terms_to_use)
            if self.get_string_width(title) > max_width: break

        return title

    def header(self):
        if not self.draw_header:
            self.draw_header = True
            return

        self.set_font(self.DEJAVU_FONT, 'B', 12)

        # Limit title if too long
        title = self.limit_title(self.page_title)

        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)

        # Title
        self.cell(w, 9, title, 0, 1, 'C', 0)
        # Line break
        self.ln(10)
        self.page_top = self.get_y()

    def footer(self):
        # No footer on first few pages
        if self.page_no() < 3: return
        # Don't draw footer if content overlaps
        if self.get_y() > self.A4_HEIGHT - self.TOP_MARGIN: return

        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font(self.DEJAVU_FONT, 'I', 8)
        # Text color in gray
        self.set_text_color(128)

        footer_text = '{0} by {1}{2} - Page {3}'.format(self.journal_title, self.author, ' (part {0})'.format(self.part) if self.part else '', self.page_no()-2)

        # Page number
        self.cell(0, 10, footer_text, 0, 0, 'C')

    def cover_title(self, title, subtitle, author, distance_statement, part=None):
        self.set_font(self.DEJAVU_FONT, 'B', 20)

        self.ln(15)
        # Title
        self.multi_cell(0, 20, title, 0, 'C', 0)
        self.ln(1)
        if part:
            self.set_font(self.DEJAVU_FONT, '', 20)
            self.cell(0, 5, 'Part {0}'.format(part), 0, 0, 'C')
            self.ln(6)

        # Line break
        self.ln(6)
        self.set_font(self.DEJAVU_FONT, '', 16)
        self.multi_cell(0, 10, subtitle, 0, 'C', 0)
        self.ln(4)
        self.set_font(self.DEJAVU_FONT, 'I', 10)
        self.multi_cell(0, 5, distance_statement, 0, 'C', 0)
        self.ln(5)
        self.set_font(self.DEJAVU_FONT, '', 16)
        self.multi_cell(0, 20, author, 0, 'C', 0)
        self.ln(8)

    def add_toc(self, toc_items):
        self.set_font(self.DEJAVU_FONT, 'B', 18)
        self.cell(0, 5, 'Table of Contents', 0, 0, 'C', 0)

        self.ln(15)
        self.set_font(self.DEJAVU_FONT, 'I', 9)

        for toc_item in toc_items:
            if toc_item.is_header:
                self.set_font(self.DEJAVU_FONT, 'B', 9)
            else:
                self.set_font(self.DEJAVU_FONT, 'I', 9)


            # Limit the title if it's too long
            title = self.limit_title(toc_item.title, 125)

            str_size = self.get_string_width(title)
            self.cell(str_size+2, 9, title)

            # Filling dots
            page_cell_size=self.get_string_width(toc_item.page_no) + 2

            dot_length = self.PAGE_WIDTH - str_size - page_cell_size - 10

            nb = int(dot_length // self.get_string_width('.'))
            dots = '.' * nb
            self.cell(dot_length, 9, dots, 0, 0, 'R')

            # Page number
            self.cell(page_cell_size, 9, toc_item.page_no, 0, 1,'R')

    def section_title(self, title):
        self.set_font(self.DEJAVU_FONT, 'B', 18)
        self.multi_cell(0, 10, title, 0, 'C', 0)
        self.ln(20)

    def chapter_title(self, label, date, distance, total_distance):
        self.set_font(self.DEJAVU_FONT, 'B', 14)

        # Colors of frame, background and text
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(230, 230, 0)
        # Thickness of frame (1 mm)
        self.set_line_width(0.5)

        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.multi_cell(0, 10, label, 1, 'C', 1)
        # Line break
        self.ln(4)

        if not distance: return

        if total_distance and date:
            distance_statement = '{0} - of total {1} - on {2}'.format(distance, total_distance, date)
        elif total_distance:
            distance_statement = '{0} - of total {1}'.format(distance, total_distance)
        else:
            distance_statement = distance

        self.set_font(self.DEJAVU_FONT, 'I', 10)
        self.cell(0, 5, distance_statement, 0, 0, 'L', 0)
        self.ln(20)

    def add_image_format_tolerant(self, image_path, x=None, y=None, width=None, height=None):
        for ext in [ None, '.jpeg', '.png']:
            if self.try_add_image(image_path, x, y, width, height, ext):
                break

    def try_add_image(self, image_path, x, y, width, height, ext=None):
        updated_ext = image_path[:image_path.rfind('.')] + ext if ext else image_path
        if ext and image_path != updated_ext:
            shutil.copyfile(image_path, updated_ext)
        try:
            self.image(updated_ext, x=x, y=y, w=width if width else 0, h=height if height else 0)
            return True
        except Exception as exc:
            return False


    def clipping_rect(self, x, y, w, h, outline=False):
        op= 'S' if outline else 'n'
        self._out('q {0} {1} {2} {3} re W {4}'.format(
            x * self.k,
            (self.h - y) * self.k,
            w * self.k,
            -h * self.k,
            op
        ))

    def unset_clipping(self):
        self._out('Q')

    def cleanup_tmp_files(self):
        for tmp_file in self.tmp_files:
            try:
                os.remove(tmp_file)
                os.remove(tmp_file + '.pkl')
                os.remove(tmp_file + '.cw127.pkl')
            except:
                pass
