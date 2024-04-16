"""
Views for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from rest_framework import permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from apis_ontology.models import Work
from .serializers import WorkPreviewSerializer


class WorkPreviewPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class WorkPreviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint which returns minimal, partial Work objects
    enriched with data from other, related entities.

    The full result set is meant to populate the default view of the
    "Search" page on the Vue.js frontend (initial view, view when
    search has been cleared).
    """

    serializer_class = WorkPreviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = WorkPreviewPagination

    def get_queryset(self):
        return (
            Work.objects.all()
            .filter(siglum__isnull=False)
            .order_by("title", "subtitle")
        )
