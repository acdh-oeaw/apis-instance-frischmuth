from django.core.management.base import BaseCommand
import importlib
import logging
import getpass
import os
import re
from pyzotero import zotero, zotero_errors
from apis_core.apis_relations.models import Property
from django.db.models import Q
from apis_ontology.models import Expression, Work
from .additional_infos import WORK_TYPES, ZOTERO_CREATORS_MAPPING
from .utils import clean_and_split_multivalue_string
from .import_helpers import (
    create_triple,
    create_source,
    create_work,
    get_work,
    get_type,
    create_expression,
    create_person,
    create_organisation,
    create_place,
    create_topic,
    get_expressions_by_work,
)

# Use keys or keywords in environment variable ZOTERO_FILTER_COLLECTIONS
# to limit Zotero imports to specific collections.

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ontology_script")

    def handle(self, *args, **options):
        script = importlib.import_module(
            f"apis_ontology.ontology_specific_scripts.{options['ontology_script']}"
        )
        script.run()


def run():
    zot = zotero_login()

    coll_id, coll = input_dialog(zot)

    imported, failed = import_work_collections(zot, coll_id, include_subs=True)

    for i in imported:
        # TODO log successful imports
        pass

    for f in failed:
        # TODO log failed imports
        pass


def import_work_collections(zot, coll_id, include_subs=True):
    """
    For regular import of works – both primary (by Frischmuth) and secondary
    (other authors).

    Import assumes three sub collections to be present in any collection
    which should be imported, which need to be imported in the order:
    "tertiaer", "primaer", "sekundaer".

    :param zot: Zotero connection object
    :param coll_id: collection to import
    :param include_subs: boolean to include/exclude sub collections;
                         ATTN. currently only works one level deep
    :return: tuple with list of imported items and list of failed items
             to use for further processing
    """
    success = []
    failure = []
    sub_ids = []

    collection_data = get_collection_data(zot, coll_id, include_subs=include_subs)

    required_subs_raw = os.environ.get("ZOTERO_SUB_COLLECTIONS", False)
    if not required_subs_raw:
        required_subs = ["primaer", "sekundaer", "tertiaer"]
    else:
        required_subs = [k.replace(" ", "") for k in required_subs_raw.split(",")]

    if required_subs:
        sub_collections = collection_data["sub_collection_info"]

        if set(required_subs).issubset([d["name"] for d in sub_collections]):
            for req in required_subs:
                for d in [d for d in sub_collections if d["name"] == req]:
                    sub_ids.append(d["key"])

            # check all required sub collections are present

            for coll_id in sub_ids:
                imported, failed = import_items_from_collection(
                    zot, coll_id, include_subs=True, import_name=collection_data["name"]
                )
                success.append(imported)
                failure.append(failed)

        else:
            failure_msg = f"Cannot import from collection {collection_data} – missing sub collections!"
            failure.append(failure_msg)

    return success, failure


def zotero_login():
    """
    Log into Zotero to make use of its API.

    :return: Zotero instance
    """
    api_key = os.environ.get("ZOTERO_API_KEY")
    library_id = os.environ.get("ZOTERO_LIBRARY_ID")

    while api_key is None or api_key == "":
        api_key = os.environ.setdefault(
            "ZOTERO_API_KEY", getpass.getpass(prompt="Enter Zotero API key:\n")
        )

    while library_id is None or library_id == "":
        library_id = os.environ.setdefault(
            "ZOTERO_LIBRARY_ID", getpass.getpass(prompt="Enter Zotero library ID:\n")
        )

    zot = zotero.Zotero(library_id, "group", api_key)

    try:
        zot.key_info()
    except zotero_errors.UserNotAuthorised as e:
        print(
            f"Zotero login not possible: "
            f"{zot.request.text} ({zot.request.status_code})"
        )
        exit(1)
    except zotero_errors.HTTPError as e:
        print(
            f"Zotero login not possible: "
            f"{zot.request.text} ({zot.request.status_code})"
        )
        exit(1)
    else:
        return zot


