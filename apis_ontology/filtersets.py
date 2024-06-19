import logging
import re
from unicodedata import combining, normalize

import django_filters
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
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


def tokenize_search_string(search_string, diacritics=True):
    """
    :param search_string: user-provided search string
    :param diacritics: whether to retain or remove diacritics from search
                       string(s) during tokenization; defaults to keeping them
    :return a list of strings
    """
    tokens = PATTERN.split(search_string)
    tokens = list(filter(str.strip, tokens))
    tokens = set(list(map(remove_quotes, tokens)) + [search_string])
    if not diacritics:
        tokens = map(remove_diacritics, tokens)
    return tokens


def trigram_search_filter(queryset, fields, value):
    """
    Look up a list of search terms in given fields of a model
    using trigram word similarity lookups.

    Note that this function currently does not check the passed fields'
    type, but trigram lookups only work on string-based fields (CharField,
    TextField).

    :param queryset: initial queryset
    :param fields: model fields which should be looked up
    :param value: user-provided search string
    :return: a queryset
    """
    tokens = tokenize_search_string(value)
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


class TitlesMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        help_text=_("Suche in allen Titelfeldern"),
        label=_("Suche: Titel"),
        method=trigram_search_filter,
    )


class AlternativeNameMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "name",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=trigram_search_filter,
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
        method=trigram_search_filter,
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
        method=trigram_search_filter,
    )
