import reversion
from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_relations.models import Property
from dateparser import parse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField


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
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Sigle"),
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


@reversion.register(follow=["rootobject_ptr"])
class Expression(WorkMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    A concrete representation of a given Work,
    captured in signs, images, audio signals,...
    """

    class EditionTypes(models.TextChoices):
        FIRST_EDITION = "first_edition", _("Erstausgabe")
        REFERENCE_EDITION = "reference_edition", _("Referenzausgabe")

    publication_date_iso = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Erscheinungsdatum (ISO)"),
        help_text=_("Format YYYY-MM-DD"),
        editable=False,
    )

    publication_date = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Erscheinungsdatum"),
        help_text=_(
            "Erlaubte Formatvariationen u.a. 1.1.1920, 12/2010, 1999-12-23,..."
        ),
    )

    issue = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("(Zeitungs)Ausgabe"),
        help_text=_("Nummer/Kennung einer Ausgabe eines periodischen Mediums"),
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
        help_text=_('Eingabe muss im Format "X-Y" erfolgen, z.B. 5-12'),
    )

    edition_type = MultiSelectField(
        max_length=255,
        choices=EditionTypes.choices,
        null=True,
        blank=True,
        verbose_name="Ausgabetyp",
        help_text="Zur Markierung speziell relevanter Ausgaben",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_publication_date = self.publication_date

    def save(self, *args, **kwargs):
        if self.publication_date != self.cached_publication_date:
            # free-form publication date was changed
            if not self.publication_date:
                # publication date field was emptied
                self.publication_date_iso = self.publication_date
            else:
                parsed_date = parse(
                    self.publication_date,
                    languages=[settings.LANGUAGE_CODE],
                    date_formats=settings.DATE_INPUT_FORMATS,
                    settings=settings.DATEPARSER_SETTINGS,
                )
                if not parsed_date:
                    # "log" invalid publication date updates in field string
                    self.publication_date = (
                        f"{self.publication_date} (unsupported date)"
                    )
                # update ISO date either way: if publication_date is a
                # recognisable date but wasn't parseable (formatting rules),
                # we don't want to keep 2 out-of-sync dates around
                self.publication_date_iso = parsed_date

            if "update_fields" in kwargs and (
                include_fields := {"publication_date", "publication_date_iso"}
            ).intersection(update_fields := kwargs.get("update_fields")):
                kwargs["update_fields"] = set(update_fields) | include_fields

        super().save(*args, **kwargs)


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

    vorlass_doc_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Vorlassdokument-Referenz"),
        editable=False,
    )

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

    class CharacterFictionality(models.TextChoices):
        FICTIONAL = "fictional_character", _("fiktive Figur")
        HISTORICAL = "historical_character", _("historische Figur")
        MYTHICAL = "mythical_character", _("mythologische Figur")

    relevancy = models.CharField(
        max_length=255,
        choices=CharacterRelevancy.choices,
        null=True,
        blank=False,
        verbose_name=_("Relevanz"),
        help_text=_("Bedeutsamkeit für den Text, Erzählfokus"),
    )

    fictionality = MultiSelectField(
        max_length=255,
        choices=CharacterFictionality.choices,
        null=True,
        blank=False,
        verbose_name="Erfindungsgrad",
        help_text="Faktizität vs. Fiktionalität",
    )

    class Meta:
        verbose_name = _("figur")
        verbose_name_plural = _("figuren")


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


def create_properties(name: str, name_reverse: str, subjects: list, objects: list):
    """
    Helper function for creating new Properties.
    """
    prop, created = Property.objects.get_or_create(
        name=name,
        name_reverse=name_reverse,
    )

    prop.subj_class.clear()
    prop.obj_class.clear()

    for entity in subjects:
        prop.subj_class.add(ContentType.objects.get(model=entity._meta.model_name))
    for entity in objects:
        prop.obj_class.add(ContentType.objects.get(model=entity._meta.model_name))

    return prop, created


def update_properties():
    """
    Function for temporary storage of destructive changes to Property
    objects until the changes have been applied (/deployed).

    Workaround for dealing with Property deletions or changes to
    values of fields by which they are looked up, like "name", "name_reverse",
    because there is no equivalent to Django migrations, with which
    changes to model classes can be preserved independently of changes
    to the code recorded via commits.

    ATTN.: Do not use update() to modify "name" or "name_reverse"
    as it ignores custom save() methods, which for changes to these
    Property fields is relevant.

    Examples:
    Property.objects.filter(name="is part of").delete()
    for prop in Property.objects.filter(name="includes"):
        prop.name = "is included in"
        prop.name_reverse = "includes"
        prop.save()

    Don't forget to also always update a Property's "name" field values
    in construct_properties() when they are modified here.
    """

    delete_is_part_of_work = Property.objects.filter(name="is part of work").delete()

    # rename "name" field of Expression/Expression relation
    # and also rename "name_reverse" field
    for prop in Property.objects.filter(
        name__in=["is part of expression", "is part of"]
    ):
        prop.name = "expression is part of expression"
        prop.name_reverse = "expression has part expression"
        prop.save()


def construct_properties():
    """
    Create relationships between entity classes.

    Regarding property definitions:
    - each "name" (and "name_reversed") may only be used once,
    - a relationship can connect more than two entities, i.e. can have more
    than just one Subject (subj_class) or just one Object (obj_class).
    """
    update_properties()

    # WORK-focussed relations
    # Aussage – something is talked about in a work
    discusses = create_properties(
        name="discusses",
        name_reverse="is discussed in",
        subjects=[Work],
        objects=[Work, Place],
    )

    # Erwähnung – something is only mentioned by name
    mentions = create_properties(
        name="mentions",
        name_reverse="is mentioned in",
        subjects=[Work],
        objects=[Work, Place],
    )

    # Schauplatz – a place is an actual location in the work
    takes_place_in = create_properties(
        name="takes place in",
        name_reverse="is locale in",
        subjects=[Work],
        objects=[Place],
    )

    # Binnenverweis
    references = create_properties(
        name="references",
        name_reverse="is referenced by",
        subjects=[Work],
        objects=[Work],
    )

    # TYPE-focussed relations
    has_type = create_properties(
        name="has type",
        name_reverse="is type of",
        subjects=[Work],
        objects=[WorkType],
    )

    has_broader_term = create_properties(
        name="has broader term",
        name_reverse="has narrower term",
        subjects=[WorkType],
        objects=[WorkType],
    )

    # EXPRESSION-focussed relations
    is_realised_in = create_properties(
        name="is realised in",
        name_reverse="realises",
        subjects=[Work],
        objects=[Expression],
    )

    expression_is_part_of_expression = create_properties(
        name="expression is part of expression",
        name_reverse="expression has part expression",
        subjects=[Expression],
        objects=[Expression],
    )

    work_is_part_of_expression = create_properties(
        name="work is part of expression",
        name_reverse="expression has part work",
        subjects=[Work],
        objects=[Expression],
    )

    published_in = create_properties(
        name="is published in",
        name_reverse="is place of publication of",
        subjects=[Expression],
        objects=[Place],
    )

    # CHARACTER-focussed relations
    features = create_properties(
        name="features",
        name_reverse="is featured in",
        subjects=[Work],
        objects=[Character],
    )

    groups = create_properties(
        name="groups",
        name_reverse="is grouped in",
        subjects=[MetaCharacter],
        objects=[Character],
    )

    place_inspires = create_properties(
        name="inspires",
        name_reverse="is inspired by",
        subjects=[Place],
        objects=[Place],
    )

    # ARCHIVE-focussed relations
    archive_holds = create_properties(
        name="holds",
        name_reverse="is held in",
        subjects=[Archive],
        objects=[PhysicalObject],
    )

    relates_to = create_properties(
        name="relates to",
        name_reverse="is connected with",
        subjects=[PhysicalObject],
        objects=[Work],
    )

    # INTERPRETATEM-focussed relations
    has_source = create_properties(
        name="has source",
        name_reverse="is source for",
        subjects=[Interpretatem],
        objects=[Work],
    )

    interprets = create_properties(
        name="interprets",
        name_reverse="is interpreted by",
        subjects=[Interpretatem],
        objects=[Work],
    )

    # CONCEPT-focussed relations
    is_based_on = create_properties(
        name="is based on",
        name_reverse="is base for",
        subjects=[Character],
        objects=[Person, Topic],
    )

    is_about = create_properties(
        name="is about topic",
        name_reverse="is topic of",
        subjects=[Work, Interpretatem],
        objects=[Topic],
    )

    applies_research_perspective = create_properties(
        name="applies research perspective",
        name_reverse="is research perspective of",
        subjects=[Work, Interpretatem],
        objects=[ResearchPerspective],
    )

    # ORGANISATION-focussed relations
    has_residence = create_properties(
        name="has current or former residence",
        name_reverse="is current or former residence of",
        subjects=[Organisation],
        objects=[Place],
    )

    is_publisher = create_properties(
        name="is publisher of",
        name_reverse="has publisher",
        subjects=[Organisation],
        objects=[Expression],
    )

    # ACTOR roles in relation to Work, Expression
    # Beitragende:r (generisch)
    is_contributor = create_properties(
        name="is contributor to",
        name_reverse="has contributor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Autor*in
    is_author = create_properties(
        name="is author of",
        name_reverse="has author",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Fotograf:in
    is_photographer = create_properties(
        name="is photographer of/for",
        name_reverse="has photographer",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # Illustrator:in
    is_illustrator = create_properties(
        name="is illustrator of/for",
        name_reverse="has illustrator",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # Übersetzer:in
    is_translator = create_properties(
        name="is translator of",
        name_reverse="has translator",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Herausgeber*in
    is_editor = create_properties(
        name="is editor of",
        name_reverse="has editor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Regisseur*in
    is_director = create_properties(
        name="is director of",
        name_reverse="has director",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Dramaturg*in
    is_dramaturg = create_properties(
        name="is dramaturg for",
        name_reverse="has dramaturg",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Komponist*in
    is_composer = create_properties(
        name="is composer of",
        name_reverse="has composer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Musiker*in
    is_session_musician = create_properties(
        name="is session musician on",
        name_reverse="has session musician",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Bühnenbildner*in (Kontext: Theater; vgl. Szenenbildner*in)
    is_stage_designer = create_properties(
        name="is stage designer for",
        name_reverse="has stage designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Kostümbildner*in
    is_costume_designer = create_properties(
        name="is costume designer for",
        name_reverse="has costume designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Maskenbildner*in
    is_makeup_artist = create_properties(
        name="is make-up artist on",
        name_reverse="has make-up artist",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # Tonmeister*in
    is_sound_engineer = create_properties(
        name="is sound engineer of",
        name_reverse="has sound engineer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Cutter*in
    is_film_editor = create_properties(
        name="is film editor of",
        name_reverse="has film editor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Schauspieler*in
    is_actor = create_properties(
        name="is actor in",
        name_reverse="has actor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Sprecher*in
    is_narrator = create_properties(
        name="is narrator of",
        name_reverse="has narrator",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Kameramensch
    is_cinematographer = create_properties(
        name="is cinematographer of",
        name_reverse="has cinematographer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Produktionsleiter*in
    is_head_of_production = create_properties(
        name="is head of production of",
        name_reverse="has head of production",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # Szenenbilder*in (Kontext: Film; vgl. Bühnenbildner*in)
    is_production_designer = create_properties(
        name="is production designer of",
        name_reverse="has production designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )
