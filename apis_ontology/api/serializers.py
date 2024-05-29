"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""

from rest_framework import serializers

from apis_ontology.models import Expression, Work, WorkType


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
        child=serializers.CharField(allow_blank=True), required=False, allow_empty=True
    )
    edition_type = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()

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

    def get_edition_type(self, obj):
        edition_type_str = obj.get("edition_type", None)
        edition_types = list(filter(None, edition_type_str.split(",")))
        return get_choices_labels(edition_types, Expression.EditionTypes)

    def get_language(self, obj):
        language_str = obj.get("language", None)
        languages = list(filter(None, language_str.split(",")))
        return get_choices_labels(languages, Expression.LanguagesIso6393)


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
