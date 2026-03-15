from .views import SriLankaViewer

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", SriLankaViewer, basename="srilanka")

urlpatterns = [
    path("", include(router.urls)),
]