from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer


class ModelLessSerializer(Serializer):
    """
    Base serializer class for serializers without model.
    Override 'Serializer' methods 'create' and 'update'
    to exclude warning - 'Class must implement all abstract methods.'
    """

    def create(self, validated_data):
        raise RuntimeError('Method create not implemented.')

    def update(self, instance, validated_data):
        raise RuntimeError('Method update not implemented.')

class RecordSplitSerializer(ModelLessSerializer):
    from_time = IntegerField(min_value=0, default=0)
    to_time = IntegerField(min_value=0, allow_null=True, default=None)

    def __init__(self, **kwargs):
        super(RecordSplitSerializer, self).__init__(**kwargs)
        message = 'To time ({to_time}) must be bigger than from time ({from_time}).'
        self.error_messages['to_time'] = message

    def validate(self, attrs):
        if attrs['to_time'] is not None and attrs['to_time'] < attrs['from_time']:
            self.fail('to_time', to_time=attrs['to_time'], from_time=attrs['from_time'])
        return attrs