def input_dialog(zot, filter_collections=True, sub_collections=True):
    """
    Input dialogue to let user choose which collection to import from
    a number of available Zotero collections.

    :param zot: Zotero instance
    :param filter_collections: boolean; toggle to allow filtering
                               collections by keys or keywords (provided via
                               env variables)
    :param sub_collections: boolean; toggle to list sub collections
                            alongside top-level collections
    :return: a tuple consisting of a collection key and collection data
    """
    collection_id = None
    collection = None
    extra_choices = [
        {
            "order": 100,
            "label": "Toggle automatic filtering of collections via env variables",
            "primary_key": "F",
            "allowed_keys": ["F", "f"],
            "run": (lambda f, s: (not f, s)),
        },
        {
            "order": 300,
            "label": "Toggle between showing only top-level collections or all collections",
            "primary_key": "S",
            "allowed_keys": ["S", "s"],
            "run": (lambda f, s: (f, not s)),
        },
        {
            "order": 1000,
            "label": "Exit",
            "primary_key": "X",
            "allowed_keys": ["X", "x"],
            "run": (lambda f, s: exit(0)),
        },
    ]

    extra_keys = sum(
        [[e["primary_key"]] + e["allowed_keys"] for e in extra_choices], []
    )

    while True:
        active_collections = get_collections(
            zot, filter_collections=filter_collections, sub_collections=sub_collections
        )

        choices = generate_input_choices(
            active_collections,
            extra_choices=sorted(extra_choices, key=lambda a: a["order"]),
        )

        allowed_keys = list(
            set(extra_keys + sum([[c["key"], str(c["key"])] for c in choices], []))
        )

        input_prompt = "Select a Zotero collection to import:\n"
        input_prompt += "".join([f"{c['key']}: {c['label']}\n" for c in choices])

        user_input = input(input_prompt)

        if user_input in allowed_keys:
            if user_input in extra_keys:
                for choice in [
                    e for e in extra_choices if user_input in e["allowed_keys"]
                ]:
                    filter_collections, sub_collections = choice["run"](
                        filter_collections, sub_collections
                    )
            else:
                # user choice is an actual Zotero collections
                user_input = int(user_input)
                for c in choices:
                    if user_input == c["key"]:
                        collection_id = c["collection_id"]
                        collection = next(
                            (
                                a
                                for a in active_collections
                                if a["data"]["key"] == collection_id
                            ),
                            None,
                        )
                break

    return collection_id, collection


def generate_input_choices(collections, extra_choices=None):
    """
    Generate input keys and human-readable labels from Zotero collections
    as well as additional options (if available) to offer to users
    in an interactive input dialogue.

    :param collections: list of Zotero collections
    :param extra_choices: list of dictionaries of other input choices besides
                          Zotero collections
    :return: a list of dictionaries of input keys and labels
    """
    choices = list()

    for i, c in enumerate(
        sorted(collections, key=lambda a: a["data"]["name"]), start=1
    ):
        collection_id = c["data"]["key"]
        display_name = c["data"]["name"]
        parent_coll = c["data"]["parentCollection"]

        if parent_coll:
            for d in [d for d in collections if d["key"] == parent_coll]:
                parent = d["data"]["name"]
                display_name = f"{display_name} ... parent collection: {parent}"

        choices.append(
            {
                "key": i,
                "label": display_name,
                "collection_id": collection_id,
            }
        )

    if extra_choices:
        for e in extra_choices:
            choices.append(
                {
                    "key": e["primary_key"],
                    "label": e["label"],
                }
            )

    return choices


def import_items_from_collection(zot, coll_key, include_subs=True, import_name=None):
    """
    Import collection items from a given Zotero collection.

    :param zot: Zotero connection object
    :param coll_key: key of collection from which to import
    :param include_subs: boolean to include/exclude sub collections;
                         ATTN. currently only works one level deep
    :param import_name: string to use for import name
    :return: tuple with list of imported items and list of failed items
             to use for further processing
    """
    collection_data = get_collection_data(zot, coll_key, include_subs=include_subs)

    success, failure = import_items(collection_data["items"], import_name)

    return success, failure


