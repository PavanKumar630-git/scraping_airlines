from .views import LufhansaViewer

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", LufhansaViewer, basename="lufhansa")

urlpatterns = [
    path("", include(router.urls)),
]