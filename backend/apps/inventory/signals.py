from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import StockItem, StockMovement


@receiver(pre_save, sender=StockItem)
def remember_previous_stock_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_branch = None
        instance._previous_status = None
        return
    previous = sender.objects.filter(pk=instance.pk).only("branch", "status").first()
    instance._previous_branch = previous.branch if previous else None
    instance._previous_status = previous.status if previous else None


@receiver(post_save, sender=StockItem)
def create_stock_movement(sender, instance, created, **kwargs):
    if getattr(instance, "_skip_stock_movement", False):
        return
    previous_branch = getattr(instance, "_previous_branch", None)
    previous_status = getattr(instance, "_previous_status", None)
    movement_type = getattr(instance, "_movement_type", "")
    if not movement_type:
        movement_type = infer_movement_type(instance, created, previous_branch, previous_status)
    if not movement_type:
        return
    StockMovement.objects.create(
        item=instance,
        movement_type=movement_type,
        from_branch=getattr(instance, "_movement_from_branch", previous_branch),
        to_branch=getattr(instance, "_movement_to_branch", instance.branch),
        order_id=getattr(instance, "_movement_order_id", None),
        user=getattr(instance, "_movement_user", None),
        note=getattr(instance, "_movement_note", ""),
    )


def infer_movement_type(instance, created, previous_branch, previous_status):
    if created:
        return StockMovement.TYPE_PURCHASE
    if previous_branch and previous_branch != instance.branch:
        return StockMovement.TYPE_TRANSFER_IN
    if previous_status == instance.status:
        return ""
    if instance.status == StockItem.STATUS_SOLD:
        return StockMovement.TYPE_SALE
    if instance.status == StockItem.STATUS_RETURNED:
        return StockMovement.TYPE_RETURN
    if instance.status == StockItem.STATUS_TRANSFERRED:
        return StockMovement.TYPE_TRANSFER_OUT
    return StockMovement.TYPE_ADJUSTMENT
