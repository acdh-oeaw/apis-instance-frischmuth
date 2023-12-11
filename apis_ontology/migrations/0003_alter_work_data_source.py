# Generated by Django 4.2.7 on 2023-12-11 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="work",
            name="data_source",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="works",
                to="apis_ontology.datasource",
                verbose_name="Datenquelle",
            ),
        ),
    ]