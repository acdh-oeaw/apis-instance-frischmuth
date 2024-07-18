"""
Views for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from django.contrib.postgres.expressions import ArraySubquery, Subquery
from django.db.models import OuterRef
from django.db.models.functions import JSONObject
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, permissions, viewsets

from apis_ontology.models import Expression, Organisation, Place, Work, WorkType

from .filters import WorkPreviewSearchFilter
from .serializers import WorkPreviewSerializer


class WorkPreviewPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.facets = self.calculate_facets(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        response = super(WorkPreviewPagination, self).get_paginated_response(data)
        response.data.update(
            {
                self.limit_query_param: self.limit,
                self.offset_query_param: self.offset,
                "facets": self.facets,
            }
        )
        return pagination.Response(dict(sorted(response.data.items())))

    def get_facet_data(self, field, queryset):
        # Implement facet data calculation
        res = {}
        # Count occurrences
        for item in queryset.all():
            attr_value = getattr(item, field)
            # given that we use array fields there can be list of lists in annotations
            if attr_value and isinstance(attr_value[0], list):
                flattened_list = [x for sublist in attr_value for x in sublist]
            else:
                flattened_list = attr_value
            # Count occurrences
            for k in flattened_list:
                if k in res:
                    res[k] += 1
                else:
                    res[k] = 1
        return [{"key": k, "count": v} for k, v in res.items()]

    def calculate_facets(self, queryset):
        # Implement facet calculation
        res = {}
        for field in queryset.query.annotations.keys():
            if field.startswith("facet_"):
                res[field.replace("facet_", "")] = self.get_facet_data(field, queryset)

        return res

    def get_paginated_response_schema(self, schema):
        res_schema = super(WorkPreviewPagination, self).get_paginated_response_schema(
            schema
        )
        props = res_schema["properties"]
        new_props = {
            self.limit_query_param: {
                "type": "integer",
                "nullable": True,
                "example": 100,
            },
            self.offset_query_param: {
                "type": "integer",
                "nullable": True,
                "example": 300,
            },
            "facets": {
                "properties": {
                    "language": {
                        "type": "array",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string"},
                                "count": {"type": "integer"},
                            },
                        },
                        "example": [{"key": "eng", "count": 100}],
                    },
                },
                "type": "object",
                "nullable": True,
            },
        }

        props.update(new_props)
        res_schema["properties"] = dict(sorted(props.items()))

        return res_schema


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkPreviewSearchFilter

    def get_queryset(self):
        work_types = WorkType.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["has type"],
        ).values(
            json=JSONObject(
                name="name",
                name_plural="name_plural",
            )
        )

        expression_publisher = Organisation.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__name_reverse__in=["has publisher"],
        ).values("name")

        expression_place = Place.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["is published in"],
        ).values_list("name")

        related_expressions = (
            Expression.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_reverse__in=["realises"],
            ).annotate(
                publisher=Subquery(expression_publisher),
                place=ArraySubquery(expression_place),
            )
        ).values(
            json=JSONObject(
                title="title",
                subtitle="subtitle",
                edition="edition",
                edition_type="edition_type",
                language="language",
                publication_date="publication_date_iso_formatted",
                publisher="publisher",
                place_of_publication="place",
            )
        )

        facet_languages = Expression.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_reverse__in=["realises"],
            language__len__gt=0,
        ).values("language")

        works = (
            Work.objects.all()
            .annotate(
                expression_data=ArraySubquery(related_expressions),
                work_type=ArraySubquery(work_types),
                facet_language=ArraySubquery(facet_languages),
            )
            .order_by("title", "subtitle")
        )

        return works
