# Generated by Django 4.2.10 on 2024-02-08 13:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0033_expression_publication_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expression",
            name="publication_date_iso",
            field=models.DateField(
                blank=True,
                editable=False,
                help_text="Format YYYY-MM-DD",
                null=True,
                verbose_name="Erscheinungsdatum (ISO 8601)",
            ),
        ),
    ]
