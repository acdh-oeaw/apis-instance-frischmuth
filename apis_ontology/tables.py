import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A
from django.utils.translation import gettext_lazy as _


from .models import (
    Archive,
    Character,
    Expression,
    Interpretatem,
    MetaCharacter,
    Organisation,
    Person,
    PhysicalObject,
    Place,
    ResearchPerspective,
    Topic,
    Work,
    WorkType,
)


class GenericEditLinkColumn(tables.Column):
    linkify = {
        "viewname": "apis:generic:update",
        "args": [A("self_contenttype"), A("pk")],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            linkify=self.linkify,
            *args,
            **kwargs,
        )


class FullTitleMixin(tables.Table):
    full_title = GenericEditLinkColumn(
        accessor="full_title",
        verbose_name=_("Titel (gesamt)"),
        order_by=("title", "subtitle"),
    )

    class Meta:
        sequence = ("full_title", "title", "subtitle")
        exclude = ["title", "subtitle"]


class FullNameMixin(tables.Table):
    full_name = GenericEditLinkColumn(
        accessor="full_name",
        verbose_name=_("Name (voller)"),
        order_by=("fallback_name", "surname", "forename"),
    )

    class Meta:
        sequence = ("full_name", "fallback_name", "surname", "forename")
        exclude = ["fallback_name", "surname", "forename"]


class BaseEntityTable(AbstractEntityTable, tables.Table):
    id = GenericEditLinkColumn()
    progress_status = tables.Column(verbose_name=_("Status"))

    class Meta(AbstractEntityTable.Meta):
        exclude = ["desc"]
        sequence = (
            "...",
            "progress_status",
            "id",
            "view",
            "edit",
            "delete",
            "noduplicate",
        )


class WorkTable(FullTitleMixin, BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Work
        fields = ["siglum"]
        order_by = ("full_title",)


class ExpressionTable(FullTitleMixin, BaseEntityTable, tables.Table):
    class Meta(BaseEntityTable.Meta):
        model = Expression
        fields = ["edition_type", "publication_date_iso", "publication_date"]
        order_by = ("full_title", "publication_date_iso", "edition_type")

    publication_date_iso = tables.Column(verbose_name=_("Datum"))
    publication_date = tables.Column(verbose_name=_("Datum (manuell)"))


class WorkTypeTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = WorkType
        fields = ["name", "description"]

    name = GenericEditLinkColumn()


class PersonTable(FullNameMixin, BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Person
        fields = ["full_name", "alternative_name", "description"]
        order_by = ("full_name", "alternative_name", "description")


class OrganisationTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Organisation

    name = GenericEditLinkColumn()


class CharacterTable(FullNameMixin, BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Character
        fields = ["relevancy", "fictionality"]


class MetaCharacterTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = MetaCharacter

    name = GenericEditLinkColumn()


class PlaceTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Place
        fields = ["name", "alternative_name"]

    name = GenericEditLinkColumn()


class ResearchPerspectiveTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = ResearchPerspective
        fields = ["name", "alternative_name", "description"]
        order_by = ("name", "alternative_name")

    name = GenericEditLinkColumn()


class TopicTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Topic
        fields = ["name", "description"]
        order_by = ("name", "alternative_name")

    name = GenericEditLinkColumn()


class InterpretatemTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Interpretatem
        fields = ["name", "description"]
        order_by = ("name", "alternative_name")

    name = GenericEditLinkColumn()


class ArchiveTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Archive
        fields = ["name", "description"]
        order_by = ("name", "description")

    name = GenericEditLinkColumn()


class PhysicalObjectTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = PhysicalObject
        fields = ["name", "description"]
        order_by = ("name",)

    name = GenericEditLinkColumn()
