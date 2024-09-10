"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from typing import TypedDict

from rest_framework import serializers

from apis_ontology.models import (
    Archive,
    Character,
    Expression,
    Person,
    PhysicalObject,
    Place,
    Topic,
    Work,
    WorkType,
)


def get_choices_labels(values: list, text_choices):
    """
    Return labels for enumeration type TextChoices.

    :param values: an array of (valid) TextChoices values
    :param text_choices: the TextChoices class against which to match the values
    :return: a list of labels
    """
    labels = []

    for v in values:
        labels.append(text_choices(v).label)

    return labels


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
    place_of_publication = PlaceDataSerializer(
        required=False, allow_null=True, many=True
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


class SimpleDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ExpressionDataDetailSerializer(ExpressionDataSerializer):
    publisher = SimpleDetailSerializer(required=False, allow_null=True)
    place_of_publication = PlaceDataSerializerMin(
        required=False, allow_null=True, many=True
    )


class WorkPreviewSerializer(serializers.ModelSerializer):
    expression_data = ExpressionDataSerializer(required=False, many=True)
    work_type = WorkTypeDataSerializer(required=False, allow_empty=True, many=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "siglum",
            "title",
            "subtitle",
            "expression_data",
            "work_type",
        ]


class RelatedWorksDict(TypedDict):
    id: int
    title: str
    subtitle: str | None
    relation_type: str


class CharacterDataSerializer(serializers.ModelSerializer):
    fictionality = serializers.ListField(
        child=serializers.CharField(allow_null=True), required=False, allow_empty=True
    )

    class Meta:
        model = Character
        fields = [
            "forename",
            "surname",
            "fallback_name",
            "alternative_name",
            "description",
            "relevancy",
            "fictionality",
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


class TopicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = [
            "self_contenttype",
            "data_source",
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


class WorkDetailSerializer(serializers.ModelSerializer):
    work_type = WorkTypeDataSerializer(required=False, allow_empty=True, many=True)
    expression_data = ExpressionDataDetailSerializer(
        required=False, allow_empty=True, many=True
    )
    related_works = serializers.SerializerMethodField()
    characters = CharacterDataSerializer(
        source="character_data",
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

    class Meta:
        model = Work
        exclude = [
            "self_contenttype",
            "data_source",
            "notes",
            "progress_status",
        ]

    def get_related_works(self, obj) -> list[RelatedWorksDict]:
        return list(obj.forward_work_relations) + list(obj.reverse_work_relations)
