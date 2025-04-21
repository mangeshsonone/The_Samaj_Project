from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FamilyHead, Member
from .tasks import add_family_head_to_sheet_task, add_member_to_sheet_task

@receiver(post_save, sender=FamilyHead)
def add_family_head_to_google_sheet(sender, instance, created, **kwargs):
    if created:
        add_family_head_to_sheet_task.delay(instance.id)

@receiver(post_save, sender=Member)
def add_member_to_google_sheet(sender, instance, created, **kwargs):
    if created:
        add_member_to_sheet_task.delay(instance.id)
