"""
URL configuration for apis_ontology project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import include, path
from rest_framework import routers

from apis_ontology.api.views import PlaceViewSet, WorkDetailViewSet, WorkPreviewViewSet


router = routers.DefaultRouter()

router.register(r"work-preview", WorkPreviewViewSet, basename="work-preview")
router.register(r"work-detail", WorkDetailViewSet, basename="work-detail")
router.register(r"place-detail", PlaceViewSet, basename="place-detail")

urlpatterns += [
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include((router.urls, "apis_ontology"))),
]
