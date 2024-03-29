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
from .additional_infos import WORK_TYPES, WORKTYPE_MAPPINGS
from .import_helpers import create_triple, create_source
from apis_ontology.scripts.access_sharepoint import import_and_parse_data

fname = os.path.basename(__file__)


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
        f"./vorlass_data_frischmuth/04_derived_custom/Frischmuth_Vorlass_FNI-FRISCHMUTH_import-data.xml",
        "r",
        encoding="utf-8",
    ) as file_obj:
        element = ET.parse(file_obj)
        items = element.findall("item")

        vorlass_xml_source, created = create_source(
            name="VorlassSourceXML",
            file_name=os.path.basename(file_obj.name),
            data_type="xslx",
        )

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
                siglum = title_siglum_dict[workelem.attrib.get("title") + notes][
                    "Sigle"
                ]
                work_type = title_siglum_dict[workelem.attrib.get("title") + notes][
                    "Werktyp"
                ]
                status = get_status(
                    title_siglum_dict[workelem.attrib.get("title") + notes]["status"]
                )
                fixed_title = title_siglum_dict[workelem.attrib.get("title") + notes][
                    "Titel"
                ]
                subtitle = (
                    title_siglum_dict[workelem.attrib.get("title") + notes][
                        "Untertitel"
                    ]
                    or ""
                )

                work, created = Work.objects.get_or_create(
                    title=fixed_title,
                    # notes=notes,
                    siglum=siglum,
                    progress_status=status,
                    subtitle=subtitle,
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

                for holding in workelem.findall("holding"):
                    description = get_text_by_elementpath(holding, "description")
                    pho = PhysicalObject.objects.create(
                        name=description[:60],
                        description=description,
                        vorlass_doc_reference=notes.replace("docx pointer: ", "")[:255],
                        # notes=notes,
                        data_source=vorlass_xml_source,
                    )
                    create_triple(
                        entity_subj=pho,
                        entity_obj=work,
                        prop=Property.objects.get(name_forward="relates to"),
                    )
                    create_triple(
                        entity_subj=archive,
                        entity_obj=pho,
                        prop=Property.objects.get(name_forward="holds"),
                    )

            else:
                for holding in workelem.findall("holding"):
                    description = get_text_by_elementpath(holding, "description")
                    pho = PhysicalObject.objects.create(
                        name=description[:60],
                        description=description,
                        vorlass_doc_reference=notes.replace("docx pointer: ", "")[:255],
                        # notes=notes,
                        data_source=vorlass_xml_source,
                    )
                    create_triple(
                        entity_subj=archive,
                        entity_obj=pho,
                        prop=Property.objects.get(name_forward="holds"),
                    )


def get_text_by_elementpath(element, element_child_name):
    """Helper function to get a cleaned string from an xml-element (as used in the auxiliary files)"""
    # strip because import data isn't clean (leading, trailing spaces)
    if element.find(element_child_name).text:
        return element.find(element_child_name).text.strip()
