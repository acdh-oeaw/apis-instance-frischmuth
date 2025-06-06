from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
import csv


def create_doublette_csv(model, field, file_name):
    cl = ContentType.objects.get(
        app_label="apis_ontology", model=model.lower()
    ).model_class()
    lst_field = [getattr(x, field) for x in cl.objects.all()]
    lst_field = set([x.lower() if x else "-" for x in lst_field])
    res = []
    for s in lst_field:
        ws = cl.objects.filter(**{f"{field}__iexact": s})
        if ws.count() > 1:
            title = "|".join([str(x) for x in ws])
            id = "|".join([str(x) for x in ws.values_list("id", flat=True)])
            url = "|".join(
                [
                    f"https://frischmuth-dev.acdh-dev.oeaw.ac.at/apis/apis_ontology.{model.lower()}/update/{x}"
                    for x in ws.values_list("id", flat=True)
                ]
            )
            res.append({"id": id, "title": title, "url": url})
    with open(file_name, "w", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=res[0].keys())
        writer.writeheader()
        for row in res:
            writer.writerow(row)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("model", nargs="+", type=str)
        parser.add_argument("field", nargs="+", type=str)
        parser.add_argument("file_name", nargs="+", type=str)

    def handle(self, *args, **options):
        create_doublette_csv(
            options["model"][0], options["field"][0], options["file_name"][0]
        )
