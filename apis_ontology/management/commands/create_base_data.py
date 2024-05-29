import os

from apis_core.apis_relations.models import Property
from django.core.management.base import BaseCommand

from apis_ontology.models import Archive, Person, WorkType
from apis_ontology.scripts.additional_infos import ARCHIVES, PERSONS, WORK_TYPES
from apis_ontology.scripts.import_helpers import create_source, create_triple


fname = os.path.basename(__file__)
data_source, created = create_source(
    name="BaseEntitiesSource", file_name="additional_infos.py", data_type="python"
)


def create_archives(calling_file=fname):
    """
    Create objects for Archive entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """

    for a in ARCHIVES:
        # for archives, save XML file as pubinfo when creating sources
        # for later reference
        Archive.objects.get_or_create(
            name=a["name"],
            data_source=data_source,
        )


def create_persons(calling_file=fname):
    """
    Create objects for Person entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """

    for p in sorted(PERSONS, key=lambda d: d["id"]):
        Person.objects.get_or_create(
            forename=p["first_name"], surname=p["last_name"], data_source=data_source
        )


def create_types(calling_file=fname):
    """
    Create objects for WorkType entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """

    # types with parents, not top-level types
    children = {key: val for (key, val) in WORK_TYPES.items() if val["parent_key"]}

    # create objects for all types
    for work_type in WORK_TYPES.values():
        wtype, created = WorkType.objects.get_or_create(
            name=work_type["german_label"],
            name_plural=work_type["german_label_plural"],
            data_source=data_source,
        )

    for work_type in children.values():
        wt_object = WorkType.objects.get(name=work_type["german_label"])
        parent_key = work_type["parent_key"]
        parent_object = WorkType.objects.get(
            name=WORK_TYPES[parent_key]["german_label"]
        )
        create_triple(
            entity_subj=wt_object,
            entity_obj=parent_object,
            prop=Property.objects.get(name_forward="has broader term"),
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_archives()
        create_persons()
        create_types()
