import reversion
from apis_core.apis_entities.models import AbstractEntity
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


@reversion.register
class StatusMixin(models.Model):
    class ProgressStates(models.TextChoices):
        CREATED = "created", _("neu angelegt")
        MINOR_EDITS = "edited", _("reine Datenänderung")
        NEEDS_DATA_CHECK = "verify_data", _("dubios")
        WORK_IN_PROGRESS = "worked_on", _("in Bearbeitung")
        NEEDS_REVIEW = "awaiting_review", _("Review erbeten")
        HAS_REVIEW = "reviewed", _("Review abgeschlossen")
        READY_FOR_RELEASE = "approved", _("für VÖ freigegeben")

    progress_status = models.CharField(
        max_length=255,
        choices=ProgressStates.choices,
        null=True,
        blank=True,
        verbose_name=_("Bearbeitungsstatus"),
    )

    class Meta:
        abstract = True
        verbose_name = _("progress state")
        verbose_name_plural = _("progress states")


@reversion.register
class AlternativeNameMixin(models.Model):
    """
    Mixin for "alternative_name" field shared between entities.
    """

    alternative_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Alternativer Name"),
    )

    class Meta:
        abstract = True


class NameMixin(models.Model):
    """
    Mixin for "name" field shared between entities.
    """

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


@reversion.register
class DescriptionMixin(models.Model):
    """
    Mixin for "description" field shared between entities.
    """

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Beschreibung"),
    )

    class Meta:
        abstract = True


@reversion.register
class HumanBeingMixin(AlternativeNameMixin, models.Model):
    """
    Mixin for fields shared between person-like entities.
    """

    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Vorname"),
    )

    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Nachname"),
    )

    class Meta:
        abstract = True


@reversion.register
class WorkMixin(models.Model):
    """
    Mixin for fields shared between work-like entities.
    """

    title = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Titel")
    )

    subtitle = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Untertitel")
    )

    class Meta:
        abstract = True


@reversion.register
class DataSource(models.Model):
    """
    Holds (meta) information about data sources.
    Used to identify e.g. imports from Zotero or Excel.
    """

    name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Main identifier for the data source"),
    )

    file_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Original name of the file that data originated from"),
    )

    data_type = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("File type or data format, e.g. PDF, Excel, CSV"),
    )

    author = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Original author/creator of the data"),
    )

    provider = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Publisher, distribution platform, data repository,..."),
    )

    original_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date the data was created or made available"),
    )

    added_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date the source was included in the project"),
    )

    added_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Person, user, script,... responsible for adding the data"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("datenquelle")
        verbose_name_plural = _("datenquellen")