def import_items(collection_items, import_name):
    """
    :param collection_items: list of Zotero items to import
    :param import_name: name to use for DataSource for entity objects
    :return: tuple with list of imported items and list of failed items
             to use for further processing
    """
    success = []
    failure = []

    source, created = create_source(import_name, "", "", "", "Zotero")
    importable, non_importable = get_valid_collection_items(collection_items)

    if importable:
        for i in importable:
            creation_success, creation_problems = create_entities(i, source)
            success.extend(creation_success)
            failure.extend(creation_problems)

    failure.extend(non_importable)

    return success, failure


def get_collection_data(zot, coll_key, include_subs=True):
    """
    Retrieve specific information about/data for a Zotero collection
    with a given key.

    Data returned includes some metadata about the collection
    as well as a list of collection items.

    :param zot: Zotero instance
    :param coll_key: key of Zotero collection to query
    :param include_subs: boolean to include/exclude sub collections;
                         ATTN. currently only works one level deep
    :return: an object holding all collection items as well as
             (meta) information about the collection
    """
    collection = zot.collection(coll_key)
    items = zot.collection_items_top(coll_key)
    sub_collections = []

    if include_subs:
        items = zot.collection_items(coll_key, itemType="-attachment")
        subs = zot.collections_sub(coll_key)
        for s in subs:
            sub_data = get_collection_data(zot, s["key"], include_subs=False)
            items.extend(sub_data.pop("items"))
            del sub_data["sub_collection_info"]
            sub_collections.append(sub_data)

    select_collection_data = {
        "key": coll_key,
        "name": collection["data"]["name"],
        "url": collection["links"]["self"]["href"],
        "items": items,
        "sub_collection_info": sub_collections,
    }

    return select_collection_data


def get_valid_collection_items(collection_items):
    """
    Function to determine whether collection items should be
    considered for import or not.
    If a collection items does not have a title or its title equals
    an empty string, it should not be considered for import.

    :param collection_items: list of collection items
    :return: a tuple with lists of valid and invalid collection items
    """
    importable = []
    not_importable = []

    for item in collection_items:
        title = item["data"].get("title", None)

        if title and title != "":
            importable.append(item)
        else:
            # notes for e.g. book items are included again as separate items
            parent_key = item["data"].get("parentItem", None)
            if parent_key and parent_key in [s["key"] for s in importable]:
                parent = list(
                    filter(lambda item: item["key"] == parent_key, importable)
                )[0]
                parent.update({"enriched": {"note": item["data"].get("note", None)}})
            else:
                not_importable.append(item)

    return importable, not_importable


def get_manifestation_type(collection_name):
    available_manifestation_types = Expression.ManifestationTypes
    manifestation_type = [
        x for x in available_manifestation_types if x.label in collection_name
    ]
    return manifestation_type


def get_edition_types_from_tags(tags):
    """
    Check if a Zotero collection item's tags contain valid
    manifestation types for Expression entities.

    :param tags: a list of strings
    :return: a list of strings
    """
    valid_tags = [t.value for t in Expression.EditionTypes if t.label in tags]

    return valid_tags


def get_work_references_fom_tags(tags):
    """
    Check if a Zotero collection item's tags contain valid references
    to create relationships between Work entities.

    :param tags: a list of strings
    :return: a list of dictionaries containing both the reference label
             and the siglum of the work being referenced
    """
    work_references = [
        "references",
        "discusses",
        "mentions",
        "is part of work",
        "is referenced in",
    ]
    valid_tags = []

    applicable_tags = [t.replace("work_", "") for t in tags if t.startswith("work_")]

    for t in applicable_tags:
        explode_string = t.split("_")

        wording = " ".join(explode_string[:-1])
        siglum = explode_string[-1]

        if wording in work_references and siglum != wording and siglum != "":
            valid_tags.append(
                {
                    "ref_label": wording,
                    "ref_siglum": siglum,
                }
            )

    return valid_tags


def get_expression_references_fom_tags(tags):
    """
    Check if a Zotero collection item's tags contain valid references
    to create relationships between Expression entities.

    :param tags: a list of strings
    :return: a list of dictionaries containing both the reference label
             and the siglum of the work being referenced
    """
    expression_references = ["expression is part of"]
    valid_tags = []

    applicable_tags = [t for t in tags if t.startswith("expression_")]

    for t in applicable_tags:
        explode_string = t.split("_")

        wording = " ".join(explode_string[:-1])
        siglum = explode_string[-1]

        if wording in expression_references and siglum != wording and siglum != "":
            valid_tags.append(
                {
                    "ref_label": f"{wording} expression",
                    "ref_siglum": siglum,
                }
            )

    return valid_tags


