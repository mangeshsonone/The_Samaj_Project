# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import FamilyHead, Member
# from .tasks import add_family_head_to_sheet_task, add_member_to_sheet_task

# @receiver(post_save, sender=FamilyHead)
# def add_family_head_to_google_sheet(sender, instance, created, **kwargs):
#     if created:
#         add_family_head_to_sheet_task.delay(instance.id)

# @receiver(post_save, sender=Member)
# def add_member_to_google_sheet(sender, instance, created, **kwargs):
#     if created:
#         add_member_to_sheet_task.delay(instance.id)
#####################################################################

# import requests
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import FamilyHead, Member

# GOOGLE_SHEETS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzep8DbvquVrcg3mBOaxCVnfiSoHgvSmeC7cjzNudpVtfPeEWLhnpDbXm-0_upFkD5C/exec"

# def send_data_to_google_sheet(payload):
#     try:
#         response = requests.post(
#             GOOGLE_SHEETS_SCRIPT_URL,
#             json=payload,
#             headers={"Content-Type": "application/json"}
#         )
#         print("Sheets update response:", response.text)
#     except Exception as e:
#         print("Error sending data to Sheets:", str(e))

# @receiver(post_save, sender=FamilyHead)
# @receiver(post_save, sender=Member)
# def update_sheet_on_save(sender, instance, created, **kwargs):
#     if not created:
#         return

#     if isinstance(instance, FamilyHead):
#         family = instance.family
#         samaj_name = family.samaj.samaj_name

#         total_members = family.member_set.count()
#         entered_members = family.member_set.exclude(name__isnull=True).count()  # Adjust based on criteria
#         remaining_members = total_members - entered_members

#         payload = {
#             "created_at": instance.created_at.strftime("%Y-%m-%d %H:%M") if instance.created_at else "",
#             "samaj": samaj_name,
#             "head_name": f"{instance.name_of_head} {instance.middle_name} {instance.last_name}".strip(),
#             "total_members": total_members,
#             "entered_members": entered_members,
#             "remaining_members": remaining_members,

#             "name": instance.name_of_head,
#             "middle_name": instance.middle_name,
#             "last_name": instance.last_name,
#             "birth_date": instance.birth_date.strftime('%Y-%m-%d') if instance.birth_date else '',
#             "age": instance.age,
#             "gender": instance.gender,
#             "marital_status": instance.marital_status,
#             "relation_with_head": "self",  # Since it's the family head
#             "phone_no": instance.phone_no,
#             "alternative_no": instance.alternative_no,
#             "landline_no": instance.landline_no,
#             "email_id": instance.email_id,
#             "country": instance.country,
#             "state": instance.state,
#             "district": instance.district,
#             "pincode": instance.pincode,
#             "building_name": instance.building_name,
#             "flat_no": instance.flat_no,
#             "door_no": instance.door_no,
#             "street_name": instance.street_name,
#             "landmark": instance.landmark,
#             "native_city": instance.native_city,
#             "native_state": instance.native_state,
#             "qualification": instance.qualification,
#             "occupation": instance.occupation,
#             "duties": instance.exact_nature_of_duties,
#             "blood_group": instance.blood_group,
#             "social_media": instance.social_media_link,
#         }

#         send_data_to_google_sheet(payload)

#     elif isinstance(instance, Member):
#         head = instance.family.familyhead
#         samaj_name = instance.family.samaj.name
#         total_members = instance.family.member_set.count()
#         entered_members = instance.family.member_set.exclude(name__isnull=True).count()
#         remaining_members = total_members - entered_members

#         payload = {
#             "created_at": instance.created_at.strftime("%Y-%m-%d %H:%M"),
#             "samaj": samaj_name,
#             "head_name": f"{head.name} {head.middle_name} {head.last_name}",
#             "total_members": total_members,
#             "entered_members": entered_members,
#             "remaining_members": remaining_members,
#             "name": instance.name,
#             "middle_name": instance.middle_name,
#             "last_name": instance.last_name,
#             "birth_date": instance.birth_date,
#             "age": instance.age,
#             "gender": instance.gender,
#             "marital_status": instance.marital_status,
#             "relation_with_head": instance.relation_with_head,
#             "phone_no": instance.phone_no,
#             "alternative_no": instance.alternative_no,
#             "landline_no": instance.landline_no,
#             "email_id": instance.email_id,
#             "country": instance.country,
#             "state": instance.state,
#             "district": instance.district,
#             "pincode": instance.pincode,
#             "building_name": instance.building_name,
#             "flat_no": instance.flat_no,
#             "door_no": instance.door_no,
#             "street_name": instance.street_name,
#             "landmark": instance.landmark,
#             "native_city": instance.native_city,
#             "native_state": instance.native_state,
#             "qualification": instance.qualification,
#             "occupation": instance.occupation,
#             "duties": instance.exact_nature_of_duties,
#             "blood_group": instance.blood_group,
#             "social_media": instance.social_media_link,
#         }
#         send_data_to_google_sheet(payload)

