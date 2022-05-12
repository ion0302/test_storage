# Todo: settings like in rest_framework
from django.core.files.storage import Storage
from django.utils.module_loading import import_string


DEFAULTS = {
    'RECORDINGS_STORAGE_BACKEND':  "records.storages.MediaAPIStorage",
    'RECORDINGS_STORAGE_BACKEND_ARGS':  (),
    'RECORDINGS_STORAGE_BACKEND_KWARGS': {},
}


IMPORT_STRINGS = [
    'RECORDINGS_STORAGE_BACKEND',
]


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for recordings setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class RecordingsSettings:
    def __init__(self, defaults: dict, import_strings: list):
        self.defaults = defaults
        self.import_strings = import_strings

    def __getitem__(self, setting_name: str):
        value = self.defaults.get(setting_name)

        if setting_name in self.import_strings:
            value = import_from_string(value, setting_name)

        return value


recordings_settings = RecordingsSettings(DEFAULTS, IMPORT_STRINGS)


def get_recordings_storage() -> Storage:
    storage_class = recordings_settings['RECORDINGS_STORAGE_BACKEND']
    storage_class_args = recordings_settings['RECORDINGS_STORAGE_BACKEND_ARGS']
    storage_class_kwargs = recordings_settings['RECORDINGS_STORAGE_BACKEND_KWARGS']

    return storage_class(*storage_class_args, **storage_class_kwargs)
