from fpdf import FPDF


class JournalPdfReduced(FPDF):

    A4_WIDTH = 210
    A4_HEIGHT = 297

    MARGIN = 20
    TOP_MARGIN = 10
    PAGE_WIDTH = A4_WIDTH - (MARGIN*2)

    PAGEBREAK_MARGIN = A4_HEIGHT - 140

    IMAGE_SCALE = 2.1
    IMAGE_WIDTH = (A4_WIDTH - (MARGIN*2))/IMAGE_SCALE
    IMAGE_X = (PAGE_WIDTH/2) - (IMAGE_WIDTH/2)
    CAPTION_WIDTH = 150

    LARGE_IMAGE_SCALE = 1.2
    LARGE_IMAGE_WIDTH = (A4_WIDTH - (MARGIN*2))/LARGE_IMAGE_SCALE
    LARGE_IMAGE_X = (PAGE_WIDTH/2) - (LARGE_IMAGE_WIDTH/2)

    RIGHT_IMAGE_X = PAGE_WIDTH - IMAGE_WIDTH + MARGIN

    IMAGE_DPI = 200
    MM_PER_INCH = 25.4

    def __init__(self, title, author, part=None):
        self.draw_header = False
        self.journal_title = title
        self.author = author
        self.part = part

        super().__init__(orientation='P', unit='mm', format='A4')

        self.add_font('DejaVu', '', '../fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', '../fonts/DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', '../fonts/DejaVuSans-Oblique.ttf', uni=True)
        self.page_title = title
        self.setup_pages()
        self.image_pair = False
        self.page_added = True
        self.image_path = None


    def update_page_title(self, name):
        self.draw_header = False
        self.page_title = name

    def setup_pages(self):
        self.set_font('DejaVu', '', 14)
        self.set_margins(self.MARGIN, self.TOP_MARGIN, self.MARGIN)
        self.add_page()

    def limit_title(self, title, max_width=PAGE_WIDTH):
        # Limit title if too long
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

        self.set_font('DejaVu', 'B', 12)

        # Limit title if too long
        title = self.limit_title(self.page_title)

        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        # self.set_draw_color(0, 80, 180)
        # self.set_fill_color(230, 230, 0)
        # self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        #self.set_line_width(0.5)
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
        # Arial italic 8
        self.set_font('DejaVu', 'I', 8)
        # Text color in gray
        self.set_text_color(128)

        footer_text = '{0} by {1}{2} - Page {3}'.format(self.journal_title, self.author, ' (part {0})'.format(self.part) if self.part else '', self.page_no()-2)

        # Page number
        self.cell(0, 10, footer_text, 0, 0, 'C')

    def cover_title(self, title, subtitle, author, distance_statement, part=None):
        self.set_font('DejaVu', 'B', 20)

        self.ln(15)
        # Title
        self.multi_cell(0, 20, title, 0, 'C', 0)
        self.ln(1)
        if part:
            self.set_font('DejaVu', '', 20)
            self.cell(0, 5, 'Part {0}'.format(part), 0, 0, 'C')
            self.ln(6)

        # Line break
        self.ln(6)
        self.set_font('DejaVu', '', 16)
        self.multi_cell(0, 10, subtitle, 0, 'C', 0)
        self.ln(4)
        self.set_font('DejaVu', 'I', 10)
        self.multi_cell(0, 5, distance_statement, 0, 'C', 0)
        self.ln(5)
        self.set_font('DejaVu', '', 16)
        self.multi_cell(0, 20, author, 0, 'C', 0)
        self.ln(8)

    def section_title(self, title):
        self.set_font('DejaVu', 'B', 18)
        self.multi_cell(0, 10, title, 0, 'C', 0)
        self.ln(20)
        self.image_pair = False

    def add_toc(self, toc_items):
        self.set_font('DejaVu', 'B', 18)
        self.cell(0, 5, 'Table of Contents', 0, 0, 'C', 0)

        self.ln(15)
        self.set_font('DejaVu', 'I', 9)

        for toc_item in toc_items:
            if toc_item.is_header:
                self.set_font('DejaVu', 'B', 9)
            else:
                self.set_font('DejaVu', 'I', 9)


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

    def chapter_title(self, label, date, distance, total_distance):
        self.set_font('DejaVu', 'B', 14)

        # Colors of frame, background and text
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(230, 230, 0)
        #self.set_text_color(220, 50, 50)
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

        self.set_font('DejaVu', 'I', 10)
        self.cell(0, 5, distance_statement, 0, 0, 'L', 0)
        self.ln(20)
        self.image_pair = False

    def text_content(self, text):
        # Flush any single images if needed
        self._add_single_image()

        self.set_font("DejaVu", size=8)
        self.multi_cell(w=0, h=6, txt=text, align='J')
        self.ln(5)
        self.image_pair = False

    def add_image(self, image_path, caption, height=None):
        # If this is the second image, add the pair
        if self.image_pair:
            self._add_image(self.image_path, self.image_caption, self.image_height)
            self._add_image(image_path, caption, height, right=True)
            self.image_path = None
            self.image_pair = False
            return

        self.image_path = image_path
        self.image_caption = caption
        self.image_height = height

        if not self.image_pair:
            self.image_pair = True
            self.pair_y = self.get_y()
        else:
            self.image_pair = False

    def add_image_large(self, image_path, caption):
        self._add_image(image_path, caption, large=True)

    def add_single_image(self):
        if self.image_path:
            self._add_image(self.image_path, self.image_caption, self.image_height, center=True)
            self.image_path = None

    def _add_image(self, image_path, caption, height=None, right=False, center=False, large=False):

        self.page_added = False
        if height:
            self.image(image_path, h=height)
        elif right:
            self.set_y(self.pair_y)
            self.image(image_path, x=self.RIGHT_IMAGE_X, w=self.IMAGE_WIDTH)
            self.pair_y = None
        elif center:
            self.cell(w=self.IMAGE_X, align='L')
            self.image(image_path, w=self.IMAGE_WIDTH)
        elif large:
            self.cell(w=self.LARGE_IMAGE_X, align='L')
            self.image(image_path, w=self.LARGE_IMAGE_WIDTH)
        else:
            # Left
            self.image(image_path, w=self.IMAGE_WIDTH)

        if self.page_added:
            self.pair_y = self.page_top
            right = False

        # Don't break between caption
        self.set_auto_page_break(False, margin=self.MARGIN)
        self.set_font("DejaVu", style='I', size=8)
        alignment = 'J' if self.get_string_width(caption) > self.IMAGE_WIDTH else 'C'

        if right:
            self.ln(3)
            self.set_x(self.RIGHT_IMAGE_X)
            self.multi_cell(w=self.IMAGE_WIDTH, h=5, txt=caption, align=alignment)
            self.ln(9)

            if self.get_y() < self.cap_y:
                self.set_y(self.cap_y)
            self.cap_y = None
        elif center:
            self.ln(3)
            self.set_x(self.IMAGE_X + self.MARGIN)
            self.multi_cell(w=self.IMAGE_WIDTH, h=5, txt=caption, align='C')
            self.ln(9)
        elif large:
            self.ln(3)
            self.multi_cell(w=self.PAGE_WIDTH, h=5, txt=caption, align='C')
            self.ln(9)
        else:
            self.ln(3)
            self.multi_cell(w=self.IMAGE_WIDTH, h=5, txt=caption, align=alignment)
            self.ln(9)
            self.cap_y = self.get_y()

        self.set_auto_page_break(True, margin=self.MARGIN)

    def add_page_if_near_bottom(self):
        if self.get_y() > self.PAGEBREAK_MARGIN:
            self.add_page()
        else:
            self.draw_header = True

    def add_page(self, orientation=''):
        self.page_added = True
        super().add_page(orientation)
        self.page_top = self.get_y()


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
