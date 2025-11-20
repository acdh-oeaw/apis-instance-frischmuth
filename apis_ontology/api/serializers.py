"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

import logging
import re

import markdown
from apis_core.history.models import RootObject
from django.contrib.postgres.expressions import Subquery
from django.db.models import TextField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apis_ontology.models import (
    Archive,
    Character,
    Expression,
    Glossar,
    Interpretatem,
    MetaCharacter,
    Person,
    PhysicalObject,
    Place,
    ResearchPerspective,
    Topic,
    Work,
    WorkType,
)


logger = logging.getLogger(__name__)


def get_link_from_id(id: str, field: str) -> str:
    obj = RootObject.objects_inheritance.filter(pk=id).select_subclasses()
    if obj.count() == 1:
        obj = obj.first()
        if hasattr(obj, "get_frontend_url"):
            return obj.get_frontend_url()
        else:
            logger.warning(
                f"{field} object {obj} doesnt have frontend function configured"
            )
    elif obj.count() > 1:
        logger.warning(f"{field} found ID {id} that returned multiple objects")
    return id


def convert_to_md(value, field_name):
    md = re.sub(
        r"(?<=\]\()[0-9]+(?=\))",
        lambda txt: get_link_from_id(txt.group(), field_name),
        value,
    )
    try:
        html = markdown.markdown(md)
    except Exception as e:
        logger.error(f"Markdown conversion failed for {field_name}: {e}")
        html = value
    return html


class MarkdownSerializerMixin(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        text_fields = [
            field.name
            for field in self.Meta.model._meta.get_fields()
            if isinstance(field, TextField)
        ]

        for field_name in text_fields:
            if field := data.get(field_name, None):
                data[field_name] = convert_to_md(field, field_name)

        return data


def get_work_type_data(id):
    work_type_parent = WorkType.objects.filter(
        triple_set_from_obj__subj_id=id, triple_set_from_obj__prop__id=7
    ).values("id")
    res = (
        WorkType.objects.filter(pk=id)
        .annotate(parent=Subquery(work_type_parent[:1]))
        .first()
    )
    return {
        "id": id,
        "name": getattr(res, "name"),
        "parent": getattr(res, "parent"),
        "count": 0,
        "children": [],
    }


class AuthorDataSerializer(MarkdownSerializerMixin):
    class Meta:
        model = Person
        fields = ["id", "forename", "surname", "fallback_name"]


class RelatedWorksMinDataSerializer(MarkdownSerializerMixin):
    authors = AuthorDataSerializer(many=True, allow_empty=True, required=False)

    class Meta:
        model = Work
        fields = ["id", "title", "subtitle", "authors"]


class NameAndIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class PlaceDataSerializerMin(MarkdownSerializerMixin):
    uris = serializers.ListField(
        required=False, allow_empty=True, child=serializers.URLField()
    )

    class Meta:
        model = Place
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class PlaceDataSerializer(PlaceDataSerializerMin):
    relation_type = serializers.CharField(required=False, allow_null=True)


class WorkTypeDataSerializer(MarkdownSerializerMixin):
    class Meta:
        model = WorkType
        fields = [
            "name",
            "name_plural",
        ]


class ExpressionDataSerializer(MarkdownSerializerMixin):
    publication_date = serializers.DateField(required=False, allow_null=True)
    publisher = serializers.CharField(required=False, allow_null=True)
    place_of_publication = serializers.ListField(
        child=serializers.CharField(allow_null=True), required=False, allow_empty=True
    )
    edition_type = serializers.ListField(
        child=serializers.CharField(allow_null=True), required=False, allow_empty=True
    )
    language = serializers.ListField(
        child=serializers.CharField(allow_null=True), required=False, allow_empty=True
    )

    class Meta:
        model = Expression
        fields = [
            "title",
            "subtitle",
            "edition",
            "edition_type",
            "language",
            "publication_date",
            "publisher",
            "place_of_publication",
        ]


class PersonDataSerializer(MarkdownSerializerMixin):
    uris = serializers.ListField(
        required=False, allow_empty=True, child=serializers.URLField()
    )
    relation_type = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Person
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class ExpressionDataDetailSerializer(ExpressionDataSerializer):
    publisher = NameAndIdSerializer(required=False, allow_null=True)
    place_of_publication = PlaceDataSerializerMin(
        required=False, allow_null=True, many=True
    )
    persons = PersonDataSerializer(required=False, allow_null=True, many=True)

    class Meta:
        model = Expression
        fields = [
            "title",
            "subtitle",
            "edition",
            "edition_type",
            "language",
            "publication_date",
            "publisher",
            "place_of_publication",
            "persons",
        ]


class PersonDataMinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()


class WorkPreviewSerializer(serializers.ModelSerializer):
    expression_data = ExpressionDataSerializer(required=False, many=True)
    work_type = WorkTypeDataSerializer(required=False, allow_empty=True, many=True)
    work_type_root = serializers.SerializerMethodField()
    authors = PersonDataMinSerializer(required=False, allow_empty=True, many=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "siglum",
            "title",
            "subtitle",
            "authors",
            "expression_data",
            "work_type",
            "work_type_root",
        ]

    @extend_schema_field(
        {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
            "nullable": True,
        }
    )
    def get_work_type_root(self, object):
        if len(object.work_type) == 0:
            return None
        work_type = object.work_type[0]
        while work_type["parent"]:
            work_type = get_work_type_data(work_type["parent"])
        return {"id": work_type["id"], "name": work_type["name"]}


class MetacharacterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)


