import importlib
import logging

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        script = importlib.import_module(
            f"apis_ontology.scripts.{options['ontology_script']}"
        )
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {options['ontology_script']}")
        script.run()

    def add_arguments(self, parser):
        parser.add_argument("ontology_script")
