import jsonpickle

from bikesanity.entities.content_blocks import Image, Map, TextBlock
from bikesanity.entities.journal import Journal
from bikesanity.entities.page import Page
from bikesanity.entities.json.journal import JsonJournal, JsonPage, JsonDistance, JsonSection, SectionType


class EnumHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):  # data contains {}
        if obj == SectionType.TEXT:
            return 'text'
        elif obj == SectionType.PIC:
            return 'pic'

jsonpickle.handlers.registry.register(SectionType, EnumHandler)


class JsonOutput:

    def __init__(self, local_handler, progress_callback=None):
        self.local_handler = local_handler
        self.progress_callback = progress_callback

    def progress_update(self, percent):
        if self.progress_callback:
            self.progress_callback(progress=percent)

    def miles_primary(self, ds):
        return 'km)' in ds

    def miles_distance(self, ds):
        if not ds or ' miles' not in ds:
            return None
        return ds[:ds.find(' miles')] if self.miles_primary(ds) else ds[ds.find('(')+1:ds.find(' miles')]

    def km_distance(self, ds):
        if not ds or ' km' not in ds:
            return None
        return ds[ds.find('(')+1:ds.find(' km')] if self.miles_primary(ds) else ds[:ds.find(' km')]

    def journal_distance(self, journal: Journal):
        ds = journal.distance_statement or ''
        first_date, last_date = None, None

        if 'to' in ds:
            last_date = ds[ds.rfind('to')+3:]
        if 'on' in ds:
            first_date = ds[ds.rfind('on')+3:]
            last_date = ds[ds.rfind('on')+3:]
        if 'from' and 'to' in ds:
            first_date = ds[ds.rfind('from')+5:ds.rfind('to')]

        return self.miles_primary(ds), self.miles_distance(ds), self.km_distance(ds), first_date, last_date

    def output_journal(self, journal: Journal):

        json_journal = JsonJournal(
            doc_id=journal.journal_id,
            title=journal.journal_title,
            subtitle=journal.journal_subtitle
        )

        json_journal.add_author(journal.journal_author)

        miles_primary, miles, km, first_date, last_date = self.journal_distance(journal)
        json_journal.primaryDistanceUomIsMiles = miles_primary
        json_journal.distanceInMiles = miles
        json_journal.distanceInKilometers = km
        json_journal.firstDate = first_date
        json_journal.lastDate = last_date

        # Update progress
        self.progress_update(percent=10)

        # Iterate over the ToC and process every page
        page_idx = 1

        toc_pages = [toc for toc in journal.toc if toc.page]
        last_toc = toc_pages[-1]

        for toc_item in journal.toc:

            if toc_item.page:
                json_page = JsonPage(id=toc_item.original_id, url=toc_item.url)
                self.output_page(json_page, toc_item.page, page_idx, last=toc_item == last_toc)
                json_journal.add_page(json_page)
                page_idx += 1

            elif toc_item.title:
                json_page = JsonPage(id=None, url=None)
                json_page.contents.set_header(toc_item.title)


            # Calculate and update progress
            self.progress_update(((page_idx / len(toc_pages)) * 80) + 10)


        # Serialize to JSON
        json = jsonpickle.encode(json_journal, unpicklable=False, indent=4)
        self.local_handler.save_generated_json(json)

        # Update progress
        self.progress_update(percent=100)


    def output_page(self, json_page: JsonPage, page: Page, page_idx: int, last=False):

        json_page.contents.set_page(page.title, page.date_statement)

        json_page.contents.set_distance(
            JsonDistance(
                miles=self.miles_distance(page.page_distance),
                km=self.km_distance(page.page_distance),
                totalMilesSoFar=self.miles_distance(page.total_distance),
                totalKmSoFar=self.km_distance(page.total_distance)
            )
        )

        for content in page.contents:
            if isinstance(content, TextBlock):
                for para in content.content_text:
                    para = para.strip()
                    if para:
                        json_page.contents.add_section(
                            JsonSection.text_section(para)
                        )
            elif isinstance(content, Image):
                json_page.contents.add_section(
                    JsonSection.pic_section(
                        id=content.image_id,
                        url=content.original_path_fullsize,
                        filename='{0}.{1}'.format(content.image_id, content.extension),
                        caption=content.caption
                    )
                )
            elif isinstance(content, Map):
                # Maps not supported currently
                pass

