import uuid


class ContentBlock:
    def clear_resources(self):
        pass

    def _sanitize_path(self, path):
        path = path.split('?')[0]
        if path.startswith('/'): path = path[1:]
        return path


class TextBlock(ContentBlock):
    def __init__(self, content_text):
        self.content_text = content_text


class Heading(ContentBlock):
    def __init__(self, content_text):
        self.content_text = content_text


class Image(ContentBlock):
    def __init__(self, original_path_small, original_path_fullsize, caption, image_small, image_fullsize):
        self.image_id = str(uuid.uuid4())

        self.original_path_small = self._sanitize_path(original_path_small)
        self.original_path_fullsize = self._sanitize_path(original_path_fullsize)
        self.extension = self._find_extension(original_path_small)

        self.caption = caption

        self.image_small = image_small
        self.image_fullsize = image_fullsize

    def _find_extension(self, path):
        if '.' in path:
            path = path[path.rfind('.')+1:]
            return path.split('?')[0].lower()

    def clear_resources(self):
        if self.image_small: self.image_small.close()
        if self.image_fullsize: self.image_fullsize.close()
        self.image_small, self.image_fullsize = None, None

    def get_small_resource_path(self):
        return '{0}.small.{1}'.format(self.image_id, self.extension)

    def get_fullsize_resource_path(self):
        return '{0}.{1}'.format(self.image_id, self.extension)


class Map(ContentBlock):
    def __init__(self, original_id, caption, gpx_data=None, json_data=None, url=None):
        self.map_id = str(uuid.uuid4())
        self.original_id = original_id
        self.caption = caption
        self.gpx_data = gpx_data
        self.json_data = json_data
        self.original_url = url

    def set_gpx_data(self, gpx_data):
        self.gpx_data = gpx_data

    def set_map_data(self, gpx_data, json_data):
        self.gpx_data = gpx_data
        self.json_data = json_data

    def clear_resources(self):
        if self.gpx_data: self.gpx_data.close()
        if self.json_data: self.json_data.close()
        self.gpx_data = None
        self.json_data = None

    def get_resource_path(self):
        return '{0}.gpx'.format(self.map_id)
