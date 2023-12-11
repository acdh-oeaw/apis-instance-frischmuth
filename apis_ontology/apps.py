from django.apps import AppConfig


class ApisOntologyConfig(AppConfig):
    """
    Config which gets loaded automatically when the app with the
    given name – apis_ontology, in this case – is included in
    INSTALLED_APPS in apis/settings/base.py

    See https://docs.djangoproject.com/en/4.1/ref/applications/#for-application-authors
    for more details.
    """

    name = "apis_ontology"
