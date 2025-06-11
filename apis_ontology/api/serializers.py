"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

import re

import markdown
from apis_core.history.models import RootObject
from django.contrib.postgres.expressions import Subquery
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


class MarkdownField(serializers.CharField):
    def to_representation(self, value):
        md = re.sub(
            r"(?<=\()[0-9]+(?=\))",
            lambda txt: RootObject.objects_inheritance.get_subclass(
                pk=txt.group()
            ).get_frontend_url()
            or txt.group(),
            value,
        )
        html = markdown.markdown(md)
        return html


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


class NameAndIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class PlaceDataSerializerMin(serializers.ModelSerializer):
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


class WorkTypeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = [
            "name",
            "name_plural",
        ]


class ExpressionDataSerializer(serializers.ModelSerializer):
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


class PersonDataSerializer(serializers.ModelSerializer):
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


class CharacterDataSerializer(serializers.ModelSerializer):
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


class ArchiveDataSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, max_length=255, label="Webseite")

    class Meta:
        model = Archive
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class PhysicalObjectDataSerializer(serializers.ModelSerializer):
    archive = ArchiveDataSerializer(required=False, allow_null=True)

    class Meta:
        model = PhysicalObject
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class AuthorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "forename", "surname", "fallback_name"]


class SourceDataSerializer(serializers.ModelSerializer):
    authors = AuthorDataSerializer(many=True, allow_empty=True, required=False)

    class Meta:
        model = Work
        fields = ["id", "title", "subtitle", "authors"]


class TopicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class InterpretatemDataSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    sources = SourceDataSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = Interpretatem
        fields = ["id", "description", "sources"]

    def get_description(self, obj) -> str:
        md = obj["description"]
        md = re.sub(
            r"(?<=\()[0-9]+(?=\))",
            lambda txt: RootObject.objects_inheritance.get_subclass(
                pk=txt.group()
            ).get_frontend_url()
            or txt.group(),
            md,
        )
        html = markdown.markdown(md, extensions=["extra"])
        return html


class RelatedWorksDataSerializer(serializers.ModelSerializer):
    relation_type = serializers.CharField(required=False)
    authors = AuthorDataSerializer(many=True, allow_empty=True, required=False)

    class Meta:
        model = Work
        fields = ["id", "title", "subtitle", "relation_type", "authors"]


class WorkDetailSerializer(serializers.ModelSerializer):
    work_type = WorkTypeDataSerializer(required=False, allow_empty=True, many=True)
    expression_data = ExpressionDataDetailSerializer(
        required=False, allow_empty=True, many=True
    )
    related_works = RelatedWorksDataSerializer(
        source="combined_work_relations", many=True, allow_empty=True, required=False
    )
    context = MarkdownField(required=False)
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
    historical_events = MarkdownField(required=False)
    summary = MarkdownField(required=False)
    text_analysis = MarkdownField(required=False)

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


class PlaceDetailDataSerializer(serializers.ModelSerializer):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Place
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class ResearchPerspectiveDetailDataSerializer(serializers.ModelSerializer):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = ResearchPerspective
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class TopicDetailDataSerializer(serializers.ModelSerializer):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Topic
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class MetaCharacterDetailSerializer(serializers.ModelSerializer):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = MetaCharacter
        exclude = ["self_contenttype", "data_source", "progress_status"]


class GlossarDetailDataSerializer(serializers.ModelSerializer):
    related_works = RelWorkMinSerializer(many=True, allow_empty=True)

    class Meta:
        model = Glossar
        exclude = [
            "self_contenttype",
            "data_source",
        ]


class CharacterDetailSerializer(serializers.ModelSerializer):
    uris = serializers.ListField(
        required=False, allow_empty=True, child=serializers.URLField()
    )

    class Meta:
        model = Character
        exclude = [
            "self_contenttype",
            "data_source",
        ]
