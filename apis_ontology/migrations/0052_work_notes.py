# Generated by Django 4.2.11 on 2024-04-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0051_alter_expression_issue"),
    ]

    operations = [
        migrations.AddField(
            model_name="work",
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
