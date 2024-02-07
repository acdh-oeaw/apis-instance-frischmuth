# Generated by Django 4.2.10 on 2024-02-07 13:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "apis_ontology",
            "0031_rename_publication_date_expression_publication_date_iso",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="expression",
            name="publication_date_iso",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Erscheinungsdatum im ISO-Format",
            ),
        ),
    ]
