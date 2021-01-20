import pickle
import bikesanity
import pkg_resources


RESOURCE_DIRECTORY = 'resources'
resource_package = bikesanity.__name__


def _resource_path(paths):
    paths.insert(0, RESOURCE_DIRECTORY)
    return '/'.join(paths)


def get_resource_string(paths):
    resource_path = _resource_path(paths)
    data = pkg_resources.resource_string(resource_package, resource_path)
    return data.decode()


def get_resource_stream(paths):
    resource_path = _resource_path(paths)
    return pkg_resources.resource_stream(resource_package, resource_path)


def unserialize_resource_stream(paths):
    with get_resource_stream(paths) as stream:
        return pickle.load(stream)
