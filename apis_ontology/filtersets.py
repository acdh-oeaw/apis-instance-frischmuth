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


class GenericSearchFilterSet(AbstractEntityFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "search" in self.filters:
            self.filters.move_to_end("search", False)


class PersonNameMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "surname",
            "forename",
            "fallback_name",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=trigram_search_filter,
    )


class PersonFilterSet(PersonNameMixinFilterSet):
    pass
