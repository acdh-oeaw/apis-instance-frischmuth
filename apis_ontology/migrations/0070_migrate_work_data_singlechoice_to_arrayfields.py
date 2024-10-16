# Generated by Django 4.2.13 on 2024-07-22 08:35

from django.db import migrations


RELEVANT_FIELDS = [
    ("temporal_order", "analysis_temporal_order"),
    ("temporal_duration", "analysis_temporal_duration"),
    ("temporal_frequency", "analysis_temporal_frequency"),
    ("figure_speech", "analysis_figure_speech"),
    ("representation_of_thought", "analysis_representation_of_thought"),
    ("focalization", "analysis_focalization"),
    ("narrative_situation", "analysis_narrative_situation"),
    ("narrative_chronology", "analysis_narrative_chronology"),
    ("narrative_level", "analysis_narrative_level"),
    ("narrative_voice", "analysis_narrative_voice"),
]


def copy_single_choice_values(apps, schema_editor):
    """
    Copy values from existing single-choice fields to ArrayFields
    meant to replace them – if they are not yet present in those ArrayFields.
    """
    VersionWork = apps.get_model("apis_ontology", "VersionWork")
    Work = apps.get_model("apis_ontology", "Work")

    for model in [Work, VersionWork]:
        for obj in model.objects.all():
            for field in RELEVANT_FIELDS:
                single_choice_val = getattr(obj, field[0], "")
                array_field_val = getattr(obj, field[1], [])

                if single_choice_val and single_choice_val not in array_field_val:
                    array_field_val.append(single_choice_val)
                    setattr(obj, field[1], array_field_val)

                    if hasattr(obj, "skip_history_when_saving"):
                        obj.skip_history_when_saving = True
                    obj.save()


def remove_array_field_values(apps, schema_editor):
    """
    Remove values from ArrayFields if they also (still) exist on the
    single-choice fields which are meant to be replaced by the ArrayFields.

    Best guess/approximation operation.
    """
    VersionWork = apps.get_model("apis_ontology", "VersionWork")
    Work = apps.get_model("apis_ontology", "Work")

    for model in [Work, VersionWork]:
        for obj in model.objects.all():
            for field in RELEVANT_FIELDS:
                single_choice_val = getattr(obj, field[0], "")
                array_field_val = getattr(obj, field[1], [])

                if array_field_val and single_choice_val:
                    try:
                        array_field_val.remove(single_choice_val)
                        setattr(obj, field[1], array_field_val)
                        if hasattr(obj, "skip_history_when_saving"):
                            obj.skip_history_when_saving = True
                        obj.save()
                    except ValueError:
                        pass


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0069_rename_language_new_expression_language_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_single_choice_values, remove_array_field_values),
    ]
