from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_relations.models import Property
from dateparser import parse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
import re


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
        blank=True,
        default="",
        verbose_name=_("Bearbeitungsstatus"),
    )

    class Meta:
        abstract = True
        verbose_name = _("progress state")
        verbose_name_plural = _("progress states")


class NotesMixin(models.Model):
    """
    Mixin for internal notes.
    """

    notes = models.TextField(
        max_length=1024,
        blank=True,
        default="",
        verbose_name=_("Notiz"),
        help_text=_("Feld für interne Notizen"),
    )

    class Meta:
        abstract = True


class AlternativeNameMixin(models.Model):
    """
    Mixin for "alternative_name" field shared between entities.
    """

    alternative_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Alternativer Name"),
    )

    class Meta:
        abstract = True


class GenericNameMixin(models.Model):
    """
    Mixin for generic "name" field used by entities.
    """

    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DescriptionMixin(models.Model):
    """
    Mixin for "description" field shared between entities.
    """

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Beschreibung"),
    )

    class Meta:
        abstract = True


class PersonNameMixin(AlternativeNameMixin, models.Model):
    """
    Mixin for name fields shared between person-like entities.
    """

    forename = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Vorname"),
    )

    surname = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Nachname"),
    )

    fallback_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Uneindeutiger Name"),
        help_text=_(
            "Namens-Ersatzfeld, falls weder Vor- noch Nachname eindeutig "
            "als solche festgelegt bzw. eingegeben werden können"
        ),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name()

    def full_name(self):
        full_name = ""
        surname = self.surname
        forename = self.forename
        fallback_name = self.fallback_name

        if fallback_name != "":
            full_name = fallback_name
        else:
            if forename != "" and surname != "":
                full_name = f"{forename} {surname}"
            elif surname != "":
                full_name = surname
            elif forename != "":
                full_name = forename
            else:
                pass

        return full_name


class TitlesMixin(models.Model):
    """
    Mixin for fields shared between work-like entities.
    """

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Titel"),
    )

    subtitle = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Untertitel"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def full_title(self):
        full_title = self.title
        subtitle = self.subtitle
        letter_or_digit = re.compile(r"[\W\d]", re.U)

        if subtitle:
            if letter_or_digit.match(subtitle[0]):
                full_title += f" {subtitle}"
            else:
                full_title += f". {subtitle}"

        return full_title


class LanguageMixin(models.Model):
    class Languages_ISO_639_3(models.TextChoices):
        """
        A selection of ISO 639-3 language codes
        relevant to the project.
        """

        DE = "deu", _("Deutsch")
        EN = "eng", _("Englisch")
        FR = "fra", _("Französisch")

    language = MultiSelectField(
        max_length=255,
        choices=Languages_ISO_639_3.choices,
        blank=True,
        default="",
        verbose_name=_("Sprache"),
    )

    class Meta:
        abstract = True


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


