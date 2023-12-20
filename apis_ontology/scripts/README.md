# Import scripts for Frischmuth data

The import process is split across three scripts, _which need to be run in order_:

1. [import_xml](import_xml.py)
2. [import_zotero_collections](import_zotero_collections.py)
3. [import_nonbibl_entities](import_nonbibl_entities.py)

## Prerequisites

Two of the scripts require access to a separate private repository **vorlass_data_frischmuth**, which contains XML data pertaining to objects which are part of Barbara Frischmuth's Vorlass. This repository is assumed to sit at the root of the Git superproject. When it's used as another submodule, make sure the superproject points to its latest commit.

One script requires access to a private [Zotero](https://www.zotero.org/) library. It expects values set for environment variables `ZOTERO_API_KEY` and  `ZOTERO_LIBRARY_ID`. If it can't find them, it will prompt you to enter these values manually.

Before running the scripts, make sure all properties between entities have been created. I.e. the `create_relationships` management command needs to have been run once before.

When developing locally, also take care to have environment variables for your local database set, or use the `--settings` parameter to point to a local settings files with variables for your DB.

## Import all Vorlass data

This script needs access to files contained within the `vorlass_data_frischmuth` repository.

Run the import with:
```sh
$ python manage.py run_ontology_script import_xml
```

## Import data from Zotero

This script needs access to a project-specific Zotero library.

Run the import with:
```sh
$ python manage.py run_ontology_script import_zotero_collections
```

## Import non-bibliographic entities

This script needs access to files contained within the `vorlass_data_frischmuth` repository.

Run the import with:
```sh
$ python manage.py run_ontology_script import_nonbibl_entities
```

