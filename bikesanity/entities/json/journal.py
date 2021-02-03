from enum import Enum, auto


class SectionType(Enum):
    TEXT = auto()
    PIC = auto()


class JsonSection:
    def __init__(self, section_type: SectionType):
        self.sectionType = section_type
        self.text = None
        self.picId = None
        self.picFilename = None
        self.picUrl = None
        self.picCaption = None

    @staticmethod
    def text_section(text):
        section = JsonSection(SectionType.TEXT)
        section.text = text
        return section

    @staticmethod
    def pic_section(id, filename, url, caption):
        section = JsonSection(SectionType.PIC)
        section.picId = id
        section.picFilename = filename
        section.picUrl = url
        section.picCaption = caption
        return section


class JsonDistance:
    def __init__(self, miles=None, km=None, totalMilesSoFar=None, totalKmSoFar=None):
        self.miles = miles
        self.km = km
        self.totalMilesSoFar = totalMilesSoFar
        self.totalKmSoFar = totalKmSoFar


class JsonPageContents:
    def __init__(self):
        self.isHeader = None
        self.title = None
        self.date = None
        self.distance = None
        self.sections = []

    def set_header(self, header):
        self.isHeader = True
        self.title = header

    def set_page(self, title, date):
        self.isHeader = False
        self.title = title
        self.date = date

    def set_distance(self, distance: JsonDistance):
        self.distance = distance

    def add_section(self, section: JsonSection):
        self.sections.append(section)


class JsonPage:
    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.contents = JsonPageContents()


class JsonJournal:

    def __init__(self, doc_id, title, subtitle):
        self.docId = doc_id
        self.title = title
        self.subtitle = subtitle

        self.distanceInMiles = None
        self.distanceInKilometers = None
        self.primaryDistanceUomIsMiles = True
        self.firstDate = None
        self.lastDate = None
        self.lastUpdate = None

        self.authors = []
        self.pages = []

    def add_author(self, author):
        self.authors.append(author)

    def add_page(self, page: JsonPage):
        self.pages.append(page)
