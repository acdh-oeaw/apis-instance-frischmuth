import logging

from apis_core.generic.forms import GenericModelForm
from django import forms

from .models import Character, Expression, LanguageMixin, Work


logger = logging.getLogger(__name__)


class LanguageForm(forms.Form):
    language = forms.MultipleChoiceField(
        required=False,
        choices=LanguageMixin.LanguagesIso6393.choices,
        label=LanguageMixin._meta.get_field("language").verbose_name,
    )


class WorkForm(GenericModelForm, LanguageForm):
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


class ExpressionForm(GenericModelForm, LanguageForm):
    edition_type = forms.MultipleChoiceField(
        required=False,
        choices=Expression.EditionTypes.choices,
        label=Expression._meta.get_field("edition_type").verbose_name,
        help_text=Expression._meta.get_field("edition_type").help_text,
    )


class CharacterForm(GenericModelForm):
    fictionality = forms.MultipleChoiceField(
        required=False,
        choices=Character.CharacterFictionality.choices,
        label=Character._meta.get_field("fictionality").verbose_name,
        help_text=Character._meta.get_field("fictionality").help_text,
    )
