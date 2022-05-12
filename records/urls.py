from django.urls import path
from rest_framework.routers import DefaultRouter

from records.views import RecordDownloadView

router = DefaultRouter()

urlpatterns = [
    path('<int:pk>/download/', RecordDownloadView.as_view(), name='download_report'),
    *router.get_urls(),
]
