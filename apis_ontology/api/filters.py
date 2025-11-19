"""
Filters for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

import logging

import django_filters
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import Func, Q
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _

from apis_ontology.models import Expression, Topic, WorkType


logger = logging.getLogger(__name__)


class MultipleChoiceOverlap(django_filters.MultipleChoiceFilter):
    def filter(self, qs, value):
        if len(value) == 0:
            return qs
        filter = {f"{self.field_name}__overlap": value}
        return qs.filter(**filter)


class WebSearchQuery(Func):
    function = "websearch_to_tsquery"
    template = "%(function)s('%(config)s', %(expressions)s)"


class WorkPreviewSearchFilter(django_filters.FilterSet):
    text_filter = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        label=_(
            "String to find in work titles and subtitles using fuzzy search (unaccent-ed trigram word similarity)."
        ),
        method="filter_search",
    )
    facet_language = MultipleChoiceOverlap(
        field_name="facet_language",
        label=_("Language of the expression."),
        lookup_expr="overlap",
        choices=Expression.LanguagesIso6393.choices,
    )
    facet_topic = MultipleChoiceOverlap(
        field_name="facet_topic",
        label=_("Topic of the expression."),
        lookup_expr="overlap",
        choices=[(x[0], x[0]) for x in Topic.objects.all().values_list("name")],
    )
    facet_work_type = MultipleChoiceOverlap(
        field_name="work_type_names",
        label=_("Type of the work."),
        lookup_expr="overlap",
        choices=[(x[0], x[0]) for x in WorkType.objects.all().values_list("name")],
    )
    start_year = django_filters.NumberFilter(
        field_name="min_year",
        label=_("Start year for publication date of expressions (inclusive)"),
        lookup_expr="gte",
    )
    end_year = django_filters.NumberFilter(
        field_name="max_year",
        label=_("End year for publication date of expressions (inclusive)"),
        lookup_expr="lte",
    )
    primary_works = django_filters.BooleanFilter(
        field_name="primary_works",
        method="filter_primary_works",
        label=_("Filter for primary works only"),
    )
    secondary_works = django_filters.BooleanFilter(
        field_name="secondary_works",
        method="filter_primary_works",
        label=_("Filter for secondary works only"),
    )

    def filter_search(self, queryset, name, value):
        search_vector = (
            SearchVector("title", weight="A", config="german")
            + SearchVector(
                "subtitle", "facet_topic", "authors", weight="B", config="german"
            )
            + SearchVector("title", "subtitle", "facet_topic", "authors", weight="C")
        )  # Combine fields for search
        search_query = SearchQuery(
            value,
            search_type="websearch",
        )  # Search term
        results = (
            queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                similarity_title=TrigramSimilarity("title", value),
                similarity_subtitle=TrigramSimilarity("subtitle", value),
                similarity=Greatest(
                    "similarity_title",
                    "similarity_subtitle",
                ),
            )
            .filter(Q(search=search_query) | Q(similarity__gte=0.3))
            .order_by("-rank")
        )
        return results

    def filter_primary_works(self, queryset, name, value):
        if name == "secondary_works":
            value = not value
        return queryset.filter(primary_work=value)
