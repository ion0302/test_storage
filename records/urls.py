from django.urls import path
from rest_framework.routers import DefaultRouter

from records.views import RecordDownloadView, RecordSplitView

router = DefaultRouter()

urlpatterns = [
    path('<int:pk>/download/', RecordDownloadView.as_view(), name='download_report'),
    path('<int:pk>/split/', RecordSplitView.as_view(), name='record_split'),
    *router.get_urls(),
]