def get_work_types_from_tags(tags):
    """
    Check if a Zotero collection item's tags contain valid work type labels
    to create relationships between Work entities and WorkType entities.

    :param tags: a list of strings
    :return: a list of dictionaries
    """
    work_types = WORK_TYPES.keys()
    valid_work_types = []

    applicable_tags = [t.replace("type_", "") for t in tags if t.startswith("type_")]

    for t in applicable_tags:
        if t in work_types:
            valid_work_types.append(
                {
                    "english_label": t,
                    "german_label": WORK_TYPES[t]["german_label"],
                    "german_label_plural": WORK_TYPES[t]["german_label_plural"],
                }
            )

    return valid_work_types


def match_creator_types(creators):
    """
    Match Zotero creator types to APIS roles for persons.

    Add the property name for the matching role to each creator object to
    allow for later creation of triples between Persons and Works resp.
    Expressions.

    :param creators: a list of dictionaries
    :return: a list of dictionaries
    """
    creator_types = ZOTERO_CREATORS_MAPPING.keys()
    valid_creators = []

    for c in creators:
        creator_type = c["creatorType"]
        if creator_type not in creator_types:
            creator_type = "contributor"

        c["property_name"] = ZOTERO_CREATORS_MAPPING[creator_type]["property_name"]
        valid_creators.append(c)

    return valid_creators


def get_collections(zot, filter_collections=True, sub_collections=True):
    """
    Retrieve Zotero collections to consider for imports.

    :param zot: the active Zotero instance
    :param filter_collections: boolean; if set to True, filters collections
                               by either keys or keywords in env variable
                               ZOTERO_FILTER_COLLECTIONS (if available)
    :param sub_collections: boolean; if set to False, only considers top-level
                            collections, not sub collections
    :return: a list of Zotero collections
    """
    active = list()

    def fetch(sub_collections=sub_collections):
        """
        Fetch available Zotero collections.

        :param sub_collections: boolean; if set to True, also includes sub
                                collections within a given collection
        :return: a list of Zotero collections
        """
        if not sub_collections:
            return zot.collections_top()
        else:
            return zot.collections()

    if not filter_collections:
        active = fetch()
    else:
        keys_keywords_raw = os.environ.get("ZOTERO_FILTER_COLLECTIONS", False)

        if not keys_keywords_raw:
            active = fetch()
        else:
            keys_keywords = [k.replace(" ", "") for k in keys_keywords_raw.split(",")]

            if len(keys_keywords) > 0:
                for k in keys_keywords:
                    keyword_matches = zot.collections(q=k)

                    if keyword_matches:
                        for m in keyword_matches:
                            if m["key"] not in active:
                                active.append(m)
                    else:
                        try:
                            key_match = zot.collection(k)
                            active.append(key_match)
                        except Exception as e:
                            print(f"Collection with key {k} not found.")

        if not active:
            print(
                "\n"
                "No matches found for provided collection keys or keywords.\n"
                "Retrieving all available collections...\n"
            )
            active = fetch()

    if not active:
        print("There are no Zotero collections available for this account. Exiting.")
        exit(1)

    return active


def add_collection(entity, collection):
    """Helper function to add collection to entity collection property"""
    entity.collection.add(collection)


