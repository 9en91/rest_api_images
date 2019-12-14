from django.conf.urls.static import static
from django.urls import path
from core.settings import MEDIA_URL, MEDIA_ROOT
from dataset.views import DataApiView, DeleteApiView

urlpatterns = [
    path("dataset/", DataApiView.as_view()),
    path("dataset/<id>/", DeleteApiView.as_view()),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
