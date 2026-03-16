from .views import AzerbaijanViewer

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", AzerbaijanViewer, basename="azerbaijan")

urlpatterns = [
    path("", include(router.urls)),
]