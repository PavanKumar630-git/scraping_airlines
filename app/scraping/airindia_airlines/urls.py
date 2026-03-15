# from .views import AirIndiaViewer,CommonViewer

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register("", AirIndiaViewer, basename="airindia")
# router.register("common", CommonViewer, basename="common")

# urlpatterns = [
#     path("", include(router.urls)),
# ]
# airindia_airlines/urls.py  ← remove CommonViewer from here
from .views import AirIndiaViewer
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", AirIndiaViewer, basename="airindia")

urlpatterns = [
    path("", include(router.urls)),
]