class Work(TitlesMixin, LanguageMixin, NotesMixin, StatusMixin, AbstractEntity):
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
        DIRECT_FIGURE_SPEECH = (
            "direct_figure_speech",
            _("autonome, direkte Figurenrede"),
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
        INTERNAL_FOCALIZATION_VARIABLE = (
            "internal_variable",
            _("interne Fokalisierung – variabel"),
        )
        INTERNAL_FOCALIZATION_FIXED = (
            "internal_fixed",
            _("interne Fokalisierung – fixiert"),
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
        HOMODIEGETIC_UNINVOLVED_EYEWITNESS = (
            "homodiegetic_uninvolved",
            _("homodiegetisches Erzählen – unbeteiligter Beobachter:in"),
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_WITNESS_PARTICIPANT = (
            "homodiegetic_participant",
            _("homodiegetisches Erzählen – beteiligter Beobachter:in"),
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_MINOR_CHARACTER = (
            "homodiegetic_character",
            _("homodiegetisches Erzählen – Nebenfigur"),
        )  # a.k.a. alterodiegetic
        HOMODIEGETIC_PROTAGONIST = (
            "homodiegetic_protagonist",
            _("homodiegetisches Erzählen – Hauptfigur"),
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
        default="",
        verbose_name=_("Teaser"),
        help_text=_("Kurzzusammenfassung"),
    )

    text_analysis = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Textanalyse"),
        help_text=_("Fließtext"),
    )

    context = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Entstehungskontext"),
    )

    historical_events = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Historischer Kontext"),
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
        blank=True,
        default="",
        verbose_name=_("Erzählordnung"),
    )

    temporal_duration = models.CharField(
        max_length=255,
        choices=TemporalDuration.choices,
        blank=True,
        default="",
        verbose_name=_("Dauer"),
    )

    temporal_frequency = models.CharField(
        max_length=255,
        choices=TemporalFrequency.choices,
        blank=True,
        default="",
        verbose_name=_("Frequenz"),
    )

    figure_speech = models.CharField(
        max_length=255,
        choices=FigureSpeech.choices,
        blank=True,
        default="",
        verbose_name=_("Figurenrede"),
    )

    representation_of_thought = models.CharField(
        max_length=255,
        choices=RepresentationOfThought.choices,
        blank=True,
        default="",
        verbose_name=_("Darstellung von Gedanken"),
    )

    focalization = models.CharField(
        max_length=255,
        choices=Focalization.choices,
        blank=True,
        default="",
        verbose_name=_("Fokalisierung"),
    )

    narrative_situation = models.CharField(
        max_length=255,
        choices=NarrativeSituation.choices,
        blank=True,
        default="",
        verbose_name=_("Erzählperspektive"),
    )

    narrative_chronology = models.CharField(
        max_length=255,
        choices=NarrativeChronology.choices,
        blank=True,
        default="",
        verbose_name=_("Zeitpunkt des Erzählens"),
    )

    narrative_level = models.CharField(
        max_length=255,
        choices=NarrativeLevel.choices,
        blank=True,
        default="",
        verbose_name=_("Ort des Erzählens"),
    )

    narrative_voice = models.CharField(
        max_length=255,
        choices=NarrativeVoice.choices,
        blank=True,
        default="",
        verbose_name=_("Stellung des:der Erzähler:in zum Geschehen"),
    )

    class Meta:
        verbose_name = _("werk")
        verbose_name_plural = _("werke")


class WorkType(
    GenericNameMixin,
    AlternativeNameMixin,
    DescriptionMixin,
    StatusMixin,
    AbstractEntity,
):
    name_plural = models.CharField(
        max_length=255,
        blank=True,
        default="",
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


class Expression(
    TitlesMixin,
    DescriptionMixin,
    LanguageMixin,
    NotesMixin,
    StatusMixin,
    AbstractEntity,
):
    """
    A concrete representation of a given Work,
    captured in signs, images, audio signals,...
    """

    class EditionTypes(models.TextChoices):
        FIRST_EDITION = "first_edition", _("Erstausgabe")
        REFERENCE_EDITION = "reference_edition", _("Referenzausgabe")

    publication_date_iso_formatted = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Erscheinungsdatum (ISO-Format)"),
        editable=False,
    )

    publication_date_manual_input = models.CharField(
        blank=True,
        default="",
        verbose_name=_("Erscheinungsdatum (manuelle Eingabe)"),
        help_text=_(
            "Erlaubte Formatvariationen u.a. 1.1.1920, 12/2010, 1999-12-23,..."
        ),
    )

    isbn = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("ISBN"),
    )

    # for storing free-form information about a published work's
    # (print) edition
    edition = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Ausgabe (Print-/Druckausgabe)"),
        help_text=_("Bsp.: 1. Aufl., deutsche Erstausg."),
    )

    volume = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name=_("Band"),
    )

    issue = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name=_("Zeitungsnummer"),
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
        default="",
        verbose_name=_("Forschungsrelevante Seiten"),
        help_text=_('Eingabe muss im Format "X-Y" erfolgen, z.B. 5-12'),
    )

    edition_type = MultiSelectField(
        max_length=255,
        choices=EditionTypes.choices,
        blank=True,
        default="",
        verbose_name=_("Ausgabetyp"),
        help_text=_("Zur Markierung speziell relevanter Ausgaben"),
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
        self.cached_pub_date_manual = self.publication_date_manual_input

    def save(self, *args, **kwargs):
        if self.publication_date_manual_input != self.cached_pub_date_manual:
            # free-form publication date was changed
            if not self.publication_date_manual_input:
                # publication date field was emptied
                self.publication_date_iso_formatted = self.publication_date_manual_input
            else:
                parsed_date = parse(
                    self.publication_date_manual_input,
                    languages=[settings.LANGUAGE_CODE],
                    date_formats=settings.DATE_INPUT_FORMATS,
                    settings=settings.DATEPARSER_SETTINGS,
                )
                if not parsed_date:
                    # "log" invalid publication date updates in field string
                    self.publication_date_manual_input = (
                        f"{self.publication_date_manual_input} (unsupported date)"
                    )
                # update ISO date either way:
                # if the manually input date is a recognisable date but wasn't
                # parseable (formatting rules), we don't want to keep two
                # out-of-sync dates around
                self.publication_date_iso_formatted = parsed_date

            if "update_fields" in kwargs and (
                include_fields := {
                    "publication_date_manual_input",
                    "publication_date_iso_formatted",
                }
            ).intersection(update_fields := kwargs.get("update_fields")):
                kwargs["update_fields"] = set(update_fields) | include_fields

        super().save(*args, **kwargs)


class Archive(GenericNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
    """
    An institution or organisation where physical objects are
    stored and cared for.
    """

    location = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Anschrift"),
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        default="",
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


class PhysicalObject(GenericNameMixin, DescriptionMixin, AbstractEntity):
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
        default="",
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


class Person(PersonNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
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


class Organisation(
    GenericNameMixin,
    AlternativeNameMixin,
    DescriptionMixin,
    StatusMixin,
    AbstractEntity,
):
    """
    Any legal entity, or subunit of a legal entity.

    Child class of abstract Actor class.
    """

    website = models.URLField(
        max_length=255,
        blank=True,
        default="",
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


class Character(PersonNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
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
        blank=False,
        default="",
        verbose_name=_("Relevanz"),
        help_text=_("Bedeutsamkeit für den Text, Erzählfokus"),
    )

    fictionality = MultiSelectField(
        max_length=255,
        choices=CharacterFictionality.choices,
        blank=False,
        default="",
        verbose_name=_("Erfindungsgrad"),
        help_text=_("Faktizität vs. Fiktionalität"),
    )

    class Meta:
        verbose_name = _("figur")
        verbose_name_plural = _("figuren")


class MetaCharacter(GenericNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
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


class Place(
    GenericNameMixin,
    AlternativeNameMixin,
    DescriptionMixin,
    StatusMixin,
    AbstractEntity,
):
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


class ResearchPerspective(
    GenericNameMixin,
    AlternativeNameMixin,
    DescriptionMixin,
    NotesMixin,
    StatusMixin,
    AbstractEntity,
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


class Topic(
    GenericNameMixin,
    AlternativeNameMixin,
    DescriptionMixin,
    NotesMixin,
    StatusMixin,
    AbstractEntity,
):
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


class Interpretatem(GenericNameMixin, DescriptionMixin, StatusMixin, AbstractEntity):
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


def create_properties(
    name_forward: str, name_reverse: str, subjects: list, objects: list
):
    """
    Helper function for creating new Properties.
    """
    prop, created = Property.objects.get_or_create(
        name_forward=name_forward,
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

    Workaround for dealing with Property deletions or changes to values of
    fields by which they are looked up, like "name_forward", "name_reverse",
    because there is no equivalent to Django migrations, with which
    changes to model classes can be preserved independently of changes
    to the code recorded via commits.

    ATTN.: Do not use update() to modify "name_forward" or "name_reverse"
    as it ignores custom save() methods, which for changes to these
    Property fields is relevant.

    Examples:
    Property.objects.filter(name_forward="is part of").delete()
    for prop in Property.objects.filter(name="includes"):
        prop.name_forward = "is included in"
        prop.name_reverse = "includes"
        prop.save("name_forward", "name_reverse")

    Don't forget to also always update a Property's name fields
    in construct_properties() when they are modified here.
    """

    # delete_is_part_of_work
    Property.objects.filter(name_forward="is part of work").delete()

    # rename "name_forward" field of Expression/Expression relation
    # and also rename "name_reverse" field
    for prop in Property.objects.filter(
        name_forward__in=["is part of expression", "is part of"]
    ):
        prop.name_forward = "expression is part of expression"
        prop.name_reverse = "expression has part expression"
        prop.save()

    # fix name_reverse of Binnenverweis relation
    for prop in Property.objects.filter(name_reverse__in=["is referenced by"]):
        prop.name_reverse = "is referenced in"
        prop.save()


def construct_properties():
    """
    Create relationships between entity classes.

    Regarding property definitions:
    - each "name_forward" (and "name_reverse") may only be used once,
    - a relationship can connect more than two entities, i.e. can have more
    than just one Subject (subj_class) or just one Object (obj_class).
    """
    update_properties()

    # WORK-focussed relations
    # discusses / Aussage – something is talked about in a work
    create_properties(
        name_forward="discusses",
        name_reverse="is discussed in",
        subjects=[Work],
        objects=[Work, Place],
    )

    # mentions / Erwähnung – something is only mentioned by name
    create_properties(
        name_forward="mentions",
        name_reverse="is mentioned in",
        subjects=[Work],
        objects=[Work, Place],
    )

    # takes_place_in / Schauplatz – a place is an actual location in the work
    create_properties(
        name_forward="takes place in",
        name_reverse="is locale in",
        subjects=[Work],
        objects=[Place],
    )

    # references / Binnenverweis
    create_properties(
        name_forward="references",
        name_reverse="is referenced in",
        subjects=[Work],
        objects=[Work],
    )

    # TYPE-focussed relations
    # has_type
    create_properties(
        name_forward="has type",
        name_reverse="is type of",
        subjects=[Work],
        objects=[WorkType],
    )

    # has_broader_term
    create_properties(
        name_forward="has broader term",
        name_reverse="has narrower term",
        subjects=[WorkType],
        objects=[WorkType],
    )

    # EXPRESSION-focussed relations
    # is_realised_in
    create_properties(
        name_forward="is realised in",
        name_reverse="realises",
        subjects=[Work, Expression],
        objects=[Expression],
    )

    # expression_is_part_of_expression
    create_properties(
        name_forward="expression is part of expression",
        name_reverse="expression has part expression",
        subjects=[Expression],
        objects=[Expression],
    )

    # work_is_part_of_expression
    create_properties(
        name_forward="work is part of expression",
        name_reverse="expression has part work",
        subjects=[Work],
        objects=[Expression],
    )

    # published_in
    create_properties(
        name_forward="is published in",
        name_reverse="is place of publication of",
        subjects=[Expression],
        objects=[Place],
    )

    # CHARACTER-focussed relations
    # features
    create_properties(
        name_forward="features",
        name_reverse="is featured in",
        subjects=[Work],
        objects=[Character],
    )

    # groups
    create_properties(
        name_forward="groups",
        name_reverse="is grouped in",
        subjects=[MetaCharacter],
        objects=[Character],
    )

    # place_inspires
    create_properties(
        name_forward="inspires",
        name_reverse="is inspired by",
        subjects=[Place],
        objects=[Place],
    )

    # ARCHIVE-focussed relations
    # archive_holds
    create_properties(
        name_forward="holds",
        name_reverse="is held in",
        subjects=[Archive],
        objects=[PhysicalObject],
    )

    # relates_to
    create_properties(
        name_forward="relates to",
        name_reverse="is connected with",
        subjects=[PhysicalObject],
        objects=[Work],
    )

    # INTERPRETATEM-focussed relations
    # has_source
    create_properties(
        name_forward="has source",
        name_reverse="is source for",
        subjects=[Interpretatem],
        objects=[Work],
    )

    # interprets
    create_properties(
        name_forward="interprets",
        name_reverse="is interpreted by",
        subjects=[Interpretatem],
        objects=[Work],
    )

    # CONCEPT-focussed relations
    # is_based_on
    create_properties(
        name_forward="is based on",
        name_reverse="is base for",
        subjects=[Character],
        objects=[Person, Topic],
    )

    # is_about
    create_properties(
        name_forward="is about topic",
        name_reverse="is topic of",
        subjects=[Work, Interpretatem],
        objects=[Topic],
    )

    # applies_research_perspective
    create_properties(
        name_forward="applies research perspective",
        name_reverse="is research perspective of",
        subjects=[Work, Interpretatem],
        objects=[ResearchPerspective],
    )

    # ORGANISATION-focussed relations
    # has_residence
    create_properties(
        name_forward="has current or former residence",
        name_reverse="is current or former residence of",
        subjects=[Organisation],
        objects=[Place],
    )

    # is_publisher
    create_properties(
        name_forward="is publisher of",
        name_reverse="has publisher",
        subjects=[Organisation],
        objects=[Expression],
    )

    # ACTOR roles in relation to Work, Expression
    # is_contributor /  Beitragende:r (generisch)
    create_properties(
        name_forward="is contributor to",
        name_reverse="has contributor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_author / Autor*in
    create_properties(
        name_forward="is author of",
        name_reverse="has author",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_photographer / Fotograf:in
    create_properties(
        name_forward="is photographer of/for",
        name_reverse="has photographer",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # is_illustrator / Illustrator:in
    create_properties(
        name_forward="is illustrator of/for",
        name_reverse="has illustrator",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # Übersetzer:in
    # is_translator
    create_properties(
        name_forward="is translator of",
        name_reverse="has translator",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_editor / Herausgeber*in
    create_properties(
        name_forward="is editor of",
        name_reverse="has editor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    #  is_director / Regisseur*in
    create_properties(
        name_forward="is director of",
        name_reverse="has director",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_dramaturg / Dramaturg*in
    create_properties(
        name_forward="is dramaturg for",
        name_reverse="has dramaturg",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_composer / Komponist*in
    create_properties(
        name_forward="is composer of",
        name_reverse="has composer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_session_musician / Musiker*in
    create_properties(
        name_forward="is session musician on",
        name_reverse="has session musician",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_stage_designer / Bühnenbildner*in (Kontext: Theater; vgl. Szenenbildner*in)
    create_properties(
        name_forward="is stage designer for",
        name_reverse="has stage designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_costume_designer / Kostümbildner*in
    create_properties(
        name_forward="is costume designer for",
        name_reverse="has costume designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_makeup_artist / Maskenbildner*in
    create_properties(
        name_forward="is make-up artist on",
        name_reverse="has make-up artist",
        subjects=[Organisation],
        objects=[Work, Expression],
    )

    # is_sound_engineer / Tonmeister*in
    create_properties(
        name_forward="is sound engineer of",
        name_reverse="has sound engineer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_film_editor / Cutter*in
    create_properties(
        name_forward="is film editor of",
        name_reverse="has film editor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_actor/ Schauspieler*in
    create_properties(
        name_forward="is actor in",
        name_reverse="has actor",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_narrator / Sprecher*in
    create_properties(
        name_forward="is narrator of",
        name_reverse="has narrator",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_cinematographer / Kameramensch
    create_properties(
        name_forward="is cinematographer of",
        name_reverse="has cinematographer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_head_of_production / Produktionsleiter*in
    create_properties(
        name_forward="is head of production of",
        name_reverse="has head of production",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )

    # is_production_designer / Szenenbilder*in (Kontext: Film; vgl. Bühnenbildner*in)
    create_properties(
        name_forward="is production designer of",
        name_reverse="has production designer",
        subjects=[Person, Organisation],
        objects=[Work, Expression],
    )
