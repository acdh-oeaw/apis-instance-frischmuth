# Generated by Django 4.2.13 on 2024-07-22 10:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0071_remove_versionwork_figure_speech_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_figure_speech",
            new_name="figure_speech",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_focalization",
            new_name="focalization",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_narrative_chronology",
            new_name="narrative_chronology",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_narrative_level",
            new_name="narrative_level",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_narrative_situation",
            new_name="narrative_situation",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_narrative_voice",
            new_name="narrative_voice",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_representation_of_thought",
            new_name="representation_of_thought",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_temporal_duration",
            new_name="temporal_duration",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_temporal_frequency",
            new_name="temporal_frequency",
        ),
        migrations.RenameField(
            model_name="versionwork",
            old_name="analysis_temporal_order",
            new_name="temporal_order",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_figure_speech",
            new_name="figure_speech",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_focalization",
            new_name="focalization",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_narrative_chronology",
            new_name="narrative_chronology",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_narrative_level",
            new_name="narrative_level",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_narrative_situation",
            new_name="narrative_situation",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_narrative_voice",
            new_name="narrative_voice",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_representation_of_thought",
            new_name="representation_of_thought",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_temporal_duration",
            new_name="temporal_duration",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_temporal_frequency",
            new_name="temporal_frequency",
        ),
        migrations.RenameField(
            model_name="work",
            old_name="analysis_temporal_order",
            new_name="temporal_order",
        ),
    ]
