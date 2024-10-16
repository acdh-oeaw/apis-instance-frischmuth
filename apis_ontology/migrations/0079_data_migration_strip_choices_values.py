"""
Data migration to strip TextChoices values in ArrayFields in database
of whitespace.
"""

# Generated by Django 4.2.15 on 2024-09-02 14:23

import logging
from django.db import migrations

logger = logging.getLogger(__name__)


# list of ArrayFields in models based on (Text)Choices
ARRAY_FIELDS_CHOICES = [
    {
        "models": ["Work", "VersionWork"],
        "fields": [
            "temporal_order",
            "temporal_duration",
            "temporal_frequency",
            "figure_speech",
            "representation_of_thought",
            "focalization",
            "narrative_situation",
            "narrative_chronology",
            "narrative_level",
            "narrative_voice",
        ],
    },
    {
        "models": ["Expression", "VersionExpression"],
        "fields": [
            "edition_type",
        ],
    },
    {
        "models": ["Character", "VersionCharacter"],
        "fields": [
            "fictionality",
        ],
    },
]


def remove_whitespace(apps, schema_editor):
    """
    Remove redundant leading/trailing whitespace from ArrayField values.

    Assumes all affected fields are ArrayFields with CharFields for base_field,
    i.e. contain a list of (string) values.
    """
    for item in ARRAY_FIELDS_CHOICES:
        for model in item["models"]:
            model_class = apps.get_model("apis_ontology", model)
            for obj in model_class.objects.all():
                for field in item["fields"]:
                    values = getattr(obj, field, [])

                    if values:
                        stripped = [v.strip() for v in values]
                        if stripped != values:
                            logger.debug(
                                f"Stripped whitespace: {','.join(values)} -> {','.join(stripped)} ({model} ID: {getattr(obj, 'id', [])})"
                            )

                            setattr(obj, field, stripped)

                            if hasattr(obj, "skip_history_when_saving"):
                                obj.skip_history_when_saving = True
                            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        (
            "apis_ontology",
            "0078_rename_new_fictionality_character_fictionality_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=remove_whitespace,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
