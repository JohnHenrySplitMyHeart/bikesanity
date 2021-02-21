from .base_pdf_template import BasePdfTemplate


class JournalPdfReduced(BasePdfTemplate):

    IMAGE_SCALE = 2.1
    LARGE_IMAGE_SCALE = 1.2


    def __init__(self, title, author, part=None):
        super().__init__(title, author, part)
        self.PAGEBREAK_MARGIN = self.A4_HEIGHT - 140
        self.IMAGE_WIDTH = (self.A4_WIDTH - (self.MARGIN*2))/self.IMAGE_SCALE
        self.IMAGE_X = (self.PAGE_WIDTH/2) - (self.IMAGE_WIDTH/2)
        self.LARGE_IMAGE_WIDTH = (self.A4_WIDTH - (self.MARGIN*2))/self.LARGE_IMAGE_SCALE
        self.LARGE_IMAGE_X = (self.PAGE_WIDTH/2) - (self.LARGE_IMAGE_WIDTH/2)
        self.RIGHT_IMAGE_X = self.PAGE_WIDTH - self.IMAGE_WIDTH + self.MARGIN

    def section_title(self, title):
        super().section_title(title)
        self.image_pair = False

    def chapter_title(self, label, date, distance, total_distance):
        super().chapter_title(label, date, distance, total_distance)
        self.image_pair = False

    def text_content(self, text):
        # Flush any single images if needed
        self.add_single_image()

        self.set_font(self.DEJAVU_FONT, size=8)
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
            self.add_image_format_tolerant(image_path, x=self.RIGHT_IMAGE_X, width=self.IMAGE_WIDTH)
            self.pair_y = None
        elif center:
            self.cell(w=self.IMAGE_X, align='L')
            self.add_image_format_tolerant(image_path, width=self.IMAGE_WIDTH)
        elif large:
            self.cell(w=self.LARGE_IMAGE_X, align='L')
            self.add_image_format_tolerant(image_path, width=self.LARGE_IMAGE_WIDTH)
        else:
            # Left
            self.add_image_format_tolerant(image_path, width=self.IMAGE_WIDTH)

        if self.page_added:
            self.pair_y = self.page_top
            right = False

        # Don't break between caption
        self.set_auto_page_break(False, margin=self.MARGIN)
        self.set_font(self.DEJAVU_FONT, style='I', size=8)
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
