# Generated by Django 4.2.9 on 2024-01-19 13:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0023_character_fictionality"),
    ]

    operations = [
        migrations.RenameField(
            model_name="expression",
            old_name="year_of_publication",
            new_name="publication_date",
        ),
    ]
