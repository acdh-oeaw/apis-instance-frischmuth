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
from django_filters.widgets import CSVWidget, RangeWidget

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


class BaseEntityFilterSet(AbstractEntityFilterSet):
    """
    Parent class for all entity model classes.
    """

    class Meta(AbstractEntityFilterSet.Meta):
        exclude = [
            f for f in AbstractEntityFilterSet.Meta.exclude if f != "notes"
        ]  # TODO remove once "notes" isn't a default field of relations anymore
        filter_overrides = {
            **AbstractEntityFilterSet.Meta.filter_overrides,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "custom_search" in self.filters:
            self.filters.move_to_end("custom_search", False)


class LanguageMixinFilter(django_filters.FilterSet):
    """
    Filter (multiple) language choices defined in models.
    """

    language = django_filters.MultipleChoiceFilter(
        choices=LanguageMixin.LanguagesIso6393.choices,
        lookup_expr="icontains",
    )


class TitlesSearch(django_filters.FilterSet):
    """
    Search within title and subtitle fields.
    """

    custom_search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
        ],
        help_text=_("Suche in allen Titelfeldern"),
        label=_("Suche: Titel"),
        method=fuzzy_search_unaccent_trigram,
    )


class AlternativeNameSearch(django_filters.FilterSet):
    """
    Search within name and alternative_name fields.

    With the exception of person-like entities (whose names are more complex),
    the existence of the latter is assumed to be predicated on the former,
    i.e. an entity cannot have an "alternative_name" without a "name".
    """

    custom_search = django_filters.CharFilter(
        field_name=[
            "name",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=fuzzy_search_unaccent_trigram,
    )


class PersonSearch(django_filters.FilterSet):
    """
    Search within the various name fields used for persons and person-like
    entities (like characters).
    """

    custom_search = django_filters.CharFilter(
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


class PersonFilterSet(BaseEntityFilterSet, PersonSearch):
    pass


class VersionPersonFilterSet(PersonFilterSet):
    pass


class CharacterFilterSet(BaseEntityFilterSet, PersonSearch):
    fictionality = django_filters.MultipleChoiceFilter(
        choices=Character.CharacterFictionality.choices,
        lookup_expr="icontains",
    )


class VersionCharacterFilterSet(CharacterFilterSet):
    pass


class MetaCharacterFilterSet(BaseEntityFilterSet):
    pass


class VersionMetaCharacterFilterSet(MetaCharacterFilterSet):
    pass


class WorkFilterSet(BaseEntityFilterSet, LanguageMixinFilter, TitlesSearch):
    custom_search = django_filters.CharFilter(
        field_name=[
            "title",
            "subtitle",
            "siglum",
        ],
        help_text=_("Suche in allen Titelfeldern und Siglum"),
        label=_("Suche: Titel, Siglum"),
        method=fuzzy_search_unaccent_trigram,
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


class VersionWorkFilterSet(WorkFilterSet):
    pass


class ExpressionFilterSet(BaseEntityFilterSet, LanguageMixinFilter, TitlesSearch):
    edition_type = django_filters.MultipleChoiceFilter(
        choices=Expression.EditionTypes.choices,
        lookup_expr="icontains",
    )

    page_count = django_filters.RangeFilter(
        widget=CSVWidget(
            attrs={
                "placeholder": "50,150",
            },
        ),
        help_text="Suche innerhalb eines Seitenbereichs. Eingabe in Form von "
        "zwei durch Komma getrennte Zahlen bzw. einer einzelnen Zahl "
        "als Untergrenze.",
    )
    publication_date_iso_formatted = django_filters.DateFromToRangeFilter(
        widget=RangeWidget(
            attrs={
                "placeholder": "DD.MM.YYYY",
            },
        ),
        help_text="Suche innerhalb eines Zeitraums. Eingabe im Format "
        "DD.MM.YYYY bzw. YYYY-MM-DD. Wird nur ein Feld ausgefüllt, "
        "wird dieses Datum als Beginn bzw. Ende des Zeitraums angenommen.",
    )


class VersionExpressionFilterSet(ExpressionFilterSet):
    pass


class WorkTypeFilterSet(BaseEntityFilterSet, AlternativeNameSearch):
    custom_search = django_filters.CharFilter(
        field_name=[
            "name",
            "name_plural",
            "alternative_name",
        ],
        help_text=_("Suche in allen Namensfeldern"),
        label=_("Suche: Namen"),
        method=fuzzy_search_unaccent_trigram,
    )


class VersionWorkTypeFilterSet(WorkTypeFilterSet):
    pass


class OrganisationFilterSet(BaseEntityFilterSet, AlternativeNameSearch):
    pass


class VersionOrganisationFilterSet(OrganisationFilterSet):
    pass


class PlaceFilterSet(BaseEntityFilterSet, AlternativeNameSearch):
    pass


class VersionPlaceFilterSet(PlaceFilterSet):
    pass


class ResearchPerspectiveFilterSet(BaseEntityFilterSet, AlternativeNameSearch):
    pass


class VersionResearchPerspectiveFilterSet(ResearchPerspectiveFilterSet):
    pass


class TopicFilterSet(BaseEntityFilterSet, AlternativeNameSearch):
    pass


class VersionTopicFilterSet(TopicFilterSet):
    pass


class InterpretatemFilterSet(BaseEntityFilterSet):
    pass


class VersionInterpretatemFilterSet(InterpretatemFilterSet):
    pass


class ArchiveFilterSet(BaseEntityFilterSet):
    pass


class VersionArchiveFilterSet(ArchiveFilterSet):
    pass


class PhysicalObjectFilterSet(BaseEntityFilterSet):
    pass


class VersionPhysicalObjectFilterSet(PhysicalObjectFilterSet):
    pass
