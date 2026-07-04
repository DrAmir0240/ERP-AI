from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AccountSale


@receiver(post_save, sender=AccountSale)
def increment_sold_count(sender, instance, created, **kwargs):
    if created:
        instance.account.__class__.objects.filter(pk=instance.account_id).update(
            sold_count=F("sold_count") + 1
        )


@receiver(post_delete, sender=AccountSale)
def decrement_sold_count(sender, instance, **kwargs):
    instance.account.__class__.objects.filter(pk=instance.account_id).update(
        sold_count=F("sold_count") - 1
    )
