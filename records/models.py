from django.db import models

from records.settings import get_recordings_storage


class Record(models.Model):
    file = models.FileField(storage=get_recordings_storage, max_length=1000)
