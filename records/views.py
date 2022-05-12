from django.shortcuts import render
from drf_util.decorators import serialize_decorator
from rest_framework.views import APIView

from records.models import Record
from records.serializers import RecordSplitSerializer
from records.settings import get_recordings_storage


class RecordDownloadView(APIView):
    """
    Class that handles Record downloading
    """

    @serialize_decorator(RecordSplitSerializer)
    def get(self, request, pk):
        valid = request.valid
        record = Record.objects.first()

        a = record.file.open()

        #content = a.read()

        return a.file




