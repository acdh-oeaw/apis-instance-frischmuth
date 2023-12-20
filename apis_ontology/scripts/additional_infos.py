PERSONS = [
    {
        "id": 0,
        "name": "Barbara Frischmuth",
        "first_name": "Barbara",
        "last_name": "Frischmuth",
    }
]

ARCHIVES = [
    {
        "name": "Franz-Nabl-Institut für Literaturforschung",
        "source_file": "./vorlass_data_frischmuth/04_derived_custom/Frischmuth_Vorlass_FNI-FRISCHMUTH_import-data.xml",
    }
]

MISC_ENTITIES = [
    {
        "entity_plural": "Names",
        "path": "Name",
        "source_file": "./vorlass_data_frischmuth/06_xml_export_excel/Frischmuth_Entitaeten_Namen.xml",
    },
    {
        "entity_plural": "Places",
        "path": "Ort",
        "source_file": "./vorlass_data_frischmuth/06_xml_export_excel/Frischmuth_Entitaeten_Orte.xml",
    },
    {
        "entity_plural": "Topics",
        "path": "Thema",
        "source_file": "./vorlass_data_frischmuth/06_xml_export_excel/Frischmuth_Entitaeten_Themen.xml",
    },
    {
        "entity_plural": "ResearchPerspectives",
        "path": "Forschungshinsicht",
        "source_file": "./vorlass_data_frischmuth/06_xml_export_excel/Frischmuth_Entitaeten_Forschungshinsichten.xml",
    },
]

