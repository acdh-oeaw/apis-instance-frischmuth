"""
Views for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from apis_core.apis_metainfo.models import Uri
from django.contrib.postgres.expressions import ArraySubquery, Subquery
from django.db.models import Max, Min, OuterRef, Q
from django.db.models.functions import JSONObject
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, pagination, permissions, viewsets

from apis_ontology.models import (
    Archive,
    Character,
    Expression,
    Organisation,
    Person,
    PhysicalObject,
    Place,
    Topic,
    Work,
    WorkType,
)

from .filters import WorkPreviewSearchFilter
from .serializers import (
    PlaceDetailDataSerializer,
    WorkDetailSerializer,
    WorkPreviewSerializer,
    get_work_type_data,
)


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

    def _build_work_type_hierarchy(self, items):
        # Create initial count dictionary
        counts = {}
        hierarchy = {}

        # First pass: Count direct occurrences and build hierarchy
        for item in items:
            if not item:
                continue
            type_id = item.get("id")
            parent_id = item.get("parent")

            if type_id not in counts:
                counts[type_id] = {
                    "id": type_id,
                    "name": item.get("name"),
                    "count": 1,
                    "parent": parent_id,
                    "children": [],
                }
            else:
                counts[type_id]["count"] += 1

            if parent_id:
                # Recursively fetch all parent data until root
                current_parent_id = parent_id
                while current_parent_id:
                    if current_parent_id not in hierarchy:
                        hierarchy[current_parent_id] = set()
                    if current_parent_id not in counts:
                        parent_data = get_work_type_data(current_parent_id)
                        counts[current_parent_id] = parent_data
                        # Add this type to its parent's hierarchy
                        if parent_data.get("parent"):
                            if parent_data["parent"] not in hierarchy:
                                hierarchy[parent_data["parent"]] = set()
                            hierarchy[parent_data["parent"]].add(current_parent_id)
                        current_parent_id = parent_data.get("parent")
                    else:
                        current_parent_id = counts[current_parent_id].get("parent")
                # Add original type to its immediate parent's hierarchy
                hierarchy[parent_id].add(type_id)

        # Fetch any missing data for types without parents
        for type_id, data in counts.items():
            if not data:
                counts[type_id] = get_work_type_data(type_id)

        # Second pass: Add child counts to parents and build tree
        def aggregate_counts(type_id):
            total = counts[type_id]["count"]
            if type_id in hierarchy:
                for child_id in hierarchy[type_id]:
                    child_total = aggregate_counts(child_id)
                    total += child_total
                    counts[type_id]["children"].append(
                        {
                            "id": counts[child_id]["id"],
                            "key": counts[child_id]["name"],
                            "count": counts[child_id]["count"],
                            "children": counts[child_id]["children"],
                        }
                    )
            counts[type_id]["count"] = total
            return total

        # Start aggregation from root nodes (those without parents)
        root_nodes = [type_id for type_id, data in counts.items() if not data["parent"]]
        result = []
        for root in root_nodes:
            aggregate_counts(root)
            result.append(
                {
                    "id": counts[root]["id"],
                    "key": counts[root]["name"],
                    "count": counts[root]["count"],
                    "children": counts[root]["children"],
                }
            )

        return result

    def get_facet_data(self, field, queryset):
        # Special handling for work_type field
        if field == "work_type":
            items = []
            for item in queryset.all():
                attr_value = getattr(item, field)
                if attr_value:
                    items.extend(attr_value)
            return self._build_work_type_hierarchy(items)

        # Regular facet calculation for other fields
        res = {}
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
            elif field == "work_type":
                res["work_type"] = self.get_facet_data(field, queryset)

        return res

    def get_schema_operation_parameters(self, view):
        params = [
            {
                "name": self.limit_query_param,
                "in": "query",
                "description": "Number of results to return per page.",
                "required": False,
                "schema": {
                    "type": "integer",
                    "default": self.default_limit,
                    "maximum": self.max_limit,
                    "minimum": 1,
                },
            },
            {
                "name": self.offset_query_param,
                "in": "query",
                "description": "The initial index from which to return the results.",
                "required": False,
                "schema": {
                    "type": "integer",
                    "default": 0,
                    "minimum": 0,
                },
            },
        ]
        return params

    def get_paginated_response_schema(self, schema):
        res_schema = super(WorkPreviewPagination, self).get_paginated_response_schema(
            schema
        )
        props = res_schema["properties"]
        new_props = {
            self.limit_query_param: {
                "type": "integer",
                "example": 100,
                "maximum": self.max_limit,
                "default": self.default_limit,
                "minimum": 1,
            },
            self.offset_query_param: {
                "type": "integer",
                "example": 300,
                "minimum": 0,
                "default": 0,
            },
            "facets": {
                "properties": {
                    "language": {
                        "type": "array",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "required": True,
                                },
                                "count": {
                                    "type": "integer",
                                    "required": True,
                                },
                            },
                        },
                        "example": [
                            {
                                "key": "Deutsch",
                                "count": 100,
                            }
                        ],
                    },
                    "topic": {
                        "type": "array",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "required": True,
                                },
                                "count": {
                                    "type": "integer",
                                    "required": True,
                                },
                            },
                        },
                        "example": [
                            {
                                "key": "Traum",
                                "count": 3,
                            }
                        ],
                    },
                    "work_type": {
                        "type": "array",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "required": True,
                                },
                                "key": {
                                    "type": "string",
                                    "required": True,
                                },
                                "count": {
                                    "type": "integer",
                                    "required": True,
                                },
                                "children": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#",
                                    },
                                },
                            },
                        },
                        "example": [
                            {
                                "id": 4,
                                "key": "Prosa",
                                "count": 150,
                                "children": [
                                    {
                                        "id": 5,
                                        "key": "Roman",
                                        "count": 50,
                                        "children": [],
                                    }
                                ],
                            }
                        ],
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
        work_type_parent = WorkType.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"), triple_set_from_obj__prop__id=7
        ).values("id")
        work_types = (
            WorkType.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_forward__in=["has type"],
            )
            .annotate(parent=Subquery(work_type_parent[:1]))
            .values(
                json=JSONObject(
                    id="id", name="name", name_plural="name_plural", parent="parent"
                )
            )
        )

        expression_publisher = Organisation.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__name_reverse__in=["has publisher"],
        ).values("name")

        expression_places = (
            Place.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_forward__in=["is published in"],
            )
            .distinct()
            .values_list("name")
        )

        related_expressions = (
            Expression.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_reverse__in=["realises"],
            ).annotate(
                publisher=Subquery(expression_publisher[:1]),
                places=ArraySubquery(expression_places),
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
                place_of_publication="places",
            )
        )

        facet_languages = (
            Expression.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_reverse__in=["realises"],
                language__len__gt=0,
            )
            .distinct()
            .values("language")
        )

        filter_years = Expression.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_reverse__in=["realises"],
            publication_date_iso_formatted__isnull=False,
        )

        facet_topics = Topic.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["is about topic"],
        ).values_list("name")

        works = (
            Work.objects.all()
            .annotate(
                expression_data=ArraySubquery(related_expressions),
                work_type=ArraySubquery(work_types),
                facet_language=ArraySubquery(facet_languages),
                facet_topic=ArraySubquery(facet_topics),
                min_year=Subquery(
                    filter_years.annotate(
                        year=Min("publication_date_iso_formatted__year")
                    ).values("year")[:1]
                ),
                max_year=Subquery(
                    filter_years.annotate(
                        year=Max("publication_date_iso_formatted__year")
                    ).values("year")[:1]
                ),
            )
            .order_by("title", "subtitle")
        )

        return works


class WorkDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """API endpoint which returns full Work objects.

    The full result set is meant to populate the detail view of the
    "Work" page on the Vue.js frontend.
    """

    serializer_class = WorkDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        related_uris = Uri.objects.filter(
            Q(root_object_id=OuterRef("pk")),
            ~Q(uri__startswith="https://frischmuth-dev.acdh-dev.oeaw.ac.at"),
        ).values_list("uri", flat=True)

        work_types = WorkType.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["has type"],
        ).values(
            json=JSONObject(
                id="id",
                name="name",
                name_plural="name_plural",
            )
        )

        expression_publisher = Organisation.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__name_reverse__in=["has publisher"],
        ).values(
            json=JSONObject(
                id="id",
                name="name",
            )
        )

        related_places = (
            Place.objects.all()
            .annotate(
                uris=ArraySubquery(related_uris),
            )
            .values(
                json=JSONObject(
                    id="id",
                    name="name",
                    alternative_name="alternative_name",
                    description="description",
                    longitude="longitude",
                    latitude="latitude",
                    relation_type="triple_set_from_obj__prop__name_forward",
                    uris="uris",
                )
            )
        )

        expression_places = related_places.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["is published in"],
        ).distinct()

        related_expressions = (
            Expression.objects.filter(
                triple_set_from_obj__subj_id=OuterRef("pk"),
                triple_set_from_obj__prop__name_reverse__in=["realises"],
            ).annotate(
                publisher=Subquery(expression_publisher[:1]),
                places=ArraySubquery(expression_places),
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
                place_of_publication="places",
            )
        )

        related_characters = Character.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["features"],
        ).values(
            json=JSONObject(
                id="id",
                forename="forename",
                surname="surname",
                fallback_name="fallback_name",
                relevancy="relevancy",
                fictionality="fictionality",
            )
        )

        work_places = related_places.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
        ).distinct()

        related_archive = Archive.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__name_forward__in=["holds"],
        ).values(
            json=JSONObject(
                id="id",
                name="name",
                description="description",
                location="location",
                website="website",
            )
        )

        related_physical_objects = (
            PhysicalObject.objects.filter(
                triple_set_from_subj__obj_id=OuterRef("pk"),
                triple_set_from_subj__prop__name_forward__in=["relates to"],
            )
            .annotate(archive=Subquery(related_archive))
            .values(
                json=JSONObject(
                    id="id",
                    name="name",
                    description="description",
                    vorlass_doc_reference="vorlass_doc_reference",
                    archive="archive",
                )
            )
        )

        topics = Topic.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
            triple_set_from_obj__prop__name_forward__in=["is about topic"],
        ).values(
            json=JSONObject(
                id="id",
                name="name",
                alternative_name="alternative_name",
                description="description",
                notes="notes",
            )
        )

        related_persons = (
            Person.objects.filter(
                triple_set_from_subj__obj_id=OuterRef("pk"),
                triple_set_from_subj__prop__name_forward__in=[
                    "is author of",
                    "is editor of",
                ],
            )
            .annotate(
                uris=ArraySubquery(related_uris),
            )
            .values(
                json=JSONObject(
                    id="id",
                    forename="forename",
                    surname="surname",
                    fallback_name="fallback_name",
                    relation_type="triple_set_from_subj__prop__name_reverse",
                    uris="uris",
                )
            )
        )

        forward_work_relations = Work.objects.filter(
            triple_set_from_obj__subj_id=OuterRef("pk"),
        ).values(
            json=JSONObject(
                id="id",
                title="title",
                subtitle="subtitle",
                relation_type="triple_set_from_obj__prop__name_forward",
            )
        )

        reverse_work_relations = Work.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
        ).values(
            json=JSONObject(
                id="id",
                title="title",
                subtitle="subtitle",
                relation_type="triple_set_from_subj__prop__name_reverse",
            )
        )

        works = (
            Work.objects.all()
            .annotate(
                expression_data=ArraySubquery(related_expressions),
                work_type=ArraySubquery(work_types),
                related_characters=ArraySubquery(related_characters),
                related_physical_objects=ArraySubquery(related_physical_objects),
                related_topics=ArraySubquery(topics),
                related_persons=ArraySubquery(related_persons),
                related_places=ArraySubquery(work_places),
                forward_work_relations=ArraySubquery(forward_work_relations),
                reverse_work_relations=ArraySubquery(reverse_work_relations),
            )
            .order_by("title", "subtitle")
        )
        return works


class PlaceViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint which returns Place objects by id only
    """

    serializer_class = PlaceDetailDataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        work_relations = Work.objects.filter(
            triple_set_from_subj__obj_id=OuterRef("pk"),
            triple_set_from_subj__prop__id=2,
        ).values(
            json=JSONObject(
                id="id",
                title="title",
                subtitle="subtitle",
            )
        )
        res = Place.objects.all().annotate(related_works=ArraySubquery(work_relations))
        return res
