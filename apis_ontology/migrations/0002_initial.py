# Generated by Django 4.2.7 on 2023-12-11 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("apis_metainfo", "0008_alter_rootobject_self_contenttype"),
        ("apis_ontology", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Main identifier for the data source",
                        max_length=255,
                    ),
                ),
                (
                    "file_name",
                    models.CharField(
                        blank=True,
                        help_text="Original name of the file that data originated from",
                        max_length=255,
                    ),
                ),
                (
                    "data_type",
                    models.CharField(
                        blank=True,
                        help_text="File type or data format, e.g. PDF, Excel, CSV",
                        max_length=255,
                    ),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        help_text="Original author/creator of the data",
                        max_length=255,
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        blank=True,
                        help_text="Publisher, distribution platform, data repository,...",
                        max_length=255,
                    ),
                ),
                (
                    "original_date",
                    models.DateField(
                        blank=True,
                        help_text="Date the data was created or made available",
                        null=True,
                    ),
                ),
                (
                    "added_date",
                    models.DateField(
                        blank=True,
                        help_text="Date the source was included in the project",
                        null=True,
                    ),
                ),
                (
                    "added_by",
                    models.CharField(
                        blank=True,
                        help_text="Person, user, script,... responsible for adding the data",
                        max_length=255,
                    ),
                ),
            ],
            options={
                "verbose_name": "datenquelle",
                "verbose_name_plural": "datenquellen",
            },
        ),
        migrations.CreateModel(
            name="Work",
            fields=[
                (
                    "rootobject_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="apis_metainfo.rootobject",
                    ),
                ),
                (
                    "progress_status",
                    models.CharField(
                        choices=[
                            ("created", "neu angelegt"),
                            ("edited", "reine Datenänderung"),
                            ("worked_on", "in Bearbeitung"),
                            ("awaiting_review", "Review erbeten"),
                            ("reviewed", "Review abgeschlossen"),
                            ("approved", "für VÖ freigegeben"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Bearbeitungsstatus",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Titel"
                    ),
                ),
                (
                    "subtitle",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Untertitel"
                    ),
                ),
                (
                    "siglum",
                    models.CharField(
                        blank=True, max_length=6, null=True, verbose_name="Sigle"
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="Kurzzusammenfassung",
                        max_length=1024,
                        null=True,
                        verbose_name="Teaser",
                    ),
                ),
                (
                    "text_analysis",
                    models.TextField(
                        blank=True,
                        help_text="Fließtext",
                        null=True,
                        verbose_name="Textanalyse",
                    ),
                ),
                (
                    "context",
                    models.TextField(
                        blank=True, null=True, verbose_name="Entstehungskontext"
                    ),
                ),
                (
                    "historical_events",
                    models.TextField(
                        blank=True, null=True, verbose_name="Historischer Kontext"
                    ),
                ),
                (
                    "temporal_order",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("chronological", "chronologisch"),
                            ("anachronic", "anachronisch"),
                            ("achronic", "achronisch"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Erzählordnung",
                    ),
                ),
                (
                    "temporal_duration",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("scene", "Szene"),
                            ("stretch", "Dehnung"),
                            ("summary", "Raffung"),
                            ("ellipsis", "Ellipse"),
                            ("pause", "Pause"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Dauer",
                    ),
                ),
                (
                    "temporal_frequency",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("singulative", "singulativ"),
                            ("repetitive", "repetitiv"),
                            ("iterative", "iterativ"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Frequenz",
                    ),
                ),
                (
                    "figure_speech",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("direct_quotation", "direkt zitierend"),
                            ("direct_figure_speech", "autonome, direkte Figurenrede"),
                            ("direct_speech", "direkte Rede"),
                            ("indirect_speech", "indirekte Rede"),
                            ("narrated_monologue", "erlebte Rede"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Figurenrede",
                    ),
                ),
                (
                    "representation_of_thought",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("quoted_monologue", "Zitat"),
                            ("psycho_narration", "erzählter Monolog"),
                            ("autonomous_monologue", "autonomer Monolog"),
                            ("stream_of_consciousness", "Bewusstseinsstrom"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Darstellung von Gedanken",
                    ),
                ),
                (
                    "focalization",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("zero", "Nullfokalisierung"),
                            ("internal_variable", "interne Fokalisierung – variabel"),
                            ("internal_fixed", "interne Fokalisierung – fixiert"),
                            ("external", "externe Fokalisierung"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Fokalisierung",
                    ),
                ),
                (
                    "narrative_situation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("authorial", "auktorial"),
                            ("neutral", "neutral"),
                            ("figural", "personal"),
                            ("first-person", "Ich-Erzähler*in"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Erzählperspektive",
                    ),
                ),
                (
                    "narrative_chronology",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("prior", "früheres Erzählen"),
                            ("simultaneous", "gleichzeitiges Erzählen"),
                            ("subsequent", "späteres Erzählen"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Zeitpunkt des Erzählens",
                    ),
                ),
                (
                    "narrative_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("extra", "extradiegetisch"),
                            ("intra", "intradiegetisch"),
                            ("meta", "metadiegetisch"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Ort des Erzählens",
                    ),
                ),
                (
                    "narrative_voice",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("heterodiegetic", "heterodiegetisches Erzählen"),
                            (
                                "homodiegetic_uninvolved",
                                "homodiegetisches Erzählen – unbeteiligter Beobachter:in",
                            ),
                            (
                                "homodiegetic_participant",
                                "homodiegetisches Erzählen – beteiligter Beobachter:in",
                            ),
                            (
                                "homodiegetic_character",
                                "homodiegetisches Erzählen – Nebenfigur",
                            ),
                            (
                                "homodiegetic_protagonist",
                                "homodiegetisches Erzählen – Hauptfigur",
                            ),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Stellung des:der Erzähler:in zum Geschehen",
                    ),
                ),
                (
                    "data_source",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="works",
                        to="apis_ontology.datasource",
                        verbose_name="Datenquelle",
                    ),
                ),
            ],
            options={
                "verbose_name": "werk",
                "verbose_name_plural": "werke",
                "ordering": ["title", "subtitle", "-siglum"],
            },
            bases=("apis_metainfo.rootobject", models.Model),
        ),
    ]