class CharacterDataSerializer(MarkdownSerializerMixin):
    fictionality = serializers.ListField(
        child=serializers.CharField(allow_null=True), required=False, allow_empty=True
    )
    metacharacter = MetacharacterSerializer(allow_null=True)

    class Meta:
        model = Character
        fields = [
            "id",
            "forename",
            "surname",
            "fallback_name",
            "alternative_name",
            "description",
            "relevancy",
            "fictionality",
            "metacharacter",
        ]


class ArchiveDataSerializer(MarkdownSerializerMixin):
    website = serializers.CharField(required=False, max_length=255, label="Webseite")

    class Meta:
        model = Archive
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class PhysicalObjectDataSerializer(MarkdownSerializerMixin):
    archive = ArchiveDataSerializer(required=False, allow_null=True)

    class Meta:
        model = PhysicalObject
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class SourceDataSerializer(MarkdownSerializerMixin):
    authors = AuthorDataSerializer(many=True, allow_empty=True, required=False)

    class Meta:
        model = Work
        fields = ["id", "title", "subtitle", "authors"]


class TopicDataSerializer(MarkdownSerializerMixin):
    class Meta:
        model = Topic
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class InterpretatemDataSerializer(MarkdownSerializerMixin):
    sources = SourceDataSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = Interpretatem
        fields = ["id", "description", "sources"]


class RelatedWorksDataSerializer(RelatedWorksMinDataSerializer):
    relation_type = serializers.CharField(required=False)

    class Meta(RelatedWorksMinDataSerializer.Meta):
        model = Work
        fields = ["id", "title", "subtitle", "relation_type", "authors"]


class WorkDetailSerializer(MarkdownSerializerMixin):
    work_type = WorkTypeDataSerializer(required=False, allow_empty=True, many=True)
    expression_data = ExpressionDataDetailSerializer(
        required=False, allow_empty=True, many=True
    )
    related_works = RelatedWorksDataSerializer(
        source="combined_work_relations", many=True, allow_empty=True, required=False
    )
    characters = CharacterDataSerializer(
        source="related_characters",
        required=False,
        allow_empty=True,
        many=True,
    )
    physical_objects = PhysicalObjectDataSerializer(
        source="related_physical_objects",
        required=False,
        allow_empty=True,
        many=True,
    )
    topics = TopicDataSerializer(
        source="related_topics",
        required=False,
        allow_empty=True,
        many=True,
    )
    persons = PersonDataSerializer(
        source="related_persons",
        required=False,
        allow_empty=True,
        many=True,
    )
    places = PlaceDataSerializer(
        source="related_places",
        required=False,
        allow_empty=True,
        many=True,
    )
    interpretatems = InterpretatemDataSerializer(
        source="related_interpretatems", required=False, allow_empty=True, many=True
    )

    class Meta:
        model = Work
        exclude = [
            "self_contenttype",
            "data_source",
            "notes",
            "progress_status",
        ]


class RelWorkMinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=255, allow_null=True)
    authors = AuthorDataSerializer(many=True, allow_empty=True)


class PlaceDetailDataSerializer(MarkdownSerializerMixin):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Place
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class ResearchPerspectiveDetailDataSerializer(MarkdownSerializerMixin):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = ResearchPerspective
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class TopicDetailDataSerializer(MarkdownSerializerMixin):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Topic
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class MetaCharacterDetailSerializer(MarkdownSerializerMixin):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = MetaCharacter
        exclude = ["self_contenttype", "data_source", "progress_status"]


class GlossarDetailDataSerializer(MarkdownSerializerMixin):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Glossar
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class CharacterDetailSerializer(MarkdownSerializerMixin):
    uris = serializers.ListField(
        required=False, allow_empty=True, child=serializers.URLField()
    )

    class Meta:
        model = Character
        exclude = [
            "self_contenttype",
            "data_source",
        ]
