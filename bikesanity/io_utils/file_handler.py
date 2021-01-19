import hashlib
import shutil
import os
import mimetypes


class FileHandler:

    HASH_BUFFER_SIZE = 6553600

    def __init__(self):
        pass

    def output_binary_to_file(self, filename, data):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data.seek(0)
        with open(filename, 'wb') as handle:
            shutil.copyfileobj(data, handle)

    def output_bytes_to_file(self, filename, bytes):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as handle:
            handle.write(bytes)

    def output_text_to_file(self, filename, text):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as handle:
            handle.write(text)

    def remove_directory(self, path):
        try:
            shutil.rmtree(path)
        except:
            pass

    def file_exists(self, filename):
        return os.path.isfile(filename)

    def get_file_content(self, filename):
        if not self.file_exists(filename):
            raise RuntimeError('File did not exist: {0}'.format(filename))
        with open(filename, 'r') as handle:
            return handle.read()

    def get_binary_content(self, filename):
        if not self.file_exists(filename):
            raise RuntimeError('File did not exist: {0}'.format(filename))
        with open(filename, 'rb') as handle:
            return handle.read()

    def get_binary(self, filename):
        if not self.file_exists(filename):
            raise RuntimeError('File did not exist: {0}'.format(filename))
        return open(filename, 'rb')

    def file_size(self, filename):
        return os.path.getsize(filename)

    def calculate_sha1_hash(self, filename):
        sha1 = hashlib.sha1()

        with open(filename, 'rb') as f:
            while True:
                data = f.read(self.HASH_BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def extension_from_type(self, mime_type):
        extension = mimetypes.guess_extension(mime_type)
        if extension and extension[0] == '.': extension = extension[1:]
        return extension


