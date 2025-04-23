from celery import shared_task
from .google_sheet_data import add_family_head_to_sheet, add_member_to_sheet
from django.core.management import call_command



@shared_task
def export_samaj_summary():
    call_command('export_samaj_summary')
    

@shared_task
def add_family_head_to_sheet_task(family_head_id):
    from .models import FamilyHead
    try:
        instance = FamilyHead.objects.get(id=family_head_id)
        add_family_head_to_sheet(instance)
    except FamilyHead.DoesNotExist:
        pass

@shared_task
def add_member_to_sheet_task(member_id):
    from .models import Member
    try:
        instance = Member.objects.get(id=member_id)
        add_member_to_sheet(instance)
    except Member.DoesNotExist:
        pass
