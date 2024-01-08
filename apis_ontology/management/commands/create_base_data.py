import os
from django.core.management.base import BaseCommand
from apis_core.apis_relations.models import Property
from apis_ontology.models import Archive, Person, WorkType
from apis_ontology.import_related.additional_infos import ARCHIVES, PERSONS, WORK_TYPES
from apis_ontology.import_related.import_helpers import create_triple, create_source

fname = os.path.basename(__file__)


def create_archives(calling_file=fname):
    """
    Create objects for Archive entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """
    import_name = "Archives_Import"

    for a in ARCHIVES:
        # for archives, save XML file as pubinfo when creating sources
        # for later reference
        source, created = create_source(import_name, metadata=a["source_file"])
        Archive.objects.get_or_create(
            name=a["name"],
            defaults={"data_source": source},
        )


def create_persons(calling_file=fname):
    """
    Create objects for Person entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """
    import_name = "Persons_Import"
    source, created = create_source(import_name, metadata=calling_file)

    for p in sorted(PERSONS, key=lambda d: d["id"]):
        Person.objects.get_or_create(
            name=p["name"],
            first_name=p["first_name"],
            last_name=p["last_name"],
            defaults={"data_source": source},
        )


def create_types(calling_file=fname):
    """
    Create objects for WorkType entity.

    :param calling_file: optional argument to pass filename of the calling
                         script, otherwise uses this file's name
    """
    import_name = "WorkTypes_Import"
    source, created = create_source(import_name, metadata=calling_file)

    # types with parents, not top-level types
    children = {key: val for (key, val) in WORK_TYPES.items() if val["parent_key"]}

    # create objects for all types
    for work_type in WORK_TYPES.values():
        wtype, created = WorkType.objects.get_or_create(
            name=work_type["german_label"],
            name_plural=work_type["german_label_plural"],
            defaults={"data_source": source},
        )

    for work_type in children.values():
        wt_object = WorkType.objects.get(name=work_type["german_label"])
        parent_key = work_type["parent_key"]
        parent_object = WorkType.objects.get(name=WORK_TYPES[parent_key]["german_label"])
        create_triple(
            entity_subj=wt_object,
            entity_obj=parent_object,
            prop=Property.objects.get(name="has broader term"),
        )

class Command(BaseCommand):

    def handle(self, *args, **options):
        create_archives()
        create_persons()
        create_types()