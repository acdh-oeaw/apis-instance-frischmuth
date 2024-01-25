import logging
import re

import django_filters
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _


PATTERN = re.compile(r"""((?:[^ "']|"[^"]*"|'[^']*')+)""")


logger = logging.getLogger(__name__)


def remove_quotes(token):
    return token.strip('"')


def trigram_search_filter_person(queryset, fields, value):
    return trigram_search_filter(
        queryset,
        [
            "forename",
            "surname",
            "fallback_name",
            "alternative_name",
        ],
        value,
    )


def trigram_search_filter(queryset, fields, value):
    tokens = PATTERN.split(value)
    tokens = list(filter(str.strip, tokens))
    tokens = set(list(map(remove_quotes, tokens)) + [value])
    trig_vector_list = []
    for token in tokens:
        for field in fields:
            trig_vector_list.append(TrigramWordSimilarity(token, field))
    trig_vector = Greatest(*trig_vector_list, None)
    return (
        queryset.annotate(similarity=trig_vector)
        .filter(similarity__gt=0.4)
        .order_by("-similarity")
    )


class PersonFilterSet(AbstractEntityFilterSet):
    search = django_filters.CharFilter(
        method=trigram_search_filter_person,
        label=_("Suche"),
        help_text=_("Suche in allen Namensfeldern von Personen"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.move_to_end("search", False)
