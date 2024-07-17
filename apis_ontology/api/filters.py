"""
Filters for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

import logging

import django_filters
from django.utils.translation import gettext_lazy as _

from apis_ontology.filtersets import fuzzy_search_unaccent_trigram


logger = logging.getLogger(__name__)


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
    facet_language = django_filters.CharFilter(
        field_name="triple_set_from_subj__obj__expression__language",
        label=_("Language of the expression."),
        lookup_expr="contains",
    )
