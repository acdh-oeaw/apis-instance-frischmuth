import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

# from django.core.validators import URLValidator
from apis_core.apis_relations.models import Property
from apis_ontology.models import (
    Person,
    Work,
    Archive,
    PhysicalObject,
    WorkType,
    StatusMixin,
)
from .additional_infos import WORK_TYPES
from .import_helpers import create_triple, create_source
from apis_ontology.scripts.access_sharepoint import import_and_parse_data

fname = os.path.basename(__file__)

ns = {"tei": "http://www.tei-c.org/ns/1.0"}

ET.register_namespace("tei", ns["tei"])

def run():
    import_and_parse_data(parse_sigle_excel)


def parse_sigle_excel(file):
    title_siglum_dict = {}
    success = []
    failure = []

    df = pd.read_excel(file)

    vorlass_excel_source, created = create_source(
        name="VorlassSourceExcel", file_name=os.path.basename(file), data_type="xslx"
    )

    df_filtered = df[(df["Werktyp"].notnull()) | (df["status"].notnull())].replace(
        {np.nan: None}
    )

    df_cleaned = df_filtered.map(lambda x: x.strip() if isinstance(x, str) else x)

    for index, row in df_cleaned.iterrows():
        title_siglum_dict[row["Name"] + row["abgeleitet von"]] = row.to_dict()
    parse_vorlass_xml(title_siglum_dict, vorlass_excel_source)
    return success, failure


def get_status(status):
    status_choices = dict(
        (v, k) for k, v in dict(StatusMixin.ProgressStates.choices).items()
    )
    return status_choices.get(status, "")


def parse_vorlass_xml(title_siglum_dict, vorlass_excel_source):
    b_fr = Person.objects.filter(forename="Barbara", surname="Frischmuth").exclude(
        data_source=None
    )[0]
    archive = Archive.objects.filter(name="Franz-Nabl-Institut für Literaturforschung")[
        0
    ]

    with open(
        "./vorlass_data_frischmuth/06_final_tei_for_apis_import/Frischmuth_Vorlass_FNI-FRISCHMUTH_tei.xml",
        "r",
        encoding="utf-8",
    ) as file_obj:
        tree = ET.parse(file_obj)
        items = tree.findall(".//tei:bibl", ns)

        vorlass_xml_source, created = create_source(
            name="VorlassSourceXML",
            file_name=os.path.basename(file_obj.name),
            data_type="xslx",
        )

        for workelem in items:
            title = get_text_by_elementpath(workelem, "./tei:title[@type='main']", ns)
            notes = "docx pointer: " + get_text_by_elementpath(
                workelem, "./tei:note[@type='category']", ns
            )

            if (
                get_text_by_elementpath(workelem, "./tei:note[@type='category']", ns)
                != title
            ):
                notes = (
                    notes
                    + " --- "
                    + get_text_by_elementpath(
                        workelem, "./tei:note[@type='unmodified_title']", ns
                    )
                )
            if (
                get_text_by_elementpath(
                    workelem, "./tei:note[@type='category']", ns
                ).split(" --- ")[0]
                in ("Werke", "Sammlungen")
                and title + notes in title_siglum_dict
            ):
                siglum = title_siglum_dict[title + notes]["Sigle"]
                work_type = title_siglum_dict[title + notes]["Werktyp"]
                status = get_status(title_siglum_dict[title + notes]["status"])
                fixed_title = title_siglum_dict[title + notes]["Titel"]
                subtitle = title_siglum_dict[title + notes]["Untertitel"] or ""

                work, created = Work.objects.get_or_create(
                    title=fixed_title,
                    siglum=siglum,
                    progress_status=status,
                    subtitle=subtitle,
                    notes=workelem.attrib.get("corresp", ""),
                    defaults={"data_source": vorlass_excel_source},
                )
                create_triple(
                    entity_subj=b_fr,
                    entity_obj=work,
                    prop=Property.objects.get(name_forward="is author of"),
                )
                """work_type_key_name = WORKTYPE_MAPPINGS.get(
                    workelem.attrib.get("category")
                )"""

                if work_type:
                    work_type = WorkType.objects.get(
                        name=WORK_TYPES.get(
                            work_type.replace("type_", "").replace(" ", "")
                        )["german_label"]
                    )

                    create_triple(
                        entity_subj=work,
                        entity_obj=work_type,
                        prop=Property.objects.get(name_forward="has type"),
                    )

def get_text_by_elementpath(element, path, ns):
    """Helper function to get a cleaned string from an xml-element (as used in the auxiliary files)"""
    # strip because import data isn't clean (leading, trailing spaces)
    node_text = ""
    if element and element.find(path, ns) is not None:
        node_text = " ".join(
            " ".join(element.find(path, ns).text.strip().splitlines()).split()
        )
    return node_text


def create_physical_object(
    element, ns, related_work, archive, data_source, physical_object_parent=None
):
    name = get_text_by_elementpath(element, "./tei:objectIdentifier/tei:objectName", ns)
    description = get_text_by_elementpath(element, "./tei:physDesc/tei:p", ns)
    docx_reference = get_text_by_elementpath(
        element, "./tei:note[@type='docx_anchor']", ns
    )

    pho = PhysicalObject.objects.create(
        name=name,
        description=description,
        vorlass_doc_reference=docx_reference,
        data_source=data_source,
    )
    create_triple(
        entity_subj=pho,
        entity_obj=related_work,
        prop=Property.objects.get(name_forward="relates to"),
    )
    create_triple(
        entity_subj=archive,
        entity_obj=pho,
        prop=Property.objects.get(name_forward="holds"),
    )
    if physical_object_parent:
        create_triple(
            entity_subj=physical_object_parent,
            entity_obj=pho,
            prop=Property.objects.get(name_forward="holds or supports"),
        )

    if element.find("./tei:note[@type='objects']/tei:listObject", ns):
        for el in element.findall(
            "./tei:note[@type='objects']/tei:listObject//tei:object", ns
        ):
            create_physical_object(el, ns, related_work, archive, data_source, pho)
