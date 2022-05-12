from django.http import HttpResponse
from drf_util.decorators import serialize_decorator
from pydub import AudioSegment
from rest_framework.views import APIView
from django.core.files.temp import NamedTemporaryFile

from records.models import Record
from records.serializers import RecordSplitSerializer


def make_temp_file(content, suffix=".mp3"):
    temp_file = NamedTemporaryFile('wb', suffix=suffix)
    temp_file.write(content)
    temp_file.seek(0)
    return temp_file

def temp_file_generation(file):
    """
    Function that writes into a temporary file content from request
    :param file: file content from response
    :return: temporary file
    """
    temp_file = make_temp_file(file)
    return AudioSegment.from_mp3(temp_file.name)

def crop_file(file, from_time=0, to_time=0):
    """
    Function that writes a temporary like an mp3 file
    :param file: file content from response
    :param from_time: segment start in seconds
    :param to_time: segment end in seconds
    :return: temporary file
    """
    temp_file = temp_file_generation(file)
    duration = int(temp_file.duration_seconds)
    # getting max range, if to value not defined.
    if not to_time:
        to_time = duration
    # convert seconds to milliseconds
    from_time = 1000 * min(from_time, duration)  # getting value in duration range and convert to milliseconds
    to_time = 1000 * to_time
    cropped = temp_file[from_time:to_time]
    return cropped.export()


class RecordDownloadView(APIView):
    """
    Class that handles Record downloading
    """

    @serialize_decorator(RecordSplitSerializer)
    def get(self, request, pk):
        valid = request.valid
        record = Record.objects.first()

        file = record.file.open()
        content = file.read()

        # if any(valid):
        #     content = crop_file(content, **valid)
        response = HttpResponse(content, content_type=bytes)
        response['Content-Disposition'] = f'attachment; filename={file.file.name}'
        return response