def create_entities(item, source):
    """
    Create entities from Zotero items.
    """
    success = []
    failure = []

    item_data = {}
    for k, v in item["data"].items():
        if isinstance(v, str):
            v = v.strip()
        item_data[k] = v

    title = item_data["title"]
    siglum = item_data["callNumber"]
    item_type = item_data["itemType"]
    subtitle = item_data.get("shortTitle", None)
    abstract = item_data.get("abstractNote", None)
    num_pages = item_data.get("numPages", None)
    relevant_pages = item_data.get("pages", "")
    item_date = item_data.get("date", None)
    languages = clean_and_split_multivalue_string(item_data.get("language", ""), ";")
    isbn = item_data.get("ISBN", "")
    places_of_publication = clean_and_split_multivalue_string(
        item_data.get("place", ""), ";"
    )
    publisher = item_data.get("publisher", None)
    creators = item_data.get("creators", [])
    item_tags = item_data.get("tags", [])
    series = item_data.get("series", "")
    publication_title = item_data.get("publicationTitle", "")
    issue = item_data.get("seriesNumber", item_data.get("issue", ""))
    volume = item_data.get("volume", "")
    edition = item_data.get("edition", "")
    creators_with_props = []
    edition_types = []
    work_types = []
    work_refs = []
    topics = []
    expr_refs = []
    page_count = None
    item_note = item.get("enriched", {}).get("note", None)

    if creators:
        creators_with_props = match_creator_types(creators)

    if item_tags:
        tags = [i["tag"].strip() for i in item_tags if "tag" in i]
        if tags:
            edition_types = get_edition_types_from_tags(
                [t for t in tags if t.endswith("ausgabe")]
            )
            work_refs = get_work_references_fom_tags(
                [t for t in tags if t.startswith("work_")]
            )
            expr_refs = get_expression_references_fom_tags(
                [t for t in tags if t.startswith("expression_")]
            )
            work_types = get_work_types_from_tags(
                [t for t in tags if t.startswith("type_")]
            )
            topics = [t.replace("topic_", "") for t in tags if t.startswith("topic_")]

    pub_date = item_date
    if num_pages:
        pages = int(num_pages)
        if pages > 0:
            page_count = pages

    # get or create Work object
    work, created = create_work(title, subtitle, siglum, source)
    # if abstract contains text, we overwrite the existing one
    if abstract:
        work.summary = abstract
        work.save()

    if languages:
        work.language = languages
        work.save()

    if created:
        success.append(work)

        if work_types:
            # create triple for work type
            for t in work_types:
                work_type = get_type(t["german_label"])

                triple, created = create_triple(
                    entity_subj=work,
                    entity_obj=work_type,
                    prop=Property.objects.get(name_forward="has type"),
                )
                if created:
                    success.append(
                        f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                    )

    # get or create Expression object
    expression, created = create_expression(
        title, subtitle, pub_date, source, relevant_pages, page_count, edition_types
    )
    if created:
        if isbn:
            expression.isbn = isbn
            expression.save()
        if languages:
            expression.language = languages
            expression.save()
        if item_note:
            expression.notes = item_note
            expression.save()
            if re.search("\<.*\>", item_note):
                logger.info(
                    f"Expression note contains potential markup. Expression {expression.id}"
                )
        if expression.title != work.title or expression.subtitle != work.subtitle:
            logger.info(
                f"Expression title or subtitle differs from work title or subtitle. Expression {expression.id}"
            )
        success.append(expression)

    triple, created = create_triple(
        entity_subj=work,
        entity_obj=expression,
        prop=Property.objects.get(name_forward="is realised in"),
    )
    if created:
        success.append(
            f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
        )

    # create relations between Works when tags for Zotero item indicate relation
    for r in work_refs:
        ref_siglum = r["ref_siglum"]
        ref_label = r["ref_label"]

        referenced_work = get_work(ref_siglum)

        if referenced_work:
            success.append(referenced_work)

            ref_prop = Property.objects.filter(
                Q(name_forward=ref_label) | Q(name_reverse=ref_label)
            ).first()

            entity_subj = (
                work if ref_prop.name_forward == ref_label else referenced_work
            )
            entity_obj = referenced_work if ref_prop.name_forward == ref_label else work

            triple, created = create_triple(
                entity_subj=entity_subj,
                entity_obj=entity_obj,
                prop=ref_prop,
            )
            if created:
                success.append(
                    f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                )

        else:
            ref_err = f"Referenced work {ref_siglum} does not exist."
            failure.append(ref_err)

    for r in expr_refs:
        ref_siglum = r["ref_siglum"]
        ref_label = r["ref_label"]

        referenced_work = get_work(ref_siglum)
        if referenced_work:
            work_expressions = get_expressions_by_work(referenced_work.id)

            # temporary fix because we have a flaw in our logic (expressions have to be in zotero to be referenced)
            if not work_expressions:
                work = Work.objects.get(id=work.id)
                exp, created = create_expression(
                    title=referenced_work.title,
                    subtitle=referenced_work.subtitle,
                    source=source,
                    pub_date=None,
                    relevant_pages="",
                )
                logger.info(
                    f"No expression found in zotero for referenced work. So basic expression will be created. Expression {expression.id}"
                )
                create_triple(
                    entity_subj=referenced_work,
                    entity_obj=exp,
                    prop=Property.objects.get(name_forward="is realised in"),
                )
                work_expressions.append(exp)

            for work_expression in work_expressions:
                triple, created = create_triple(
                    entity_subj=expression,
                    entity_obj=work_expression,
                    prop=Property.objects.get(name_forward=ref_label),
                )
                if created:
                    success.append(
                        f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                    )

        else:
            ref_err = f"Referenced work {ref_siglum} does not exist."
            failure.append(ref_err)

    if creators_with_props:
        # get or create Person object for creators
        for creator in creators_with_props:
            person, created = create_person(creator, source)
            if created:
                success.append(f"Created author: {person}")

            triple, created = create_triple(
                entity_subj=person,
                entity_obj=work,
                prop=Property.objects.get(name_forward=creator["property_name"]),
            )
            if created:
                success.append(
                    f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                )

            if expression:
                triple, created = create_triple(
                    entity_subj=person,
                    entity_obj=expression,
                    prop=Property.objects.get(name_forward=creator["property_name"]),
                )
                if created:
                    success.append(
                        f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                    )
    else:
        ref_err = f"Work {siglum} is missing creators."
        failure.append(ref_err)

    if publisher:
        # get or create Organisation object for publisher
        organisation, created = create_organisation(publisher, source)

        if created:
            success.append(organisation)

        triple, created = create_triple(
            entity_subj=organisation,
            entity_obj=expression,
            prop=Property.objects.get(name_forward="is publisher of"),
        )
        if created:
            success.append(
                f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
            )

        # get or create Place object for place of publication
        # ATTN. Zotero "place" field can contain multiple places
        # separated by semicolons
        if places_of_publication:
            for p in places_of_publication:
                place, created = create_place(p, source)
                if created:
                    success.append(f"Created place: {place}")

                triple, created = create_triple(
                    entity_subj=expression,
                    entity_obj=place,
                    prop=Property.objects.get(name_forward="is published in"),
                )
                if created:
                    success.append(
                        f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
                    )
    # get or create topics and relations between work and topics
    for topic in topics:
        topic, created = create_topic(topic_name=topic, source=source)
        if created:
            success.append(f"Created topic: {topic}")

        triple, created = create_triple(
            entity_subj=work,
            entity_obj=topic,
            prop=Property.objects.get(name_forward="is about topic"),
        )
        if created:
            success.append(
                f"Created new triple: {triple.subj} – {triple.prop.name_forward} – {triple.obj}"
            )

    if item_type in ("dictionaryEntry", "newspaperArticle", "journalArticle", "book"):
        parent_publication = None
        parent_expression = None
        if series:
            parent_publication, created = Work.objects.get_or_create(
                title=series, defaults={"data_source": source}
            )
            parent_expression, created = Expression.objects.get_or_create(
                title=series,
                issue=issue,
                volume=volume,
                edition=edition,
                defaults={"data_source": source},
            )
        if publication_title:
            parent_publication, created = Work.objects.get_or_create(
                title=publication_title, defaults={"data_source": source}
            )
            parent_expression, created = Expression.objects.get_or_create(
                title=publication_title,
                issue=issue,
                volume=volume,
                edition=edition,
                defaults={"data_source": source},
            )
        if parent_publication and parent_expression:
            parent_parent_triple, created = create_triple(
                entity_subj=parent_publication,
                entity_obj=parent_expression,
                prop=Property.objects.get(name_forward="is realised in"),
            )
            parent_child_triple, created = create_triple(
                entity_subj=expression,
                entity_obj=parent_expression,
                prop=Property.objects.get(name_forward="is realised in"),
            )

    return success, failure
