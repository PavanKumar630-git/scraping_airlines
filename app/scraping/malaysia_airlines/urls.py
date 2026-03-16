from .views import MalaysiaViewer

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", MalaysiaViewer, basename="malaysia")

urlpatterns = [
    path("", include(router.urls)),
]