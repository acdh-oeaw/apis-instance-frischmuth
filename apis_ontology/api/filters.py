"""
Filters for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

import logging

import django_filters
from django.utils.translation import gettext_lazy as _

from apis_ontology.filtersets import fuzzy_search_unaccent_trigram
from apis_ontology.models import Expression, Topic, WorkType


logger = logging.getLogger(__name__)


class MultipleChoiceOverlap(django_filters.MultipleChoiceFilter):
    def filter(self, qs, value):
        if len(value) == 0:
            return qs
        filter = {f"{self.field_name}__overlap": value}
        return qs.filter(**filter)


class WorkPreviewSearchFilter(django_filters.FilterSet):
    text_filter = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        label=_(
            "String to find in work titles and subtitles using fuzzy search (unaccent-ed trigram word similarity)."
        ),
        method=fuzzy_search_unaccent_trigram,
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
        choices=Topic.objects.all().values_list("name", "name"),
    )
    facet_work_type = MultipleChoiceOverlap(
        field_name="work_type_names",
        label=_("Type of the work."),
        lookup_expr="overlap",
        choices=WorkType.objects.all().values_list("name", "name"),
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
