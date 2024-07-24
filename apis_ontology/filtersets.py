import logging
import re
from unicodedata import combining, normalize

import django_filters
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.lookups import Unaccent
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _

from .models import Character, Expression, LanguageMixin, Work


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


def trigram_search_filter(queryset, fields, tokens):
    """
    Look up a list of search terms in given fields of a model
    using trigram word similarity lookups.

    Note that this function currently does not check the passed fields'
    type, but trigram lookups only work on string-based fields (CharField,
    TextField).

    :param queryset: initial queryset
    :param fields: model fields which should be looked up
    :param tokens: a list of search strings
    :return: a queryset
    """
    trig_vector_list = []
    for token in tokens:
        for field in fields:
            trig_vector_list.append(TrigramWordSimilarity(token, field))
    trig_vector = Greatest(*trig_vector_list, None)
    return (
        queryset.annotate(similarity=trig_vector)
        .filter(similarity__gt=0.7)
        .order_by("-similarity")
    )


def fuzzy_search_trigram(queryset, fields, value):
    """
    Search across model fields using trigram search.

    :param queryset: input queryset
    :param fields: model fields which should be looked up
    :param value: user-provided search string
    :return: a queryset
    """
    tokens = tokenize_search_string(value)
    return trigram_search_filter(queryset, fields, tokens)


def fuzzy_search_unaccent_trigram(queryset, fields, value):
    """
    Search across model fields using trigram search with unaccent
    lookups and with diacritics removed from search strings.

    :param queryset: input queryset
    :param fields: model fields which should be looked up
    :param value: user-provided search string
    :return: a queryset
    """
    fields = [Unaccent(f) for f in fields]
    tokens = tokenize_search_string(value, diacritics=False)
    return trigram_search_filter(queryset, fields, tokens)


class GenericSearchFilterSet(AbstractEntityFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "search" in self.filters:
            self.filters.move_to_end("search", False)


class TitlesMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        help_text=_("Suche in allen Titelfeldern"),
        label=_("Suche: Titel"),
        method=fuzzy_search_unaccent_trigram,
    )


class AlternativeNameMixinFilterSet(GenericSearchFilterSet):
    search = django_filters.CharFilter(
        field_name=[
            "name",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=fuzzy_search_unaccent_trigram,
    )


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
        method=fuzzy_search_unaccent_trigram,
    )


class PersonFilterSet(PersonNameMixinFilterSet):
    pass


class CharacterFilterSet(PersonNameMixinFilterSet):
    new_fictionality = django_filters.MultipleChoiceFilter(
        choices=Character.CharacterFictionality.choices,
        lookup_expr="icontains",
    )

    class Meta(PersonNameMixinFilterSet.Meta):
        fields = {
            "new_fictionality": ["icontains"],
        }
        filter_overrides = {
            ArrayField: {
                "filter_class": django_filters.MultipleChoiceFilter,
                # "extra" attribute not working for fields with choices, see:
                # https://github.com/carltongibson/django-filter/issues/1475
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                    "widget": forms.SelectMultiple,
                },
            },
        }


class VersionCharacterFilterSet(CharacterFilterSet):
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
        method=fuzzy_search_unaccent_trigram,
    )

    language = django_filters.MultipleChoiceFilter(
        choices=LanguageMixin.LanguagesIso6393.choices,
        lookup_expr="icontains",
    )

    temporal_order = django_filters.MultipleChoiceFilter(
        choices=Work.TemporalOrder.choices,
        lookup_expr="icontains",
    )
    temporal_duration = django_filters.MultipleChoiceFilter(
        choices=Work.TemporalDuration.choices,
        lookup_expr="icontains",
    )
    temporal_frequency = django_filters.MultipleChoiceFilter(
        choices=Work.TemporalFrequency.choices,
        lookup_expr="icontains",
    )
    figure_speech = django_filters.MultipleChoiceFilter(
        choices=Work.FigureSpeech.choices,
        lookup_expr="icontains",
    )
    representation_of_thought = django_filters.MultipleChoiceFilter(
        choices=Work.RepresentationOfThought.choices,
        lookup_expr="icontains",
    )
    focalization = django_filters.MultipleChoiceFilter(
        choices=Work.Focalization.choices,
        lookup_expr="icontains",
    )
    narrative_situation = django_filters.MultipleChoiceFilter(
        choices=Work.NarrativeSituation.choices,
        lookup_expr="icontains",
    )
    narrative_chronology = django_filters.MultipleChoiceFilter(
        choices=Work.NarrativeChronology.choices,
        lookup_expr="icontains",
    )
    narrative_level = django_filters.MultipleChoiceFilter(
        choices=Work.NarrativeLevel.choices,
        lookup_expr="icontains",
    )
    narrative_voice = django_filters.MultipleChoiceFilter(
        choices=Work.NarrativeVoice.choices,
        lookup_expr="icontains",
    )

    class Meta(TitlesMixinFilterSet.Meta):
        fields = {
            "temporal_order": ["icontains"],
        }
        filter_overrides = {
            ArrayField: {
                "filter_class": django_filters.MultipleChoiceFilter,
                # "extra" attribute not working for fields with choices, see:
                # https://github.com/carltongibson/django-filter/issues/1475
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                    "widget": forms.SelectMultiple,
                },
            },
        }


class VersionWorkFilterSet(WorkFilterSet):
    pass


class ExpressionFilterSet(TitlesMixinFilterSet):
    new_edition_type = django_filters.MultipleChoiceFilter(
        choices=Expression.EditionTypes.choices,
        lookup_expr="icontains",
    )

    language = django_filters.MultipleChoiceFilter(
        choices=LanguageMixin.LanguagesIso6393.choices,
        lookup_expr="icontains",
    )

    class Meta(TitlesMixinFilterSet.Meta):
        fields = {
            "language": ["icontains"],
        }
        filter_overrides = {
            ArrayField: {
                "filter_class": django_filters.MultipleChoiceFilter,
                # "extra" attribute not working for fields with choices, see:
                # https://github.com/carltongibson/django-filter/issues/1475
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                    "widget": forms.SelectMultiple,
                },
            },
        }


class VersionExpressionFilterSet(ExpressionFilterSet):
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
        method=fuzzy_search_unaccent_trigram,
    )
