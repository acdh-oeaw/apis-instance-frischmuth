import os
import pandas as pd
import logging
from apis_ontology.scripts.access_sharepoint import import_and_parse_data
from .import_helpers import create_triple, create_source, work_with_siglum_exists
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

logger = logging.getLogger(__name__)

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
    file_name = os.path.basename(file)
    data_source, created = create_source(
        name="NonBiblEntities",
        file_name=file_name,
        data_type="xslx",
    )
    for index, row in df.iterrows():
        if sheet_name == "Orte":
            place_name = row["Name_im_Werk"]
            related_work_siglum = row["Sigle"]
            place_type = row["Kategorie"]
            place_description = row["Beschreibung"]
            place_uris = (row["URL_Geonames"], row["URL_Wikipedia"], row["URL_extern"])
            place_uri_objects = []

            if work_with_siglum_exists(related_work_siglum):
                for place_uri in place_uris:
                    if place_uri:
                        secure_uri = secure_urls(place_uri)
                        if secure_uri:
                            uri, created = Uri.objects.get_or_create(uri=secure_uri)
                            place_uri_objects.append(uri)
                        else:
                            logger.info(
                                f"Non-valid input for uri. {place_uri} place name: {place_name}"
                            )

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
                    place_description_info = (
                        f": {place_description}" if place_description else ""
                    )
                    triple.notes = f"{place_name}{place_description_info}"
                    triple.save()

            else:
                rejection_cause_message = (
                    f"Work with sigle {related_work_siglum} doesn't exist."
                    if related_work_siglum
                    else "No sigle was provided."
                )
                logger.info(
                    f"{rejection_cause_message} Place import was rejected. File: {file_name}. Sheet: {sheet_name}. Entity name: {place_name}"
                )

        if sheet_name == "Namen":
            character_name = row["Name"]
            forename = row["Vorname"]
            surname = row["Nachname"]
            person_alternative_name = row["alternativeName"]
            description = row["Beschreibung"]
            character_relevancy = RELEVANCIES.get(row["Rolle"], "")
            character_fictionality = row["Kategorie"]
            character_fictionality_degree = FICTIONALITY_DEGREES[character_fictionality]
            related_work_siglum = row["Sigle"]
            person_uris = (row["URL_Wikipedia"], row["URL_DNB"], row["URL_extern"])

            if work_with_siglum_exists(related_work_siglum):
                character = Character.objects.create(
                    fallback_name=character_name,
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

                    person_fallback_name = (
                        character_name if not (forename or surname) else ""
                    )

                    if len(person_uri_objects) > 0:
                        person_qs = Person.objects.filter(
                            uri__in=[uri.id for uri in person_uri_objects],
                        )
                    else:
                        person_qs = Person.objects.filter(
                            fallback_name=person_fallback_name,
                            forename=forename,
                            surname=surname,
                        )

                    if person_qs.count() == 0:
                        person, created = Person.objects.get_or_create(
                            fallback_name=person_fallback_name,
                            forename=forename,
                            surname=surname,
                            alternative_name=person_alternative_name,
                            description=description,
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
                else:
                    character.description = description
                    character.forename = forename
                    character.surname = surname
                    character.save()

            else:
                rejection_cause_message = (
                    f"Work with sigle {related_work_siglum} doesn't exist."
                    if related_work_siglum
                    else "No sigle was provided."
                )
                logger.info(
                    f"{rejection_cause_message} Character/Person import was rejected. File: {file_name}. Sheet: {sheet_name}. Entity name: {character_name}"
                )

        if sheet_name == "Themen":
            topic_name = row["Thema"]
            related_work_siglum = row["Sigle"]
            topic_alt_name = row["Synonyme"]

            if work_with_siglum_exists(related_work_siglum):
                topic, created = Topic.objects.get_or_create(
                    name=topic_name,
                    defaults={"data_source": data_source},
                )
                topic.alternative_name = topic_alt_name
                topic.save()

                if Work.objects.filter(siglum=related_work_siglum).exists():
                    work_object = Work.objects.get(siglum=related_work_siglum)

                    create_triple(
                        entity_subj=work_object,
                        entity_obj=topic,
                        prop=Property.objects.get(name_forward="is about topic"),
                    )

            else:
                rejection_cause_message = (
                    f"Work with sigle {related_work_siglum} doesn't exist."
                    if related_work_siglum
                    else "No sigle was provided."
                )
                logger.info(
                    f"{rejection_cause_message} Topic import was rejected. File: {file_name}. Sheet: {sheet_name}. Entity name: {topic_name}"
                )

        if sheet_name == "Forschungshinsichten":
            research_perspective_name = row["Thema"]
            related_work_siglum = row["Sigle"]

            if work_with_siglum_exists(related_work_siglum):
                (
                    research_perspective,
                    created,
                ) = ResearchPerspective.objects.get_or_create(
                    name=research_perspective_name,
                    defaults={"data_source": data_source},
                )

                if Work.objects.filter(siglum=related_work_siglum).exists():
                    work_object = Work.objects.get(siglum=related_work_siglum)

                    create_triple(
                        entity_subj=work_object,
                        entity_obj=research_perspective,
                        prop=Property.objects.get(
                            name_forward="applies research perspective"
                        ),
                    )
            else:
                rejection_cause_message = (
                    f"Work with sigle {related_work_siglum} doesn't exist."
                    if related_work_siglum
                    else "No sigle was provided."
                )
                logger.info(
                    f"{rejection_cause_message} ResearchPerspective import was rejected. File: {file_name}. Sheet: {sheet_name}. Entity name: {research_perspective_name}"
                )
