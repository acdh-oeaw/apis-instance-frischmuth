import xml.etree.ElementTree as ET
import copy

from .additional_infos import MISC_ENTITIES

# from django.core.validators import URLValidator
from apis_core.apis_metainfo.models import Uri
from apis_core.apis_relations.models import Property
from apis_ontology.models import (
    Character,
    Person,
    Place,
    Work,
    Topic,
    ResearchPerspective,
)
from .utils import secure_urls
from .import_helpers import create_triple, create_source


def get_text_by_elementpath(element, element_child_name):
    """
    Helper function to get a cleaned string from an XML element
    (as used in the auxiliary files).
    """
    if element.find(element_child_name) is not None:
        # strip because import data isn't clean (leading, trailing spaces)
        if element.find(element_child_name).text:
            stripped = element.find(element_child_name).text.strip()
            if stripped != "":
                return stripped


def create_entities_from_xml(tree, entity_plural, path, source):
    """Helper function to create entities related to works"""

    # Mappings for fixed property values and values used in excel
    RELEVANCIES = {
        "H": "protagonist",
        "N": "supporting_character",
        "E": "referenced_character",
    }

    WORK_PLACE_RELATIONTYPES = {
        "E": "mentions",
        "S": "takes place in",
        "A": "discusses",
    }

    FICTIONALITY_DEGREES = {
        "F": "fictional_character",
        "M": "mythical_character",
        "R": "historical_character",
        "M/R": ["mythical_character", "historical_character"],
    }

    # Create a Character for each row in Names sheet for the given siglum
    if entity_plural == "Names":
        for name_entity in tree.findall(path):
            fictionality = None
            fictionality_type = get_text_by_elementpath(name_entity, "kategorie")
            name = get_text_by_elementpath(name_entity, "name")
            description = get_text_by_elementpath(name_entity, "beschreibung")
            character_role = get_text_by_elementpath(name_entity, "rolle")
            relevancy = RELEVANCIES.get(character_role)
            notes = get_text_by_elementpath(name_entity, "notiz")
            name_url_fields = ["id1", "id2", "idr"]
            name_urls = [
                get_text_by_elementpath(name_entity, u)
                for u in name_url_fields
                if get_text_by_elementpath(name_entity, u)
            ]

            if fictionality_type in FICTIONALITY_DEGREES:
                fictionality = FICTIONALITY_DEGREES[fictionality_type]

            character = Character.objects.create(
                name=name,
                description=description,
                fictionality=fictionality,
                relevancy=relevancy,
                notes=notes,
                source=source,
            )

            # Create Person entity, if name refers to real or mythical Person
            if fictionality_type in ("R", "M", "M/R"):
                uris = []
                for uri in name_urls:
                    uri = secure_urls(uri)
                    uri_obj, uri_created = Uri.objects.get_or_create(uri=uri)
                    uris.append(uri_obj)

                person = None
                person_qs = None

                if len(uris) > 0:
                    person_qs = Person.objects.filter(
                        uri__in=[uri.id for uri in uris],
                    )
                else:
                    person_qs = Person.objects.filter(name=name)

                if person_qs.count() == 0:
                    person, created = Person.objects.get_or_create(
                        name=name,
                        defaults={"source": source},
                    )
                else:
                    person = person_qs.first()

                if len(uris) > 0 and name != person.name:
                    person_names = person.name.split("; ")

                    if name not in person_names:
                        person.name += f"; {name}"
                        person.save()

                for uri in uris:
                    if not uri.root_object:
                        uri.root_object = person
                        uri.save()

                create_triple(
                    entity_subj=character,
                    entity_obj=person,
                    prop=Property.objects.get(name="is based on"),
                )

            specified_siglum = name_entity.find("werk").text.strip()
            if Work.objects.filter(siglum=specified_siglum).exists():
                work_object = Work.objects.get(siglum=specified_siglum)
                # Create relation triple between Work and Character
                create_triple(
                    entity_subj=work_object,
                    entity_obj=character,
                    prop=Property.objects.get(name="features"),
                )

    # Create a Place for each row in Places sheet for the given siglum
    if entity_plural == "Places":
        for place_entity in tree.findall(path):
            place_name = get_text_by_elementpath(place_entity, "ort")
            place_type = get_text_by_elementpath(place_entity, "kategorie")
            place_url_fields = ["id1", "id2", "idr"]
            place_urls = [
                get_text_by_elementpath(place_entity, u)
                for u in place_url_fields
                if get_text_by_elementpath(place_entity, u)
            ]
            uris = []

            for uri in place_urls:
                uri = secure_urls(uri)
                uri_obj, uri_created = Uri.objects.get_or_create(uri=uri)
                uris.append(uri_obj)

            place = None
            place_qs = None

            if len(uris) > 0:
                place_qs = Place.objects.filter(
                    uri__in=[uri.id for uri in uris],
                )
            else:
                place_qs = Place.objects.filter(name=place_name)

            if place_qs.count() == 0:
                place, created = Place.objects.get_or_create(
                    name=place_name,
                    defaults={"source": source},
                )
            else:
                place = place_qs.first()

            if len(uris) > 0 and place != place.name:
                places = place.name.split("; ")

                if place_name not in places:
                    place.name += f"; {place_name}"
                    place.save()

            for uri in uris:
                if not uri.root_object:
                    uri.root_object = place
                    uri.save()

            # place.collection.add(collection)
            specified_siglum = place_entity.find("werk").text.strip()
            if Work.objects.filter(siglum=specified_siglum).exists():
                work_object = Work.objects.get(siglum=specified_siglum)

            create_triple(
                entity_subj=work_object,
                entity_obj=place,
                prop=Property.objects.get(name=WORK_PLACE_RELATIONTYPES[place_type]),
            )

    # Create a Topic for each row in Topics (Themen) sheet for the given siglum
    if entity_plural == "Topics":
        for topic_entity in tree.findall(path):
            topic_name = get_text_by_elementpath(topic_entity, "thema")
            alt_name = get_text_by_elementpath(topic_entity, "synonyme")
            note = get_text_by_elementpath(topic_entity, "anmerkung")
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                alternative_names=alt_name,
                notes=note,
                defaults={"source": source},
            )

            specified_siglum = topic_entity.find("werk").text.strip()
            if Work.objects.filter(siglum=specified_siglum).exists():
                work_object = Work.objects.get(siglum=specified_siglum)

                create_triple(
                    entity_subj=work_object,
                    entity_obj=topic,
                    prop=Property.objects.get(name="is about topic"),
                )

    # Create a ResearchPerspective for each row in Forschungshinsichten sheet for the given siglum
    if entity_plural == "ResearchPerspectives":
        for res_persp_entity in tree.findall(path):
            topic_name = get_text_by_elementpath(res_persp_entity, "thema")
            notes = get_text_by_elementpath(res_persp_entity, "anmerkung")

            research_perspective, created = ResearchPerspective.objects.get_or_create(
                name=topic_name,
                notes=notes,
                defaults={"source": source},
            )

            specified_siglum = res_persp_entity.find("werk").text.strip()
            if Work.objects.filter(siglum=specified_siglum).exists():
                work_object = Work.objects.get(siglum=specified_siglum)
                create_triple(
                    entity_subj=work_object,
                    entity_obj=research_perspective,
                    prop=Property.objects.get(name="applies research perspective"),
                )


def run():
    """
    Create Entities and Triples by iterating through xml-data
    """
    for e in MISC_ENTITIES:
        import_name = "Nonbib_Entities"

        # load and parse auxiliary XML files derived from Excel sheets
        aux_file = open(
            e["source_file"],
            "r",
            encoding="utf-8",
        )
        root_entities = ET.parse(aux_file)

        import_name += f"_{e['entity_plural']}_Import"
        # use XML file for entity source pubinfo
        source = create_source(import_name, e["source_file"])

        create_entities_from_xml(root_entities, e["entity_plural"], e["path"], source)
