import logging

from apis_core.generic.forms import GenericModelForm
from django import forms

from .models import Character, Expression, Work


logger = logging.getLogger(__name__)


class WorkForm(GenericModelForm):
    temporal_order = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalOrder.choices,
        label=Work._meta.get_field("temporal_order").verbose_name,
    )
    temporal_duration = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalDuration.choices,
        label=Work._meta.get_field("temporal_duration").verbose_name,
    )
    temporal_frequency = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalFrequency.choices,
        label=Work._meta.get_field("temporal_frequency").verbose_name,
    )
    figure_speech = forms.MultipleChoiceField(
        required=False,
        choices=Work.FigureSpeech.choices,
        label=Work._meta.get_field("figure_speech").verbose_name,
    )
    representation_of_thought = forms.MultipleChoiceField(
        required=False,
        choices=Work.RepresentationOfThought.choices,
        label=Work._meta.get_field("representation_of_thought").verbose_name,
    )
    focalization = forms.MultipleChoiceField(
        required=False,
        choices=Work.Focalization.choices,
        label=Work._meta.get_field("focalization").verbose_name,
    )
    narrative_situation = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeSituation.choices,
        label=Work._meta.get_field("narrative_situation").verbose_name,
    )
    narrative_chronology = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeChronology.choices,
        label=Work._meta.get_field("narrative_chronology").verbose_name,
    )
    narrative_level = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeLevel.choices,
        label=Work._meta.get_field("narrative_level").verbose_name,
    )
    narrative_voice = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeVoice.choices,
        label=Work._meta.get_field("narrative_voice").verbose_name,
    )
    language = forms.MultipleChoiceField(
        required=False,
        choices=Expression.LanguagesIso6393.choices,
        label=Expression._meta.get_field("language").verbose_name,
    )


class ExpressionForm(GenericModelForm):
    new_edition_type = forms.MultipleChoiceField(
        required=False,
        choices=Expression.EditionTypes.choices,
        label=Expression._meta.get_field("new_edition_type").verbose_name,
    )
    language = forms.MultipleChoiceField(
        required=False,
        choices=Expression.LanguagesIso6393.choices,
        label=Expression._meta.get_field("language").verbose_name,
    )


class CharacterForm(GenericModelForm):
    new_fictionality = forms.MultipleChoiceField(
        required=False,
        choices=Character.CharacterFictionality.choices,
        label=Character._meta.get_field("new_fictionality").verbose_name,
    )
