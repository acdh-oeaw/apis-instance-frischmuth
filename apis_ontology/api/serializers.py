"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""
from rest_framework import serializers

from apis_ontology.models import Expression, Work, WorkType


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = [
            "name",
            "name_plural",
        ]


class ExpressionSerializer(serializers.ModelSerializer):
    publication_date = serializers.DateField(required=False, allow_null=True)
    publisher = serializers.CharField(required=False, allow_null=True)
    place_of_publication = serializers.ListField(required=False, allow_empty=True
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


class WorkPreviewSerializer(serializers.ModelSerializer):
    expression_data = ExpressionSerializer(required=False, many=True)
    work_type = WorkTypeSerializer(required=False)

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
