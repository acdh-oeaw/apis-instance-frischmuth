"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""
from rest_framework import serializers

from apis_ontology.models import Expression, Work


class ExpressionSerializer(serializers.ModelSerializer):
    publication_date = serializers.CharField()

    class Meta:
        model = Expression
        fields = [
            "edition",
            "edition_type",
            "publication_date",
        ]


class WorkPreviewSerializer(serializers.ModelSerializer):
    expression_data = ExpressionSerializer(required=False, many=True)

    class Meta:
        model = Work
        fields = [
            "title",
            "subtitle",
            "expression_data",
        ]
