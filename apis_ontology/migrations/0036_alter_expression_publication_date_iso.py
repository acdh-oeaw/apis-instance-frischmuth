# Generated by Django 4.2.10 on 2024-02-12 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0035_alter_expression_relevant_pages"),
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
                verbose_name="Erscheinungsdatum (ISO)",
            ),
        ),
    ]
