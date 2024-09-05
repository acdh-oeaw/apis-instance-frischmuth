import logging
import os

from apis_core.utils.autocomplete import (
    ExternalAutocomplete,
    LobidAutocompleteAdapter,
    TypeSenseAutocompleteAdapter,
)


logger = logging.getLogger(__name__)


class PlaceExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        TypeSenseAutocompleteAdapter(
            collections=[
                "prosnet-wikidata-place-index",
                "prosnet-geonames-place-index",
            ],
            template="apis_ontology/place_external_autocomplete_result.html",
            token=os.getenv("TYPESENSE_TOKEN", None),
            server=os.getenv("TYPESENSE_SERVER", None),
        ),
        LobidAutocompleteAdapter(
            params={
                "filter": "type:PlaceOrGeographicName",
                "format": "json:preferredName",
            }
        ),
    ]


class PersonExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        TypeSenseAutocompleteAdapter(
            collections="prosnet-wikidata-person-index",
            template="apis_ontology/generic_external_autocomplete_result.html",
            token=os.getenv("TYPESENSE_TOKEN", None),
            server=os.getenv("TYPESENSE_SERVER", None),
        ),
        LobidAutocompleteAdapter(
            template="apis_ontology/generic_external_autocomplete_result.html",
            params={
                "filter": "type:Person",
                "format": "json:preferredName,*_dateOfBirth,†_dateOfDeath,professionOrOccupation",
            },
        ),
    ]


class OrganisationExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        TypeSenseAutocompleteAdapter(
            collections="prosnet-wikidata-organization-index",
            template="apis_ontology/generic_external_autocomplete_result.html",
            token=os.getenv("TYPESENSE_TOKEN", None),
            server=os.getenv("TYPESENSE_SERVER", None),
        ),
        LobidAutocompleteAdapter(
            template="apis_ontology/generic_external_autocomplete_result.html",
            params={"filter": "type:CorporateBody", "format": "json:preferredName"},
        ),
    ]
