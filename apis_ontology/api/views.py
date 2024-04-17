"""
Views for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef
from django.db.models.functions import JSONObject
from rest_framework import permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from apis_ontology.models import Expression, Work
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
        related_expressions = Expression.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_reverse__in=["realises"],
        )

        works = Work.objects.annotate(
            expression_data=ArraySubquery(
                related_expressions.values(
                    json=JSONObject(
                        edition="edition",
                        edition_type="edition_type",
                        publication_date="publication_date_iso_formatted",
                    )
                )
            )
        ).order_by("title", "subtitle")

        return works
