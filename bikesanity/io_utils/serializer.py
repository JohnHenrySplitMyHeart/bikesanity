import pickle
from io import BytesIO

from bikesanity.entities.journal import Journal


class Serializer:

    def serialize_journal(self, journal: Journal):
        buffer = BytesIO()
        pickle.dump(journal, buffer)
        buffer.seek(0)
        return buffer

    def serialize_journal_to_disk(self, filename, journal: Journal):
        with open(filename, 'wb') as handle:
            pickle.dump(journal, handle)

    def serialize_to_disk(self, filename, obj):
        with open(filename, 'wb') as handle:
            pickle.dump(obj, handle)

    def serialize_to_byteio(self, obj):
        buffer = BytesIO()
        pickle.dump(obj, buffer)
        buffer.seek(0)
        return buffer

    def unserialize_from_data(self, data):
        try:
            return pickle.load(data)
        except Exception as exc:
            return None
        finally:
            if data: data.close()
