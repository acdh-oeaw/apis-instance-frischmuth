"""
Data migration to update values of representation_of_thought field of
Work entity in database to match new/modified values of RepresentationOfThought
TextChoices in models.py.
"""

# Generated by Django 4.2.15 on 2024-09-04 11:01

import logging
from functools import partial
from django.db import migrations

logger = logging.getLogger(__name__)

# list of dicts containing old and new field (string) values
REPRESENTATION_OF_THOUGHT_VALUES = [
    {
        "old": "Zitat",
        "new": "Gedankenzitat",
    },
    {
        "old": "erzählter Monolog",
        "new": "Bewusstseinsbericht",
    },
    {
        "old": "autonomer Monolog",
        "new": "innerer Monolog",
    },
]

# list of dicts which link fields whose values need updating in the database
# with the models they appear in and the values that need changing
CHOICES_FIELDS = [
    {
        "models": ["Work", "VersionWork"],
        "fields": [
            {
                "name": "representation_of_thought",
                "values": REPRESENTATION_OF_THOUGHT_VALUES,
            },
        ],
    },
]


def update_field_values(apps, schema_editor, from_key="old", to_key="new"):
    """
    Replace existing field values in the database with new values if
    they match a given string.

    Assumes affected fields contain strings (CharField, TextField,...)
    or a list of strings (ArrayField with e.g. CharField for base_field).

    :param from_key: identifier for current value in dict with new/old value pairs
    :type from_key: str
    :param to_key: identifier for replacement value in dict with new/old value pairs
    :type to_key: str
    """
    for item in CHOICES_FIELDS:
        for model in item["models"]:
            model_class = apps.get_model("apis_ontology", model)

            for obj in model_class.objects.all():
                for field in item["fields"]:
                    field_name = field["name"]
                    field_values = field["values"]

                    field_data = getattr(obj, field_name, None)

                    if field_data:
                        converted_data = field_data

                        if isinstance(field_data, str):
                            for c in field_values:
                                if field_data == c[from_key]:
                                    converted_data = c[to_key]

                        if isinstance(field_data, list):
                            converted_data = []
                            for value in field_data:
                                for c in field_values:
                                    if value == c[from_key]:
                                        value = c[to_key]
                                converted_data.append(value)

                        if converted_data != field_data:
                            setattr(obj, field_name, converted_data)

                            logger.debug(
                                f"Converted: {','.join(field_data) if isinstance(field_data, list) else field_data} "
                                f"-> {','.join(converted_data) if isinstance(converted_data, list) else converted_data} "
                                f"({model}, ID: {getattr(obj, 'id', [])})"
                            )

                            if hasattr(obj, "skip_history_when_saving"):
                                obj.skip_history_when_saving = True

                            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0083_alter_versionwork_representation_of_thought_and_more"),
    ]

    operations = [
        migrations.RunPython(
            code=update_field_values,
            reverse_code=partial(
                update_field_values,
                from_key="new",
                to_key="old",
            ),
        ),
    ]
