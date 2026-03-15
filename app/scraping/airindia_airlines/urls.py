from .views import AirIndiaViewer

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", AirIndiaViewer, basename="magma")

urlpatterns = [
    path("", include(router.urls)),
]