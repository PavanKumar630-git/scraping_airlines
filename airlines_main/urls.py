from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def home(request):
    return JsonResponse({"message": "AirLines Scraper API Running"})


urlpatterns = [

    path("", home),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("airindia/", include("app.scraping.airindia_airlines.urls")),
    path("lufhansa/", include("app.scraping.lufhansa_airlines.urls")),
    path("srilanka/", include("app.scraping.srilanka_airlines.urls")),
]