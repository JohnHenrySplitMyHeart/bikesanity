import bikesanity.io_utils.log_handler as log_handler
from bikesanity.entities.content_blocks import Image, Map, TextBlock
from bikesanity.entities.journal import Journal

from .journal_pdf import JournalPdf


class PdfTocEntry:
    def __init__(self, title, page_no, is_header):
        self.is_header = is_header
        self.page_no = str(page_no)
        self.title = title


class PdfOutput:

    MAX_PDF_SECTIONS = 25


    def __init__(self, local_handler, progress_callback=None):
        self.local_handler = local_handler
        self.progress_callback = progress_callback

    def progress_update(self, percent):
        if self.progress_callback:
            self.progress_callback(progress=percent)


    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def output_journal(self, journal: Journal):

        # Determine if it needs to be split into parts, and make the split
        full_pages = [content for content in journal.toc if content.page]

        if len(full_pages) <= self.MAX_PDF_SECTIONS:
            log_handler.log.info('Writing to single PDF file')
            self.output_journal_part(journal, journal.toc)
        else:
            start_page = 0
            part = 1

            log_handler.log.info('Splitting up into multiple PDF files')
            for chunk in self.chunks(journal.toc, self.MAX_PDF_SECTIONS):
                log_handler.log.info('Creating PDF part {0}'.format(part))
                self.output_journal_part(journal, chunk, part=part, from_page=start_page)
                part += 1
                start_page += self.MAX_PDF_SECTIONS


    def output_journal_part(self, journal: Journal, contents, part=None, from_page=None):
        journal_pdf = JournalPdf(title=journal.journal_title, author=journal.journal_author, part=part)

        # Create a cover
        journal_pdf.set_auto_page_break(False, margin=journal_pdf.MARGIN)
        journal_pdf.cover_title(journal.journal_title, journal.journal_subtitle, journal.journal_author, journal.distance_statement, part=part)

        journal_pdf.clipping_rect(0, 100, journal_pdf.A4_WIDTH, 180, False)
        if journal.cover_image:
            self.output_image(journal_pdf, journal.cover_image)
        journal_pdf.set_auto_page_break(True, margin=journal_pdf.MARGIN)
        journal_pdf.unset_clipping()

        # Leave space for the TOC
        journal_pdf.add_page()

        pdf_toc = []

        # Process pages
        page_idx = from_page or 0

        for toc_item in contents:

            if toc_item.page:
                log_handler.log.info('Processing page {0} to PDF'.format(page_idx))
                page_idx += 1

                journal_pdf.update_page_title(toc_item.page.title)

                journal_pdf.add_page()
                pdf_toc.append(PdfTocEntry(toc_item.page.title, journal_pdf.page_no()-2, False))

                journal_pdf.chapter_title(
                    toc_item.page.title, toc_item.page.date_statement,
                    toc_item.page.page_distance, toc_item.page.total_distance
                )

                for content in toc_item.page.contents:
                    if isinstance(content, TextBlock):
                        self.output_textblock(journal_pdf, content)
                    elif isinstance(content, Image):
                        self.output_image(journal_pdf, content)
                    elif isinstance(content, Map):
                        self.output_map(journal_pdf, content)

            elif toc_item.title:
                journal_pdf.section_title(toc_item.title)
                pdf_toc.append(PdfTocEntry(toc_item.title, journal_pdf.page_no()-2, True))

        # Go back and populate the table of contents
        final_page = journal_pdf.page_no()
        journal_pdf.page = 2
        journal_pdf.set_y(30)

        journal_pdf.section_title('Table of Contents')

        journal_pdf.add_toc(pdf_toc)

        # Reset to the last page
        journal_pdf.page = final_page

        log_handler.log.info('Writing PDF file (this can be CPU intensive and take a few minutes)')
        self.local_handler.save_generated_pdf(journal_pdf, part=part)

        # Cleanup font files
        journal_pdf.cleanup_tmp_files()


    def output_textblock(self, journal_pdf: JournalPdf, content: TextBlock):
        for para in content.content_text:
            para = para.strip()

            if not para: continue

            # Don't write out the previous page section dividers, as they're no longer needed
            if para.startswith('>>>') or para.startswith('<<<'): continue

            journal_pdf.text_content(para)

    def output_image(self, journal_pdf: JournalPdf, image: Image, height=None):
        url_fullsize = self.output_pic(image)
        journal_pdf.add_image(url_fullsize, image.caption, height=height)

    def output_map(self, journal_pdf: JournalPdf, map: Map):
        pass

    def output_pic(self, image: Image):
        return self.local_handler.get_resource_path('{0}.{1}'.format(image.image_id, image.extension))
