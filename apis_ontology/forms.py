import logging

from apis_core.generic.forms import GenericModelForm
from django import forms

from .models import Expression, Work


logger = logging.getLogger(__name__)


class WorkForm(GenericModelForm):
    analysis_temporal_order = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalOrder.choices,
        label=Work._meta.get_field("analysis_temporal_order").verbose_name,
    )
    analysis_temporal_duration = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalDuration.choices,
        label=Work._meta.get_field("analysis_temporal_duration").verbose_name,
    )
    analysis_temporal_frequency = forms.MultipleChoiceField(
        required=False,
        choices=Work.TemporalFrequency.choices,
        label=Work._meta.get_field("analysis_temporal_frequency").verbose_name,
    )
    analysis_figure_speech = forms.MultipleChoiceField(
        required=False,
        choices=Work.FigureSpeech.choices,
        label=Work._meta.get_field("analysis_figure_speech").verbose_name,
    )
    analysis_representation_of_thought = forms.MultipleChoiceField(
        required=False,
        choices=Work.RepresentationOfThought.choices,
        label=Work._meta.get_field("analysis_representation_of_thought").verbose_name,
    )
    analysis_focalization = forms.MultipleChoiceField(
        required=False,
        choices=Work.Focalization.choices,
        label=Work._meta.get_field("analysis_focalization").verbose_name,
    )
    analysis_narrative_situation = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeSituation.choices,
        label=Work._meta.get_field("analysis_narrative_situation").verbose_name,
    )
    analysis_narrative_chronology = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeChronology.choices,
        label=Work._meta.get_field("analysis_narrative_chronology").verbose_name,
    )
    analysis_narrative_level = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeLevel.choices,
        label=Work._meta.get_field("analysis_narrative_level").verbose_name,
    )
    analysis_narrative_voice = forms.MultipleChoiceField(
        required=False,
        choices=Work.NarrativeVoice.choices,
        label=Work._meta.get_field("analysis_narrative_voice").verbose_name,
    )


class ExpressionForm(GenericModelForm):
    language_new = forms.MultipleChoiceField(
        required=False,
        choices=Expression.LanguagesIso6393.choices,
        label=Expression._meta.get_field("language_new").verbose_name,
    )
