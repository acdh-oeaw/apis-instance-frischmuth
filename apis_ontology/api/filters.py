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
    search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        label=_("Suche"),
        method=fuzzy_search_unaccent_trigram,
    )
