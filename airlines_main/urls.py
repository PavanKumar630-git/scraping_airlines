# from django.urls import path, include
# from django.http import JsonResponse
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# def home(request):
#     return JsonResponse({"message": "AirLines Scraper API Running"})


# urlpatterns = [

#     path("", home),

#     path("schema/", SpectacularAPIView.as_view(), name="schema"),

#     path(
#         "docs/",
#         SpectacularSwaggerView.as_view(url_name="schema"),
#         name="swagger-ui",
#     ),
#     path("airindia/", include("app.scraping.airindia_airlines.urls")),
#     # path("lufhansa/", include("app.scraping.lufhansa_airlines.urls")),
#     path("srilanka/", include("app.scraping.srilanka_airlines.urls")),
# ]

# airlines_main/urls.py
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from app.scraping.airindia_airlines.views import CommonViewer

def home(request):
    return JsonResponse({"message": "AirLines Scraper API Running"})

common_router = DefaultRouter()
common_router.register("common", CommonViewer, basename="common")

urlpatterns = [
    path("", home),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # /common/soft-delete/
    path("", include(common_router.urls)),

    # Airline specific
    path("airindia/", include("app.scraping.airindia_airlines.urls")),
    path("srilanka/", include("app.scraping.srilanka_airlines.urls")),
    path("malaysia/", include("app.scraping.malaysia_airlines.urls")),
    path("azerbaijan/", include("app.scraping.azerbaijan_airlines.urls")),
    path("lotpolish/", include("app.scraping.lotpolish_airlines.urls")),

]