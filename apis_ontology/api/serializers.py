"""
Serializers for custom API.

I.e. project-specific endpoints (not APIS built-in API).
"""
from rest_framework import serializers

from apis_ontology.models import Work


class WorkPreviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Work
        fields = ["title", "subtitle"]
