# Generated by Django 4.2.11 on 2024-04-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "apis_ontology",
            "0055_alter_expression_publication_date_iso_formatted_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="researchperspective",
            name="notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Feld für interne Notizen",
                max_length=1024,
                verbose_name="Notiz",
            ),
        ),
        migrations.AddField(
            model_name="topic",
            name="notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Feld für interne Notizen",
                max_length=1024,
                verbose_name="Notiz",
            ),
        ),
    ]