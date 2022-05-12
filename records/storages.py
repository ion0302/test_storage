import io
import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from django.core.exceptions import SuspiciousFileOperation
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.crypto import get_random_string
from django.utils.text import get_valid_filename
from requests import Session
from rest_framework.status import is_success
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.storage import FileSystemStorage


class MediaAPISession(Session):
    def __init__(self, base_url: str):
        super(MediaAPISession, self).__init__()
        self.base_url = base_url

    def request(self, method, url, **kwargs):
        return super(MediaAPISession, self).request(method, urljoin(self.base_url, url))

    def health(self):
        return self.get('common/health')


class MediaAPIStorage(Storage):
    def __init__(self, media_api_session: MediaAPISession = None):
        super(MediaAPIStorage, self).__init__()

        if media_api_session is None:
            media_api_session = MediaAPISession(base_url='')

        self.session = media_api_session

    def _open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        response = self.session.get(name)
        response.raise_for_status()
        return ContentFile(content=response.content, name=Path(name).name)

    def _save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)

    # These methods are part of the public API, with default implementations.

    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)

    def get_alternative_name(self, file_root, file_ext):
        """
        Return an alternative filename, by adding an underscore and a random 7
        character alphanumeric string (before the file extension, if one
        exists) to the filename.
        """
        return '%s_%s%s' % (file_root, get_random_string(7), file_ext)

    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's free on the target storage system and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, generate an alternative filename
        # until it doesn't exist.
        # Truncate original name if required, so the new filename does not
        # exceed the max_length.
        while self.exists(name) or (max_length and len(name) > max_length):
            # file_ext includes the dot.
            name = os.path.join(dir_name, self.get_alternative_name(file_root, file_ext))
            if max_length is None:
                continue
            # Truncate file_root if max_length exceeded.
            truncation = len(name) - max_length
            if truncation > 0:
                file_root = file_root[:-truncation]
                # Entire file_root was truncated in attempt to find an available filename.
                if not file_root:
                    raise SuspiciousFileOperation(
                        'Storage can not find an available filename for "%s". '
                        'Please make sure that the corresponding file field '
                        'allows sufficient "max_length".' % name
                    )
                name = os.path.join(dir_name, self.get_alternative_name(file_root, file_ext))
        return name

    def generate_filename(self, filename):
        """
        Validate the filename by calling get_valid_name() and return a filename
        to be passed to the save() method.
        """
        # `filename` may include a path as returned by FileField.upload_to.
        dirname, filename = os.path.split(filename)
        return os.path.normpath(os.path.join(dirname, self.get_valid_name(filename)))

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses must implement *all* of these.

    def delete(self, name):
        """
        Delete the specified file from the storage system.
        """
        raise NotImplementedError('subclasses of Storage must provide a delete() method')

    def exists(self, name):
        """
        Return True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        raise NotImplementedError('subclasses of Storage must provide an exists() method')

    def listdir(self, path):
        """
        List the contents of the specified path. Return a 2-tuple of lists:
        the first item being directories, the second item being files.
        """
        raise NotImplementedError('subclasses of Storage must provide a listdir() method')

    def size(self, name):
        """
        Return the total size, in bytes, of the file specified by name.
        """
        raise NotImplementedError('subclasses of Storage must provide a size() method')

    def url(self, name):
        """
        Return an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        raise NotImplementedError('subclasses of Storage must provide a url() method')
