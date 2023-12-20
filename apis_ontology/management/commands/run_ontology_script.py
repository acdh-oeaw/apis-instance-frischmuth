from django.core.management.base import BaseCommand
import importlib


class Command(BaseCommand):
    def handle(self, *args, **options):
        script = importlib.import_module(
            f"apis_ontology.scripts.{options['ontology_script']}"
        )
        script.run()

    def add_arguments(self, parser):
        parser.add_argument("ontology_script")
