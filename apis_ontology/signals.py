import logging

from apis_core.apis_metainfo.models import RootObject
from apis_core.apis_metainfo.signals import post_duplicate
from django.dispatch import receiver


logger = logging.getLogger(__name__)


@receiver(post_duplicate)
def update_duplicates(sender, instance, duplicate, **kwargs):
    """
    Update field values of already-saved duplicates of entity objects
    for easier differentiation and/or to remove ambiguity.

    :param sender: the model class
    :param instance: the original object
    :param duplicate: the original object's copy
    """
    if isinstance(duplicate, RootObject):
        orig_id = instance.id
        available_fields = [f.name for f in duplicate._meta.fields]

        valid_fields = []
        update_fields = {
            "data_source": None,
            "progress_status": "created",
            "notes": f"Duplicate of {orig_id}",
        }

        for f, v in update_fields.items():
            if f in available_fields:
                valid_fields.append(f)
                setattr(duplicate, f, v)

        duplicate.save(update_fields=valid_fields)
