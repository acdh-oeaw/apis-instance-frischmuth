"""
Views for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from django.contrib.postgres.expressions import ArraySubquery, Subquery
from django.db.models import OuterRef
from django.db.models.functions import JSONObject
from rest_framework import permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from apis_ontology.models import Expression, Organisation, Work, WorkType
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
        work_types = WorkType.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["has type"],
        )

        expression_publisher = Organisation.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__name_reverse__in=["has publisher"],
        )

        related_expressions = Expression.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_reverse__in=["realises"],
        ).annotate(
            publisher=Subquery(expression_publisher.values("name")),
        )

        works = (
            Work.objects.all()
            .annotate(
                expression_data=ArraySubquery(
                    related_expressions.values(
                        json=JSONObject(
                            title="title",
                            subtitle="subtitle",
                            edition="edition",
                            edition_type="edition_type",
                            language="language",
                            publication_date="publication_date_iso_formatted",
                            publisher="publisher",
                        )
                    )
                ),
                work_type=Subquery(
                    work_types.values(
                        json=JSONObject(
                            name="name",
                            name_plural="name_plural",
                        )
                    ),
                ),
            )
            .order_by("title", "subtitle")
        )

        return works
