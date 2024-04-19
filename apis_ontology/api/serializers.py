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
    publication_date = serializers.CharField()

    class Meta:
        model = Expression
        fields = [
            "title",
            "subtitle",
            "edition",
            "edition_type",
            "publication_date",
        ]


class WorkPreviewSerializer(serializers.ModelSerializer):
    expression_data = ExpressionSerializer(required=False, many=True)
    work_type = WorkTypeSerializer(required=False)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "subtitle",
            "expression_data",
            "work_type",
        ]
