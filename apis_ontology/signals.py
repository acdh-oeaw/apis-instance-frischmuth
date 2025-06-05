from apis_core.apis_relations.models import TempTriple
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender=TempTriple)
def set_primary_work(sender, instance, **kwargs):
    if (
        instance.prop_id == 24 and instance.subj_id == 19306
    ):  # `is author of` & author == Frischmuth
        if not instance.obj.primary_work:
            instance.obj.primary_work = True
            instance.obj.save()
    elif instance.prop_id == 24:
        if instance.obj.primary_work:
            instance.obj.primary_work = False
            instance.obj.save()


@receiver(post_delete, sender=TempTriple)
def unset_primary_work(sender, instance, **kwargs):
    if (
        instance.prop_id == 24 and instance.subj_id == 19306
    ):  # `is author of` & author == Frischmuth
        if instance.obj.primary_work:
            instance.obj.primary_work = False
            instance.obj.save()
