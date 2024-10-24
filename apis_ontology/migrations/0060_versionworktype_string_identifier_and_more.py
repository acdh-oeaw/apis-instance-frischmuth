# Generated by Django 4.2.13 on 2024-05-28 16:45

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0059_versionworktype_versionwork_versiontopic_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="versionworktype",
            name="string_identifier",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Zeichenfolge aus Buchstaben und Unterstrichen",
                max_length=50,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="englischsprachiger Identifier",
            ),
        ),
        migrations.AddField(
            model_name="worktype",
            name="string_identifier",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Zeichenfolge aus Buchstaben und Unterstrichen",
                max_length=50,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="englischsprachiger Identifier",
            ),
        ),
    ]
