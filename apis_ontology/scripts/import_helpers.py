import datetime
import inspect
import os
import sys
import re

from apis_core.apis_relations.models import TempTriple, Property
from apis_ontology.models import (
    Archive,
    DataSource,
    Expression,
    Organisation,
    Person,
    Place,
    Work,
    WorkType,
    Topic,
)


def create_triple(entity_subj, entity_obj, prop):
    """
    Helper function for creating APIS Ontologies triples.

    Initial code bluntly taken from Jelinek project.
    """

    triple, created = TempTriple.objects.get_or_create(
        subj=entity_subj, obj=entity_obj, prop=prop
    )

    return triple, created


def create_source(
    name: str,
    file_name: str = None,
    data_type: str = None,
    author: str = None,
    provider: str = None,
):
    """
    Helper function for creating a DataSource object by which
    individual data imports can be identified.

    Useful for e.g. later removal of objects created during
    specific imports.

    :param name: base name of import source,
                 used for DataSource "file_name" field
    :param separator: word separator
    :param metadata: should hold more information about import source, defaults
                     to name of calling script if not provided; used for
                     DataSource "pubinfo" field
    :param author: used for DataSource "author" field
    :param with_date: boolean, determines if datetime of import script
                      execution should be appended to DataSource name
    :return:
    """
    # script from which create_source is called
    calling_script = os.path.basename(inspect.getsourcefile(sys._getframe(1)))

    added_date = datetime.datetime.now()

    if not author:
        # required field for DataSource, cannot be empty
        author = ""

    if not provider:
        # required field for DataSource, cannot be empty
        provider = ""

    source_obj, created = DataSource.objects.get_or_create(
        name=name,
        file_name=file_name,
        added_date=added_date,
        data_type=data_type,
        provider=provider,
        author=author,
        added_by=calling_script,
    )

    return source_obj, created


def create_work(title: str, subtitle: str, siglum: str, source: DataSource):
    """
    Create a new Work entity object if one with the sigle parameter
    does not exist yet.

    :param title: main title of the Work, used for "name" field
    :param siglum: unique identifier for Work objects
    :param source: DataSource object to link to, used to identify data imports
    :return: Work object
    """

    if siglum:
        work, created = Work.objects.get_or_create(
            siglum=siglum,
        )

        if created:
            work.title = title
            work.subtitle = subtitle
            work.data_source = source
            work.save()
    else:
        work = Work.objects.create(title=title, subtitle=subtitle, data_source=source)
        created = True

    return work, created


def get_work(siglum: str):
    """
    :return: Work object or None
    """
    work = None

    try:
        work = Work.objects.get(
            siglum=siglum,
        )
    except Exception:
        pass

    return work


def get_type(title: str):
    """
    :return: WorkType object or None
    """
    work_type = None

    try:
        work_type = WorkType.objects.get(
            name=title,
        )
    except Exception:
        pass

    return work_type


def create_expression(
    title: str,
    subtitle: str,
    pub_date: str,
    source: DataSource,
    relevant_pages: str,
    page_count: int = None,
    edition_types: list = None,
):
    """
    Create a new Expression entity object if one with the given parameters
    does not exist yet.

    :param title: full title of the Expression, used for "name" field
    :param pub_date: date object
    :param source: DataSource object to link to, used to identify data imports
    :param pages: number of pages
    :param man_types: type(s) of manifestation, if any; can be string
                    or list of strings
    :return: Expression object
    """
    expression, created = Expression.objects.get_or_create(
        title=title,
        subtitle=subtitle,
        edition_type=edition_types,
        page_count=page_count,
        relevant_pages=relevant_pages,
        defaults={"data_source": source},
    )
    if pub_date:
        expression.publication_date_manual_input = pub_date
        expression.save()

    return expression, created


def create_person(person_data: dict, source: DataSource):
    """
    Create a new Person entity object if one with the given parameters
    does not exist yet.

    Primarily used to create new authors of works.

    :param person_data: dict containing keys/values holding information
                        about a person's name
    :param source: DataSource object to link to, used to identify data imports
    :return: Person object
    """
    # Zotero uses fields "lastName" and "firstName" for creators
    full_name = person_data.get("name", person_data.get("full_name", None))
    first_name = person_data.get("first_name", person_data.get("firstName", None))
    last_name = person_data.get("last_name", person_data.get("lastName", None))
    fallback_name = ""

    if full_name and full_name == "":
        full_name = None
    if first_name and first_name == "":
        first_name = None
    if last_name and last_name == "":
        last_name = None

    if not full_name:
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif last_name:
            full_name = last_name
            if re.match("[a-zA-Z]+\.", last_name):
                fallback_name = last_name
                last_name = ""
        elif first_name:
            full_name = first_name
        else:
            # TODO log as error instead of exiting program
            "Missing name to look up or create Person, exiting."
            exit(1)
    else:
        # rudimentary way of determining first name and last name from
        # a person's full name
        if not first_name and not last_name:
            name_parts = full_name.split()
            if len(name_parts) > 1:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])

    person, created = Person.objects.get_or_create(
        fallback_name=fallback_name,
        forename=first_name,
        surname=last_name,
        defaults={"data_source": source},
    )

    return person, created


def create_organisation(org_name: str, source: DataSource):
    """
    Create a new Organisation entity object if one with the given parameters
    does not exist yet.

    Primarily used to create new publishers.

    :param org_name: name of an organisation, used for "name" field
    :param source: DataSource object to link to, used to identify data imports
    :return: Organisation object
    """
    organisation, created = Organisation.objects.get_or_create(
        name=org_name,
        defaults={"data_source": source},
    )

    return organisation, created


def create_place(place_name: str, source: DataSource):
    """
    Create a new Place entity object if one with the given parameters
    does not exist yet.

    Used for creating places of publication as well as office addresses for
    publishers.

    :param place_name: name of a place, used for "name" field
    :param source: DataSource object to link to, used to identify data imports
    :param place_type: can be used to addd notes about a place, e.g. to
                       add a separate place object for a place of publication
                       or a publisher's address; gets added to "notes" field
    :return: Place object
    """
    place, created = Place.objects.get_or_create(
        name=place_name,
        defaults={"data_source": source},
    )

    return place, created


def create_archive(archive_name: str, source: DataSource):
    """
    Create a new Archive entity object if one with the given parameters
    does not exist yet.

    :param archive_name: name of an archive, used for "name" field
    :param source: DataSource object to link to, used to identify data imports
    :return: Archive object
    """
    archive, created = Archive.objects.get_or_create(
        name=archive_name,
        defaults={"data_source": source},
    )

    return archive, created


def create_topic(topic_name: str, source: DataSource):
    """
    Create a new Topic entity object if one with the given parameters
    does not exist yet.

    :param topic_name: name of an topic, used for "name" field
    :param source: DataSource object to link to, used to identify data imports
    :return: Topic object
    """
    archive, created = Topic.objects.get_or_create(
        name=topic_name,
        defaults={"data_source": source},
    )

    return archive, created


def get_expressions_by_work(work_id: int):
    prop = Property.objects.get(name_forward="is realised in")
    related_expressions = [
        i.obj for i in TempTriple.objects.filter(subj__id=work_id, prop=prop)
    ]
    return related_expressions


def work_with_siglum_exists(siglum):
    return Work.objects.filter(siglum=siglum).exists()
