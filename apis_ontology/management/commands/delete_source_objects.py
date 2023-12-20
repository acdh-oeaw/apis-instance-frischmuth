import itertools
from django.core.management.base import BaseCommand
from apis_core.apis_metainfo.models import Source
from apis_core.utils.caching import (
    get_all_entity_class_names,
    get_entity_class_of_name,
)


class Command(BaseCommand):
    # TODO allow removal of source itself when/once empty

    help = "Delete entity objects from specific Sources."

    all_sources = Source.objects.all()
    source_names = [s.orig_filename for s in all_sources]
    # allow targeting of objects which don't belong to a Source; useful
    # e.g. when objects were previously imported without assigning a Source
    # or when a Source was deleted (by name) but its objects remained
    # TODO rework 'NULL' sources so they remain available as an option
    #  but aren't included when deleting 'ALL_SOURCES'
    source_names.append("NULL")

    missing_args_message = (
        "\n"
        "You need to provide both the name of a source "
        "and an entity to delete from it!"
    )

    def add_arguments(self, parser):
        # optional arguments
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-l",
            "--list",
            dest="list",
            action="store_const",
            const=True,
            help="List all available sources.",
        )
        # positional arguments (required)
        parser.add_argument(
            "source",
            nargs=1,
            type=str,
            help="Name of source for which to remove entity objects.",
        )
        parser.add_argument(
            "entity",
            nargs="+",
            type=str,
            help="Name of model class from which to remove those objects.",
        )
        # optional arguments
        parser.add_argument(
            "-n",
            "--dry-run",
            dest="skip",
            action="store_const",
            const=True,
            help="Dry-run deletion action. "
            "Does not actually delete objects from the database.",
        )

    def handle(self, *args, **options):
        src_id = "-1"
        msg_prefix = ""
        skip = None
        source_obj = None
        entities = []
        entities_failed = []

        all_sources = Source.objects.all()
        all_entities = get_all_entity_class_names()
        entity_names = [m for m in all_entities]

        if options["skip"]:
            skip = True
            msg_prefix = "DRY RUN – "

        source_name = options["source"][0]
        if source_name == "ALL_SOURCES":
            source_obj = Source.objects.all()
        elif source_name != "NULL":
            source_obj = Source.objects.filter(orig_filename=source_name)
            if len(source_obj) == 0:
                for src in self.source_names:
                    self.stdout.write(src)
                self.stdout.write(
                    self.style.ERROR(
                        f"The supplied Source {source_name} does not exist, "
                        f"please choose one from the above list."
                    )
                )
                exit(1)
            else:
                if len(source_obj) > 1:
                    self.stdout.write(
                        "There are several source objects with the given name. "
                        "Please provide the ID for the source from which to delete objects:"
                    )
                    src_ids = list(source_obj.values_list("id", flat=True))
                    src_ids_str = [str(x) for x in src_ids]
                    src_ids_str.append("ALL")

                    for src in source_obj:
                        self.stdout.write(
                            f"{src.id}, {src.orig_filename}, {src.pubinfo}"
                        )

                    while src_id not in src_ids_str and src_id != "ALL":
                        src_id = input()

                    if src_id != "ALL":
                        source_obj = Source.objects.get(id=src_id)
        else:
            source_name = "(NULL)"
            source_obj = Source.objects.filter(orig_filename=source_name)

        entities_provided = options["entity"]
        for ent_prov in entities_provided:
            ent = ent_prov.split(",")
            entities.extend(ent)

        if entities[0] == "ALL_ENTITIES":
            # shortcut to allow deletion of all entity objects
            # with a given source
            entities = entity_names

        for ent in entities:
            if ent not in entity_names:
                entities_failed.append(ent)
            else:
                ent_class = get_entity_class_of_name(ent)

                # if len(source_obj) > 1:
                #     print(source_obj[0].orig_filename)
                #     exit()
                # else:
                try:
                    ent_obj = ent_class.objects.filter(source__in=source_obj)
                except:
                    print(f"No objects left for source {source_obj.orig_filename}.")
                    exit(0)

                if not source_obj:
                    ent_obj = ent_class.objects.filter(source__isnull=True)

                obj_count = len(ent_obj)

                success_msg = (
                    f"Deleted {obj_count} {ent} objects from Source " f"{source_name}"
                )
                nothing_todo_msg = (
                    f"No {ent} objects to delete from Source {source_name}."
                )

                if skip:
                    success_msg = msg_prefix + success_msg
                    nothing_todo_msg = msg_prefix + nothing_todo_msg

                if obj_count > 0:
                    self.stdout.write(self.style.SUCCESS(success_msg))
                    for obj in ent_obj:
                        delete_msg = f".. Deleted {ent} object {obj}."
                        delete_err_msg = f"Failed to delete '{obj}'."
                        if skip:
                            delete_msg = msg_prefix + delete_msg
                            delete_err_msg = msg_prefix + delete_err_msg

                        try:
                            if not skip:
                                obj.delete()
                            self.stdout.write(delete_msg)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(delete_err_msg))
                            self.stdout.write(self.style.ERROR(e))

                else:
                    self.stdout.write(nothing_todo_msg)

        if len(entities_failed) > 0:
            self.stdout.write(self.style.ERROR("The following entities do not exist:"))

            for ent in entities_failed:
                self.stdout.write(self.style.ERROR(ent))

            self.stdout.write("Available entities:")
            self.stdout.write(", ".join(entity_names))
