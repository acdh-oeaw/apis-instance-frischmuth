from apis_core.generic.importers import GenericImporter
from apis_core.utils.rdf import get_definition_and_attributes_from_uri

from apis_ontology.models import Organisation, Person, Place


class PlaceImporter(GenericImporter):
    def request(self, uri):
        model, data = get_definition_and_attributes_from_uri(uri, Place)
        return data


class PersonImporter(GenericImporter):
    def request(self, uri):
        model, data = get_definition_and_attributes_from_uri(uri, Person)
        return data


class InstitutionImporter(GenericImporter):
    def request(self, uri):
        model, data = get_definition_and_attributes_from_uri(uri, Organisation)
        return data
