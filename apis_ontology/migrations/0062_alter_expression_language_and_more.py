# Generated by Django 4.2.13 on 2024-06-27 07:20

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0061_postgres_extensions_trigram_unaccent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expression",
            name="language",
            field=multiselectfield.db.fields.MultiSelectField(
                blank=True,
                choices=[
                    ("deu", "Deutsch"),
                    ("eng", "Englisch"),
                    ("fra", "Französisch"),
                    ("ita", "Italienisch"),
                ],
                default="",
                max_length=255,
                verbose_name="Sprache",
            ),
        ),
        migrations.AlterField(
            model_name="versionexpression",
            name="language",
            field=multiselectfield.db.fields.MultiSelectField(
                blank=True,
                choices=[
                    ("deu", "Deutsch"),
                    ("eng", "Englisch"),
                    ("fra", "Französisch"),
                    ("ita", "Italienisch"),
                ],
                default="",
                max_length=255,
                verbose_name="Sprache",
            ),
        ),
        migrations.AlterField(
            model_name="versionwork",
            name="language",
            field=multiselectfield.db.fields.MultiSelectField(
                blank=True,
                choices=[
                    ("deu", "Deutsch"),
                    ("eng", "Englisch"),
                    ("fra", "Französisch"),
                    ("ita", "Italienisch"),
                ],
                default="",
                max_length=255,
                verbose_name="Sprache",
            ),
        ),
        migrations.AlterField(
            model_name="work",
            name="language",
            field=multiselectfield.db.fields.MultiSelectField(
                blank=True,
                choices=[
                    ("deu", "Deutsch"),
                    ("eng", "Englisch"),
                    ("fra", "Französisch"),
                    ("ita", "Italienisch"),
                ],
                default="",
                max_length=255,
                verbose_name="Sprache",
            ),
        ),
    ]
