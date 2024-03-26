import os
import numpy as np
import pandas as pd
import logging
from apis_ontology.scripts.access_sharepoint import import_and_parse_data
from .import_helpers import create_triple, create_source
from apis_ontology.models import (
    Place,
    Work,
    Topic,
    ResearchPerspective,
    Character,
    Person,
)
from apis_core.apis_metainfo.models import Uri
from apis_core.apis_relations.models import Property
from .utils import secure_urls

WORK_PLACE_RELATIONTYPES = {
    "E": "mentions",
    "S": "takes place in",
    "A": "discusses",
}

RELEVANCIES = {
    "H": "protagonist",
    "N": "supporting_character",
    "E": "referenced_character",
}

FICTIONALITY_DEGREES = {
    "F": "fictional_character",
    "M": "mythical_character",
    "R": "historical_character",
    "M/R": ["mythical_character", "historical_character"],
}


def run():
    import_and_parse_data(parse_entities_excel)


def parse_entities_excel(file):
    success = []
    failure = []

    dfs = pd.read_excel(file, sheet_name=None)
    # remove leading and trailing whitespsaces
    for sheet_name, df in dfs.items():
        # df = dataStorage[names_of_files[i]]
        df_cleaned = df.map(lambda x: x.strip() if isinstance(x, str) else x).fillna(
            value=""
        )
        parse_entities_dataframe(sheet_name, df_cleaned, file)

    return success, failure


def parse_entities_dataframe(sheet_name, df, file):
    data_source, created = create_source(
        name="NonBiblEntities",
        file_name=os.path.basename(file),
        data_type="xslx",
    )
    for index, row in df.iterrows():
        if sheet_name == "Orte":
            place_name = row["ORT"]
            related_work_siglum = row["Sigle"]
            place_type = row["Kategorie"]
            place_description = row["Beschreibung"]
            place_uris = (row["URL_Geonames"], row["URL_Wikipedia"], row["URL_extern"])
            place_uri_objects = []

            for place_uri in place_uris:
                if place_uri:
                    place_uri = secure_urls(place_uri)
                    uri, created = Uri.objects.get_or_create(uri=place_uri)
                    place_uri_objects.append(uri)

            place_qs = None
            place = None

            if len(place_uri_objects) > 0:
                place_qs = Place.objects.filter(
                    uri__in=[uri.id for uri in place_uri_objects],
                )
            else:
                place_qs = Place.objects.filter(name=place_name)

            if place_qs.count() == 0:
                place, created = Place.objects.get_or_create(
                    name=place_name, defaults={"data_source": data_source}
                )
            else:
                place = place_qs.first()
                alternative_names = list(
                    filter(None, place.alternative_name.split(";"))
                )
                if (
                    place_name
                    and place_name != place.name
                    and place_name not in alternative_names
                ):
                    alternative_names.append(place_name)
                    place.alternative_name = ";".join(alternative_names)
                    place.save()

            for uri in place_uri_objects:
                if not uri.root_object:
                    uri.root_object = place
                    uri.save()

            if Work.objects.filter(siglum=related_work_siglum).exists():
                work_object = Work.objects.get(siglum=related_work_siglum)
                triple, created = create_triple(
                    entity_subj=work_object,
                    entity_obj=place,
                    prop=Property.objects.get(
                        name_forward=WORK_PLACE_RELATIONTYPES[place_type]
                    ),
                )

        if sheet_name == "Namen":
            character_name = row["Name"]
            character_forename = row["Vorname"]
            character_surname = row["Nachname"]
            character_alternative_name = row["alternativeName"]
            character_description = row["Beschreibung"]
            character_relevancy = RELEVANCIES.get(row["Rolle"])
            character_fictionality = row["Kategorie"]
            character_fictionality_degree = FICTIONALITY_DEGREES[character_fictionality]
            related_work_siglum = row["Sigle"]
            person_uris = (row["URL_Wikipedia"], row["URL_DNB"], row["URL_extern"])

            character = Character.objects.create(
                fallback_name=character_name,
                forename=character_forename,
                surname=character_surname,
                alternative_name=character_alternative_name,
                description=character_description,
                relevancy=character_relevancy,
                fictionality=character_fictionality_degree,
                data_source=data_source,
            )

            if Work.objects.filter(siglum=related_work_siglum).exists():
                work_object = Work.objects.get(siglum=related_work_siglum)

                create_triple(
                    entity_subj=work_object,
                    entity_obj=character,
                    prop=Property.objects.get(name_forward="features"),
                )

            if character_fictionality in ("R", "M", "M/R"):
                person_uri_objects = []
                for person_uri in person_uris:
                    if person_uri:
                        uri = secure_urls(person_uri)
                        uri_obj, uri_created = Uri.objects.get_or_create(uri=uri)
                        person_uri_objects.append(uri_obj)

                person = None
                person_qs = None

                if len(person_uri_objects) > 0:
                    person_qs = Person.objects.filter(
                        uri__in=[uri.id for uri in person_uri_objects],
                    )
                else:
                    person_qs = Person.objects.filter(
                        fallback_name=character_name,
                        forename=character_forename,
                        surname=character_surname,
                    )

                if person_qs.count() == 0:
                    person_fallback_name = (
                        character_name
                        if not (character_forename or character_surname)
                        else ""
                    )
                    person, created = Person.objects.get_or_create(
                        fallback_name=person_fallback_name,
                        forename=character_forename,
                        surname=character_surname,
                        defaults={"data_source": data_source},
                    )
                else:
                    person = person_qs.first()

                for uri in person_uri_objects:
                    if not uri.root_object:
                        uri.root_object = person
                        uri.save()

                create_triple(
                    entity_subj=character,
                    entity_obj=person,
                    prop=Property.objects.get(name_forward="is based on"),
                )

        if sheet_name == "Themen":
            topic_name = row["Thema"]
            related_work_siglum = row["Sigle"]
            topic_alt_name = row["Synonyme"]
            topic_description = row["Anmerkungen"]
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={"data_source": data_source},
            )
            topic.alternative_name = topic_alt_name
            topic.description = topic_description
            topic.save()

            if Work.objects.filter(siglum=related_work_siglum).exists():
                work_object = Work.objects.get(siglum=related_work_siglum)

                create_triple(
                    entity_subj=work_object,
                    entity_obj=topic,
                    prop=Property.objects.get(name_forward="is about topic"),
                )

        if sheet_name == "Forschungshinsichten":
            research_perspective_name = row["Thema"]
            related_work_siglum = row["Sigle"]
            research_perspective_description = row["Anmerkungen"]

            research_perspective, created = ResearchPerspective.objects.get_or_create(
                name=research_perspective_name,
                defaults={"data_source": data_source},
            )
            research_perspective.description = research_perspective_description
            research_perspective.save()

            if Work.objects.filter(siglum=related_work_siglum).exists():
                work_object = Work.objects.get(siglum=related_work_siglum)

                create_triple(
                    entity_subj=work_object,
                    entity_obj=research_perspective,
                    prop=Property.objects.get(
                        name_forward="applies research perspective"
                    ),
                )
