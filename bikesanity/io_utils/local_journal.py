import io
import os


from bikesanity.entities.content_blocks import Image, Map
from .resources import get_resource_stream
from .serializer import Serializer
from .file_handler import FileHandler


class LocalJournalHandler(FileHandler):

    def __init__(self, base_path, journal_id):
        super().__init__()
        self.base_path = base_path
        self.journal_id = journal_id
        self.serializer = Serializer()

    def get_path(self, filename):
        return os.path.join(self.base_path, self.journal_id, filename)

    def get_base_path(self):
        return self.get_path('')

    def get_resource_path(self, filename):
        return os.path.join(self.base_path, self.journal_id, 'resources', filename)

    def get_html_path(self, filename):
        return os.path.join(self.base_path, self.journal_id, 'html', filename)

    def get_index(self):
        return self.get_file_content(
            os.path.join(self.base_path, self.journal_id, 'index.html')
        )

    def get_html_page_id(self, page_id, additional_path=None):
        terms = [self.base_path, self.journal_id]
        if additional_path: terms.append(additional_path)
        terms.append(page_id + '.html')
        return self.get_file_content(os.path.join(*terms))

    def get_image_binary(self, path, additional_path=None):
        terms = [self.base_path, self.journal_id]
        if additional_path: terms.append(additional_path)
        terms.append(path)
        return io.BytesIO(self.get_binary_content(os.path.join(*terms)))

    def _resource_key(self, id, extension, suffix=''):
        return '{0}{1}.{2}'.format(id, suffix, extension)

    def save_html_original(self, filename, html):
        self.output_bytes_to_file(self.get_path(filename), html)

    def save_image_original(self, image: Image):
        if image.image_fullsize:
            self.output_binary_to_file(self.get_path(image.original_path_fullsize), image.image_fullsize)
        if image.image_small:
            self.output_binary_to_file(self.get_path(image.original_path_small), image.image_small)

    def save_map_original(self, map: Map):
        if map.gpx_data:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'maps', self._resource_key(map.map_id, 'gpx')
            ), map.gpx_data)
        if map.json_data:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'maps', self._resource_key(map.map_id, 'json')
            ), map.json_data)

    def save_image_resource(self, image: Image):
        # Output fullsize image
        if image.image_fullsize:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'resources', self._resource_key(image.image_id, image.extension)
            ), image.image_fullsize)

        # Output small image
        if image.image_small:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'resources', self._resource_key(image.image_id, image.extension, suffix='.small')
            ), image.image_small)

    def save_map_resource(self, map: Map):
        if map.gpx_data:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'resources', self._resource_key(map.map_id, 'gpx')
            ), map.gpx_data)
        if map.json_data:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'resources', self._resource_key(map.map_id, 'json')
            ), map.json_data)

    def load_map_gpx(self, map: Map):
        return self.get_file_content(os.path.join(
            self.base_path, self.journal_id, 'resources', self._resource_key(map.map_id, 'gpx')
        ))

    def save_js_resource(self, js, content):
        if content:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'javascript', js
            ), content)

    def save_css_resource(self, css, content):
        if content:
            self.output_binary_to_file(os.path.join(
                self.base_path, self.journal_id, 'css', css
            ), content)

    def save_generated_html(self, soup, filename):
        html = str(soup)
        filename = '{0}.html'.format(filename)
        path = self.get_html_path(filename)
        self.output_text_to_file(path, html)
        return filename

    def serialize_and_save_journal(self, journal):
        serialized = self.serializer.serialize_journal(journal)
        self.output_binary_to_file(os.path.join(
            self.base_path, self.journal_id, 'journal.pickle'
        ), serialized)

    def load_serialized_journal(self):
        return self.serializer.unserialize_from_data(
            self.get_binary(os.path.join(
                self.base_path, self.journal_id, 'journal.pickle'
            ))
        )

    def remove_directory(self, path):
        super().remove_directory(os.path.join(
            self.base_path, self.journal_id, path
        ))

    def copy_resource_stream(self, paths, output_paths):
        stream = get_resource_stream(paths)

        full_output_paths = [ self.base_path, self.journal_id, 'html' ]
        full_output_paths.extend(output_paths)

        self.output_binary_to_file(os.path.join(*full_output_paths), stream)
        stream.close()
