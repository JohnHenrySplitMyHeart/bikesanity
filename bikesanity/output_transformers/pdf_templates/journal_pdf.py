from .base_pdf_template import BasePdfTemplate


class JournalPdf(BasePdfTemplate):

    IMAGE_SCALE = 1.2


    def __init__(self, title, author, part=None):
        super().__init__(title, author, part)
        self.IMAGE_WIDTH = (self.A4_WIDTH - (self.MARGIN*2))/self.IMAGE_SCALE
        self.IMAGE_X = (self.PAGE_WIDTH/2) - (self.IMAGE_WIDTH/2)

    def text_content(self, text):
        self.set_font(self.DEJAVU_FONT, size=12)
        self.multi_cell(w=0, h=8, txt=text, align='J')
        self.ln(10)

    def add_image_large(self, image_path, caption):
        self.add_image(image_path, caption)

    def add_image(self, image_path, caption, height=None):
        self.cell(w=self.IMAGE_X, align='L')

        # Attempt to add the image in, trying different formats if the given extension is wrong (due to amateur treatment
        # in the source)
        if height:
            self.add_image_format_tolerant(image_path, height=height)
        else:
            self.add_image_format_tolerant(image_path, width=self.IMAGE_WIDTH)

        # Don't break between the image and the caption
        self.set_auto_page_break(False, margin=self.MARGIN)
        self.set_font(self.DEJAVU_FONT, style='I', size=10)
        self.ln(5)
        self.multi_cell(w=self.PAGE_WIDTH, h=5, txt=caption, align='C')
        self.ln(9)
        self.set_auto_page_break(True, margin=self.MARGIN)

    def add_single_image(self):
        pass

    def add_page_if_near_bottom(self):
        self.add_page()