# dictionary for script-based creation of "Type" entity objects
# dictionary keys are used for required field "name"
WORK_TYPES = {
    # example dict item:
    # "english_key": {  #  reuses English values for WorkType choices
    #     "hierarchy_level": 1,  # for reference only; Integer (regular numbering, not zero-based)
    #     "german_label": "",  #  value for "name" field; String
    #     "german_label_plural": "",  #  value for "name_plural" field; String or None
    #     "parent_key": "",  # key for parent type in hierarchy; String or None
    #     "previous_english_key": None,  # old WorkType value where applicable; String or None
    # },
    "primary_work_frischmuth": {
        "hierarchy_level": 1,
        "german_label": "Primärwerk",
        "german_label_plural": None,
        "parent_key": None,
        "previous_english_key": "main_category_primary_work_frischmuth",
    },
    "prose": {
        "hierarchy_level": 2,
        "german_label": "Prosa",
        "german_label_plural": None,
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": "subcategory_prose",
    },
    "novels": {
        "hierarchy_level": 3,
        "german_label": "Roman",
        "german_label_plural": "Romane",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "tales": {
        "hierarchy_level": 3,
        "german_label": "Erzählung",
        "german_label_plural": "Erzählungen",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "creative_nonfiction": {
        "hierarchy_level": 3,
        "german_label": "literarischer Sachtext",
        "german_label_plural": "Literarische Sachtexte",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "lectures_on_poetics": {
        "hierarchy_level": 3,
        "german_label": "Poetik-Vorlesung",
        "german_label_plural": "Poetik-Vorlesungen",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "literature_for_children_and_young_adults": {
        "hierarchy_level": 3,
        "german_label": "Kinder- und Jugendbuch",
        "german_label_plural": "Kinder- und Jugendbücher",
        "parent_key": "prose",
        "previous_english_key": "childrens_and_young_adults_literature",
    },
    "speeches": {
        "hierarchy_level": 3,
        "german_label": "Rede",
        "german_label_plural": "Reden",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "essays": {
        "hierarchy_level": 3,
        "german_label": "Essay",
        "german_label_plural": "Essays",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "lectures": {
        "hierarchy_level": 3,
        "german_label": "Vorlesung",
        "german_label_plural": "Vorlesungen",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "reviews": {
        "hierarchy_level": 3,
        "german_label": "Rezension",
        "german_label_plural": "Rezensionen",
        "parent_key": "prose",
        "previous_english_key": None,
    },
    "poetry": {
        "hierarchy_level": 2,
        "german_label": "Lyrik",
        "german_label_plural": None,
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": None,
    },
    "dramatic_writing": {
        "hierarchy_level": 2,
        "german_label": "Dramatik",
        "german_label_plural": None,
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": "subcategory_dramatic_writing",
    },
    "dramas": {
        "hierarchy_level": 3,
        "german_label": "Drama",
        "german_label_plural": "Dramen",
        "parent_key": "dramatic_writing",
        "previous_english_key": None,
    },
    "radio_scripts": {
        "hierarchy_level": 3,
        "german_label": "Hörspieldrehbuch",
        "german_label_plural": "Hörspieldrehbücher",
        "parent_key": "dramatic_writing",
        "previous_english_key": None,
    },
    "screenwriting": {
        "hierarchy_level": 3,
        "german_label": "Filmdrehbuch, Filmvorlage",
        "german_label_plural": "Filmdrehbücher, Filmvorlagen",
        "parent_key": "dramatic_writing",
        "previous_english_key": None,
    },
    "audiovisual_media": {
        "hierarchy_level": 2,
        "german_label": "Veröffentlichung in audiovisuellen Medien",
        "german_label_plural": "Veröffentlichungen in audiovisuellen Medien",
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": "subcategory_audiovisual_media",
    },
    "radio_plays": {
        "hierarchy_level": 3,
        "german_label": "Hörspiel",
        "german_label_plural": "Hörspiele",
        "parent_key": "audiovisual_media",
        "previous_english_key": None,
    },
    "films": {
        "hierarchy_level": 3,
        "german_label": "Film",
        "german_label_plural": "Filme",
        "parent_key": "audiovisual_media",
        "previous_english_key": None,
    },
    "audiovisual_works_for_children_and_young_adults": {
        "hierarchy_level": 3,
        "german_label": "Kinder- und Jugendproduktion",
        "german_label_plural": "Kinder- und Jugendproduktionen",
        "parent_key": "audiovisual_media",
        "previous_english_key": "audiovisual_works_for_young_audiences",
    },
    "radio_drama_translations_and_adaptations": {
        "hierarchy_level": 3,
        "german_label": "Hörspielübersetzung, Hörspielbearbeitung",
        "german_label_plural": "Hörspielübersetzungen, Hörspielbearbeitungen",
        "parent_key": "audiovisual_media",
        "previous_english_key": None,
    },
    "books_and_literature_programmes": {
        "hierarchy_level": 3,
        "german_label": "Literatursendung",
        "german_label_plural": "Literatursendungen",
        "parent_key": "audiovisual_media",
        "previous_english_key": None,
    },
    "misc_audiovisual_contributions": {
        "hierarchy_level": 3,
        "german_label": "anderweitiger Beitrag in audiovisuellen Medien",
        "german_label_plural": "anderweitige Beiträge in audiovisuellen Medien",
        "parent_key": "audiovisual_media",
        "previous_english_key": None,
    },
    "paratexts": {
        "hierarchy_level": 2,
        "german_label": "Paratext",
        "german_label_plural": None,
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": None,
    },
    "images": {
        "hierarchy_level": 2,
        "german_label": "Abbildung",
        "german_label_plural": "Abbildungen",
        "parent_key": "primary_work_frischmuth",
        "previous_english_key": None,
    },
    "secondary_work": {
        "hierarchy_level": 1,
        "german_label": "Rezeption/Sekundärwerk",
        "german_label_plural": None,
        "parent_key": None,
        "previous_english_key": "main_category_secondary_work",
    },
    "literary_criticism_academia": {
        "hierarchy_level": 2,
        "german_label": "akademische Rezeption",
        "german_label_plural": None,
        "parent_key": "secondary_work",
        "previous_english_key": "subcategory_literary_criticism_academia",
    },
    "monographs": {
        "hierarchy_level": 3,
        "german_label": "Monografie",
        "german_label_plural": "Monografien",
        "parent_key": "literary_criticism_academia",
        "previous_english_key": None,
    },
    "anthologies": {
        "hierarchy_level": 3,
        "german_label": "Sammelband",
        "german_label_plural": "Sammelbände",
        "parent_key": "literary_criticism_academia",
        "previous_english_key": None,
    },
    "articles": {
        "hierarchy_level": 3,
        "german_label": "Artikel",
        "german_label_plural": "Artikel",
        "parent_key": "literary_criticism_academia",
        "previous_english_key": None,
    },
    "journal_articles": {
        "hierarchy_level": 3,
        "german_label": "Journalartikel",
        "german_label_plural": "Journalartikel",
        "parent_key": "literary_criticism_academia",
        "previous_english_key": None,
    },
    "graduate_papers": {
        "hierarchy_level": 3,
        "german_label": "Hochschulschrift",
        "german_label_plural": "Hochschulschriften",
        "parent_key": "literary_criticism_academia",
        "previous_english_key": "further_subcategory_graduate_papers",
    },
    "university_theses_masters_degree": {
        "hierarchy_level": 4,
        "german_label": "Diplomarbeit",
        "german_label_plural": "Diplomarbeiten",
        "parent_key": "graduate_papers",
        "previous_english_key": None,
    },
    "university_dissertations_doctorate": {
        "hierarchy_level": 4,
        "german_label": "Dissertation",
        "german_label_plural": "Dissertationen",
        "parent_key": "graduate_papers",
        "previous_english_key": None,
    },
    "literary_review_journalism": {
        "hierarchy_level": 2,
        "german_label": "journalistische Rezeption",
        "german_label_plural": None,
        "parent_key": "secondary_work",
        "previous_english_key": "subcategory_literary_review_journalism",
    },
    "book_reviews": {
        "hierarchy_level": 3,
        "german_label": "Besprechung",
        "german_label_plural": "Besprechungen",
        "parent_key": "literary_review_journalism",
        "previous_english_key": None,
    },
    "reports": {
        "hierarchy_level": 3,
        "german_label": "Bericht",
        "german_label_plural": "Berichte",
        "parent_key": "literary_review_journalism",
        "previous_english_key": None,
    },
    "announcements": {
        "hierarchy_level": 3,
        "german_label": "Ankündigung",
        "german_label_plural": "Ankündigungen",
        "parent_key": "literary_review_journalism",
        "previous_english_key": None,
    },
    "author_profiles": {
        "hierarchy_level": 3,
        "german_label": "Porträt",
        "german_label_plural": "Porträts",
        "parent_key": "literary_review_journalism",
        "previous_english_key": None,
    },
    "misc_journalistic_works": {
        "hierarchy_level": 3,
        "german_label": "anderweitige journalistische Rezeption",
        "german_label_plural": None,
        "parent_key": "literary_review_journalism",
        "previous_english_key": None,
    },
    "derivative_works": {
        "hierarchy_level": 2,
        "german_label": "produktive Rezeption",
        "german_label_plural": None,
        "parent_key": "secondary_work",
        "previous_english_key": "subcategory_derivative_works",
    },
    "theatre_and_opera_performances": {
        "hierarchy_level": 3,
        "german_label": "Drama-, Opernaufführung",
        "german_label_plural": "Drama-, Opernaufführungen",
        "parent_key": "derivative_works",
        "previous_english_key": None,
    },
    "renderings_of_works_by_frischmuth": {
        "hierarchy_level": 3,
        "german_label": "Nachdichtung von Barbara Frischmuth",
        "german_label_plural": "Nachdichtungen von Barbara Frischmuth",
        "parent_key": "derivative_works",
        "previous_english_key": None,
    },
    "translations": {
        "hierarchy_level": 1,
        "german_label": "Übersetzung",
        "german_label_plural": "Übersetzungen",
        "parent_key": None,
        "previous_english_key": "main_category_translations",
    },
    "translations_of_works_other_authors": {
        "hierarchy_level": 2,
        "german_label": "Übersetzung von Werken anderer Autor:innen",
        "german_label_plural": "Übersetzungen von Werken anderer Autor:innen",
        "parent_key": "translations",
        "previous_english_key": "translations_of_works_by_others",
    },
    "translations_of_works_frischmuth": {
        "hierarchy_level": 2,
        "german_label": "Übersetzung von Werken Frischmuths",
        "german_label_plural": "Übersetzungen von Werken Frischmuths",
        "parent_key": "translations",
        "previous_english_key": "translations_of_works_by_frischmuth",
    },
    "interviews": {
        "hierarchy_level": 1,
        "german_label": "Interview",
        "german_label_plural": "Interviews",
        "parent_key": None,
        "previous_english_key": "main_category_interviews",
    },
    "correspondence": {
        "hierarchy_level": 1,
        "german_label": "Korrespondenz",
        "german_label_plural": None,
        "parent_key": None,
        "previous_english_key": "main_category_correspondence",
    },
}

WORKTYPE_MAPPINGS = {
    # "Werke --- Selbständige Publikationen [Buchpublikationen] --- Prosa [Romane, Erzählungen, Gartenbücher, Poetik-Vorlesungen etc.]": "",
    "Werke --- Selbständige Publikationen [Buchpublikationen] --- Reden": "speeches",
    "Werke --- Selbständige Publikationen [Buchpublikationen] --- Lyrik": "poetry",
    "Werke --- Selbständige Publikationen [Buchpublikationen] --- Kinder- und Jugendbücher": "literature_for_children_and_young_adults",
    "Werke --- Selbständige Publikationen [Buchpublikationen] --- Hörspiele": "radio_scripts",
    "Werke --- Selbständige Publikationen [Buchpublikationen] --- Übersetzungen von Werken anderer Autoren --- Drama": "translations_of_works_other_authors",
    # "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Prosa": "",
    # "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Reden und Essays": "",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Dramen": "dramas",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Hörspiele": "radio_scripts",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Fernsehfilme": "screenwriting",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Kinder und Jugend": "literature_for_children_and_young_adults",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Übersetzungen von Werken anderer Autoren --- Lyrik [publ. oder in audiovisuellen Medien veröff.?]": "translations_of_works_other_authors",
    "Werke --- Unselbständige Publikationen [Veröffentlichungen in Zeitungen, Zeitschriften, Anthologien und Programmheften] --- Übersetzungen von Werken anderer Autoren --- Prosa": "translations_of_works_other_authors",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Hörspiele": "radio_plays",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Fernsehfilme": "films",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Kinder und Jugend": "audiovisual_works_for_children_and_young_adults",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Hörspielübersetzungen und –bearbeitungen": "radio_drama_translations_and_adaptations",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Literatur-Sendungen": "books_and_literature_programmes",
    "Werke --- Veröffentlichungen in audiovisuellen Medien --- Diverse Beiträge in audiovisuellen Medien": "misc_audiovisual_contributions",
    "Werke --- Reden [unpubl.?]": "speeches",
    "Werke --- Dramen- und Opernaufführungen --- Werke von Barbara Frischmuth": "theatre_and_opera_performances",
    "Werke --- Dramen- und Opernaufführungen --- Übersetzungen von Barbara Frischmuth": "theatre_and_opera_performances",
    "Werke --- Dramen- und Opernaufführungen --- Nachdichtungen von Barbara Frischmuth": "theatre_and_opera_performances",
    #    "Werke --- Unveröffentlichte Werke --- Prosa": "",
    "Werke --- Unveröffentlichte Werke --- Dramen": "dramas",
    "Werke --- Unveröffentlichte Werke --- Hörspiele": "radio_scripts",
    "Werke --- Unveröffentlichte Werke --- Fernsehfilme": "screenwriting",
    #    "Werke --- Unveröffentlichte Werke --- Übersetzungen": "",
    "Sammlungen --- Publikationen von und über B. F. in Freihandaufstellung --- Primärliteratur --- Selbständige Publikationen --- Übersetzungen": "translations_of_works_frischmuth",
}

ZOTERO_CREATORS_MAPPING = {
    "artist": {
        "german_label_zotero": "Künstler",
        "property_name": "is author of",
    },
    "author": {
        "german_label_zotero": "Autor",
        "property_name": "is author of",
    },
    "bookAuthor": {
        "german_label_zotero": "Buchautor",
        "property_name": "is author of",
    },
    "composer": {
        "german_label_zotero": "Komponist",
        "property_name": "is composer of",
    },
    "contributor": {
        "german_label_zotero": "Mitarbeiter",
        "property_name": "is contributor to",
    },
    "director": {
        "german_label_zotero": "Regisseur",
        "property_name": "is director of",
    },
    "editor": {
        "german_label_zotero": "Herausgeber",
        "property_name": "is editor of",
    },
    "performer": {
        "german_label_zotero": "Darsteller",
        "property_name": "is actor in",
    },
    "presenter": {
        "german_label_zotero": "Vortragender",
        "property_name": "is author of",
    },
    "scriptwriter": {
        "german_label_zotero": "Drehbuchautor",
        "property_name": "is author of",
    },
    "seriesEditor": {
        "german_label_zotero": "Hrsg. der Reihe",
        "property_name": "is editor of",
    },
    "translator": {
        "german_label_zotero": "Übersetzer",
        "property_name": "is translator of",
    },
    "wordsBy": {
        "german_label_zotero": "Text von",
        "property_name": "is author of",
    },
}
