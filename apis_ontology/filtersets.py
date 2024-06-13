import logging
import re
from unicodedata import combining, normalize

import django_filters
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django.contrib.postgres.lookups import Unaccent
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _


PATTERN = re.compile(r"""((?:[^ "']|"[^"]*"|'[^']*')+)""")


logger = logging.getLogger(__name__)


def remove_quotes(token):
    return token.strip('"')


def remove_diacritics(token):
    """
    Remove diacritics from strings by merging them into their preceding
    unicode characters.
    See https://stackoverflow.com/a/517974/
    """
    normalized = normalize("NFKD", token)
    return "".join([c for c in normalized if not combining(c)])


def trigram_unaccent_search_filter(queryset, fields, value):
    tokens = PATTERN.split(value)
    tokens = list(filter(str.strip, tokens))
    tokens = set(list(map(remove_quotes, tokens)) + [value])
    trig_vector_list = []
    for token in tokens:
        for field in fields:
            trig_vector_list.append(
                TrigramWordSimilarity(remove_diacritics(token), Unaccent(field))
            )
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
        method=trigram_unaccent_search_filter,
    )


class TitlesMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        help_text=_("Suche in allen Titelfeldern"),
        label=_("Suche: Titel"),
        method=trigram_unaccent_search_filter,
    )


class AlternativeNameMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "name",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=trigram_unaccent_search_filter,
    )


class PersonFilterSet(PersonNameMixinFilterSet):
    pass


class CharacterFilterSet(PersonNameMixinFilterSet):
    pass


class WorkFilterSet(TitlesMixinFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
            "siglum",
        ],
        help_text=_("Suche in allen Titelfeldern und Siglum"),
        label=_("Suche: Titel, Siglum"),
        method=trigram_unaccent_search_filter,
    )


class ExpressionFilterSet(TitlesMixinFilterSet):
    pass


class OrganisationFilterSet(AlternativeNameMixinFilterSet):
    pass


class PlaceFilterSet(AlternativeNameMixinFilterSet):
    pass


class ResearchPerspectiveFilterSet(AlternativeNameMixinFilterSet):
    pass


class TopicFilterSet(AlternativeNameMixinFilterSet):
    pass


class WorkTypeFilterSet(AlternativeNameMixinFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "name",
            "name_plural",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=trigram_unaccent_search_filter,
    )
