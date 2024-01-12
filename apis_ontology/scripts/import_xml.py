import os
import xml.etree.ElementTree as ET

# from django.core.validators import URLValidator
from apis_core.apis_relations.models import Property
from apis_ontology.models import (
    Person,
    Work,
    Archive,
    PhysicalObject,
    Expression,
    WorkType,
)
from .additional_infos import WORK_TYPES, WORKTYPE_MAPPINGS
from .import_helpers import create_triple, create_source
from .create_base_entities import create_archives, create_persons, create_types

fname = os.path.basename(__file__)


def get_text_by_elementpath(element, element_child_name):
    """Helper function to get a cleaned string from an xml-element (as used in the auxiliary files)"""
    # strip because import data isn't clean (leading, trailing spaces)
    if element.find(element_child_name).text:
        return element.find(element_child_name).text.strip()


def run():
    """
    creates Entities and Triples by iterating through xml-data
    """
    import_name = "Vorlass_Import"
    title_siglum_dict = {}

    # Load and parse auxiliary xml files derived excels
    auxfile_siglum = open(
        "./vorlass_data_frischmuth/06_xml_export_excel/Frischmuth_Werktitel_Sigle.xml",
        "r",
        encoding="utf-8",
    )

    root_siglum_file = ET.parse(auxfile_siglum)

    for workitem in root_siglum_file.findall("WorkItem"):
        title_siglum_dict[
            get_text_by_elementpath(workitem, "title")
            + get_text_by_elementpath(workitem, "path")
        ] = get_text_by_elementpath(workitem, "siglum")

    source = create_source(import_name)

    create_persons(calling_file=fname)
    create_archives(calling_file=fname)
    create_types(calling_file=fname)

    b_fr = Person.objects.filter(name="Barbara Frischmuth").exclude(source=None)[0]
    archives = Archive.objects.all().exclude(source=None)

    for archive_obj in archives:
        archive_source_file = archive_obj.source.pubinfo

        with open(f"{archive_source_file}", "r", encoding="utf-8") as file_obj:
            element = ET.parse(file_obj)
            items = element.findall("item")
            for workelem in items:
                title = workelem.attrib.get("title")
                notes = "docx pointer: " + workelem.attrib.get("category")

                if workelem.attrib.get("category") != workelem.attrib.get("title"):
                    notes = notes + " --- " + workelem.attrib.get("unmodified_title")
                if (
                    workelem.attrib.get("category").split(" --- ")[0]
                    in ("Werke", "Sammlungen")
                    and title + notes in title_siglum_dict
                ):
                    siglum = title_siglum_dict[workelem.attrib.get("title") + notes]
                    work, created = Work.objects.get_or_create(
                        name=title,
                        notes=notes,
                        siglum=siglum,
                        defaults={"source": source},
                    )
                    create_triple(
                        entity_subj=b_fr,
                        entity_obj=work,
                        prop=Property.objects.get(name="is author of"),
                    )
                    work_type_key_name = WORKTYPE_MAPPINGS.get(
                        workelem.attrib.get("category")
                    )
                    if work_type_key_name:
                        work_type = WorkType.objects.get(
                            name=WORK_TYPES.get(work_type_key_name)["german_label"]
                        )
                        create_triple(
                            entity_subj=work,
                            entity_obj=work_type,
                            prop=Property.objects.get(name="has type"),
                        )

                    if not any(
                        x in workelem.attrib.get("category")
                        for x in ("[unpubl.?]", "Unveröffentlichte Werke")
                    ):
                        expression, created = Expression.objects.get_or_create(
                            name=title,
                            defaults={"source": source},
                        )
                        create_triple(
                            entity_subj=b_fr,
                            entity_obj=expression,
                            prop=Property.objects.get(name="is author of"),
                        )
                        create_triple(
                            entity_subj=work,
                            entity_obj=expression,
                            prop=Property.objects.get(name="is realised in"),
                        )

                    for holding in workelem.findall("holding"):
                        description = get_text_by_elementpath(holding, "description")
                        pho, created = PhysicalObject.objects.get_or_create(
                            name=description[:60],
                            description=description,
                            notes=notes,
                            defaults={"source": source},
                        )
                        create_triple(
                            entity_subj=pho,
                            entity_obj=work,
                            prop=Property.objects.get(name="relates to"),
                        )
                        create_triple(
                            entity_subj=archive_obj,
                            entity_obj=pho,
                            prop=Property.objects.get(name="holds"),
                        )

                else:
                    for holding in workelem.findall("holding"):
                        description = get_text_by_elementpath(holding, "description")
                        pho, created = PhysicalObject.objects.get_or_create(
                            name=description[:60],
                            description=description,
                            notes=notes,
                            defaults={"source": source},
                        )
                        create_triple(
                            entity_subj=archive_obj,
                            entity_obj=pho,
                            prop=Property.objects.get(name="holds"),
                        )