@reversion.register(follow=["rootobject_ptr"])
class Work(WorkMixin, StatusMixin, AbstractEntity):
    """
    The abstract notion of an intellectual creation, irrespective
    of its exact transmitted version, language or other form.
    """

    # choices for narrative analysis fields
    class TemporalOrder(models.TextChoices):
        CHRONOLOGICAL = "chronological", _("chronologisch")
        ANACHRONICAL = "anachronic", _("anachronisch")
        ACHRONIC = "achronic", _("achronisch")

    class TemporalDuration(models.TextChoices):
        SCENE = "scene", _("Szene")
        STRETCH = "stretch", _("Dehnung")
        SUMMARY = "summary", _("Raffung")
        ELLIPSIS = "ellipsis", _("Ellipse")
        PAUSE = "pause", _("Pause")

    class TemporalFrequency(models.TextChoices):
        SINGULATIVE = "singulative", _("singulativ")
        REPEATING = "repetitive", _("repetitiv")
        ITERATIVE = "iterative", _("iterativ")

    class FigureSpeech(models.TextChoices):
        DIRECT_QUOTE = "direct_quotation", _("direkt zitierend")
        DIRECT_FIGURE_SPEECH = "direct_figure_speech", _(
            "autonome, direkte Figurenrede"
        )
        DIRECT_SPEECH = "direct_speech", _("direkte Rede")
        INDIRECT_SPEECH = "indirect_speech", _("indirekte Rede")
        NARRATED_MONOLOGUE = "narrated_monologue", _("erlebte Rede")

    class RepresentationOfThought(models.TextChoices):
        QUOTED_MONOLOGUE = "quoted_monologue", _("Zitat")
        PSYCHO_NARRATION = "psycho_narration", _("erzählter Monolog")
        AUTONOMOUS_MONOLOGUE = "autonomous_monologue", _("autonomer Monolog")
        STREAM_OF_CONSCIOUSNESS = (
            "stream_of_consciousness",
            _("Bewusstseinsstrom"),
        )

    class Focalization(models.TextChoices):
        ZERO_FOCALIZATION = "zero", _("Nullfokalisierung")
        INTERNAL_FOCALIZATION_VARIABLE = "internal_variable", _(
            "interne Fokalisierung – variabel"
        )
        INTERNAL_FOCALIZATION_FIXED = "internal_fixed", _(
            "interne Fokalisierung – fixiert"
        )
        EXTERNAL_FOCALIZATION = "external", _("externe Fokalisierung")

    # Typology by Franz Stanzel
    class NarrativeSituation(models.TextChoices):
        AUTHORIAL_NARRATIVE_SITUATION = "authorial", _("auktorial")
        NEUTRAL_NARRATIVE_SITUATION = "neutral", _("neutral")
        FIGURAL_NARRATIVE_SITUATION = "figural", _("personal")
        FIRST_PERSON_NARRATIVE_SITUATION = "first-person", _("Ich-Erzähler*in")

    class NarrativeChronology(models.TextChoices):
        PRIOR_NARRATION = "prior", _("früheres Erzählen")
        SIMULTANEOUS_NARRATION = "simultaneous", _("gleichzeitiges Erzählen")
        SUBSEQUENT_NARRATION = "subsequent", _("späteres Erzählen")

    class NarrativeLevel(models.TextChoices):
        EXTRADIEGETIC = "extra", _("extradiegetisch")
        INTRADIEGETIC = "intra", _("intradiegetisch")
        METADIEGETIC = "meta", _("metadiegetisch")

    class NarrativeVoice(models.TextChoices):
        HETERODIEGETIC = "heterodiegetic", _("heterodiegetisches Erzählen")
        HOMODIEGETIC_UNINVOLVED_EYEWITNESS = "homodiegetic_uninvolved", _(
            "homodiegetisches Erzählen – unbeteiligter Beobachter:in"
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_WITNESS_PARTICIPANT = "homodiegetic_participant", _(
            "homodiegetisches Erzählen – beteiligter Beobachter:in"
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_MINOR_CHARACTER = "homodiegetic_character", _(
            "homodiegetisches Erzählen – Nebenfigur"
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_PROTAGONIST = "homodiegetic_protagonist", _(
            "homodiegetisches Erzählen – Hauptfigur"
        )  # a.k.a. autodiegetic

    siglum = models.CharField(
        max_length=6, blank=True, null=True, verbose_name=_("Sigle")
    )

    summary = models.TextField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_("Teaser"),
        help_text=_("Kurzzusammenfassung"),
    )

    text_analysis = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Textanalyse"),
        help_text=_("Fließtext"),
    )

    context = models.TextField(
        blank=True, null=True, verbose_name=_("Entstehungskontext")
    )

    historical_events = models.TextField(
        blank=True, null=True, verbose_name=_("Historischer Kontext")
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="works",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    #  fields relating to narrative analysis / Erzähltextanalyse
    temporal_order = models.CharField(
        max_length=255,
        choices=TemporalOrder.choices,
        null=True,
        blank=True,
        verbose_name=_("Erzählordnung"),
    )

    temporal_duration = models.CharField(
        max_length=255,
        choices=TemporalDuration.choices,
        null=True,
        blank=True,
        verbose_name=_("Dauer"),
    )

    temporal_frequency = models.CharField(
        max_length=255,
        choices=TemporalFrequency.choices,
        null=True,
        blank=True,
        verbose_name=_("Frequenz"),
    )

    figure_speech = models.CharField(
        max_length=255,
        choices=FigureSpeech.choices,
        null=True,
        blank=True,
        verbose_name=_("Figurenrede"),
    )

    representation_of_thought = models.CharField(
        max_length=255,
        choices=RepresentationOfThought.choices,
        null=True,
        blank=True,
        verbose_name=_("Darstellung von Gedanken"),
    )

    focalization = models.CharField(
        max_length=255,
        choices=Focalization.choices,
        null=True,
        blank=True,
        verbose_name=_("Fokalisierung"),
    )

    narrative_situation = models.CharField(
        max_length=255,
        choices=NarrativeSituation.choices,
        null=True,
        blank=True,
        verbose_name=_("Erzählperspektive"),
    )

    narrative_chronology = models.CharField(
        max_length=255,
        choices=NarrativeChronology.choices,
        null=True,
        blank=True,
        verbose_name=_("Zeitpunkt des Erzählens"),
    )

    narrative_level = models.CharField(
        max_length=255,
        choices=NarrativeLevel.choices,
        null=True,
        blank=True,
        verbose_name=_("Ort des Erzählens"),
    )

    narrative_voice = models.CharField(
        max_length=255,
        choices=NarrativeVoice.choices,
        null=True,
        blank=True,
        verbose_name=_("Stellung des:der Erzähler:in zum Geschehen"),
    )

    class Meta:
        verbose_name = _("werk")
        verbose_name_plural = _("werke")
        ordering = ["title", "subtitle", "-siglum"]


@reversion.register(follow=["rootobject_ptr"])
class WorkType(AlternativeNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    name_plural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Pluralform"),
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="worktypes",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("werktyp")
        verbose_name_plural = _("werktypen")
        ordering = ["name", "name_plural", "alternative_name"]


@reversion.register(follow=["rootobject_ptr"])
class Expression(WorkMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A concrete representation of a given Work,
    captured in signs, images, audio signals,...
    """

    year_of_publication = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Erscheinungsjahr"),
        help_text=_("Eingabe muss im Format YYYY-MM-DD erfolgen"),
    )

    page_count = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Seitenanzahl"),
        help_text=_("Seitenanzahl einer relevanten Manifestation"),
    )

    relevant_pages = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Forschungsrelevante Seiten"),
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="expressions",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("werksexpression")
        verbose_name_plural = _("werksexpressionen")
        ordering = ["title", "subtitle"]


@reversion.register(follow=["rootobject_ptr"])
class Archive(DescriptionMixin, AbstractEntity):
    """
    An institution or organisation where physical objects are
    stored and cared for.
    """

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Anschrift"),
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Webseite"),
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="archives",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("archiv")
        verbose_name_plural = _("archive")


@reversion.register(follow=["rootobject_ptr"])
class PhysicalObject(DescriptionMixin, AbstractEntity):
    """
    A physical object pertaining to a Work.

    Has a quantifiable size, e.g. has a number of pages, comprises
    a number of folders, contains a number of items,...

    May be a manuscript or typoscript of a given Work, but extends to
    all kinds of material which are (loosely) related to a Work.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="physicalobjects",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("vorlassobjekt")
        verbose_name_plural = _("vorlassobjekte")


@reversion.register(follow=["rootobject_ptr"])
class Person(HumanBeingMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    Any natural person.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="persons",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name_plural = _("personen")
        ordering = ["last_name", "first_name", "name"]


@reversion.register(follow=["rootobject_ptr"])
class Organisation(AlternativeNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    Any legal entity, or subunit of a legal entity.

    Child class of abstract Actor class.
    """

    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Webseite"),
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="organisations",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("körperschaft")
        verbose_name_plural = _("körperschaften")
        ordering = ["name"]


@reversion.register(follow=["rootobject_ptr"])
class Character(HumanBeingMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A real or fictitious person who appears in or is mentioned in a Work.

    Defined per work, so "Anna" in Work A is distinct from "Anna" in Work B,
    even if they are the same character.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="characters",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class CharacterRelevancy(models.TextChoices):
        MAIN = "protagonist", _("Hauptfigur")
        SUPPORTING = "supporting_character", _("Nebenfigur")
        REFERENCED = "referenced_character", _("erwähnte Figur")

    relevancy = models.CharField(
        max_length=255,
        choices=CharacterRelevancy.choices,
        null=True,
        blank=False,
        verbose_name=_("Relevanz"),
        help_text=_("Bedeutsamkeit für den Text, Erzählfokus"),
    )

    class Meta:
        verbose_name = _("figur")
        verbose_name_plural = _("figuren")
        ordering = ["name", "-relevancy"]


@reversion.register(follow=["rootobject_ptr"])
class MetaCharacter(DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A composite entity to refer to related characters across works.

    Used to group identical characters (e.g. recurring characters),
    as well as different representations of the same characters
    (or what's assumed to be the same characters).
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="metacharacters",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("metafigur")
        verbose_name_plural = _("metafiguren")
        ordering = ["name"]


@reversion.register(follow=["rootobject_ptr"])
class Place(AlternativeNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A real place in our world, either in the past or present.
    Has a physical location which can be referenced via geocoordinates.
    """

    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("latitude"),
    )

    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("longitude"),
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="places",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("ort")
        verbose_name_plural = _("orte")
        ordering = ["name"]


@reversion.register(follow=["rootobject_ptr"])
class ResearchPerspective(
    AlternativeNameMixin, DescriptionMixin, StatusMixin, AbstractEntity
):
    """
    Lens through which works are investigated.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="researchperspectives",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("forschungshinsicht")
        verbose_name_plural = _("forschungshinsichten")
        ordering = ["name"]


@reversion.register(follow=["rootobject_ptr"])
class Topic(AlternativeNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    Topic with regard to content, theme.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="topics",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name = _("thema")
        verbose_name_plural = _("themen")
        ordering = ["name"]


@reversion.register(follow=["rootobject_ptr"])
class Interpretatem(DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A conceptual object representing a specific (interpretative/scholarly)
    view on one or more Works.
    """

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="interpretatems",
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Datenquelle"),
    )

    class Meta:
        verbose_name_plural = _("interpretateme")
        ordering = ["name"]
