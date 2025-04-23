import gspread
from itertools import chain
from operator import attrgetter
from .models import Samaj, Family, FamilyHead, Member



gc = gspread.service_account(filename="testapp/credentials.json")
sh = gc.open_by_key('1qdJcSbquB9-guAeqxsWRTr7sn33GjkCa_8ZERYpIf2M')
worksheet = sh.worksheet("Sheet1")

    # return worksheet  # Or use .worksheet('SheetName') if you use a named sheet


def format_family_head_row(head):
    family = head.family
    samaj = family.samaj
    number_of_members = Member.objects.filter(family_head=head).count() + 1
    remaining_members = family.total_family_members - number_of_members

    return [
        head.created_at.strftime('%Y-%m-%d %H:%M:%S') if head.created_at else '',
        samaj.samaj_name,
        f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
        family.total_family_members,
        number_of_members,
        remaining_members,
        
        head.name_of_head,
        head.middle_name,
        head.last_name,
        head.birth_date.strftime('%Y-%m-%d') if head.birth_date else '',
        head.age,
        head.gender,
        head.marital_status,
        "self",
        head.phone_no,
        head.alternative_no,
        head.landline_no,
        head.email_id,
        head.country,
        head.state,
        head.district,
        head.pincode,
        head.building_name,
        head.flat_no,
        head.door_no,
        head.street_name,
        head.landmark,
        head.native_city,
        head.native_state,
        head.qualification,
        head.occupation,
        head.exact_nature_of_duties,
        head.blood_group,
        head.social_media_link
    ]


def format_member_row(member):
    head = member.family_head
    family = head.family
    samaj = family.samaj
    number_of_members = Member.objects.filter(family_head=head).count() + 1
    remaining_members = family.total_family_members - number_of_members

    return [
        member.created_at.strftime('%Y-%m-%d %H:%M:%S') if member.created_at else '',
        samaj.samaj_name,
        f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
        family.total_family_members,
        number_of_members,
        remaining_members,
        
        member.name,
        member.middle_name,
        member.last_name,
        member.birth_date.strftime('%Y-%m-%d') if member.birth_date else '',
        member.age,
        member.gender,
        member.marital_status,
        member.relation_with_family_head,
        member.phone_no,
        member.alternative_no,
        member.landline_no,
        member.email_id,
        member.country,
        member.state,
        member.district,
        member.pincode,
        member.building_name,
        member.flat_no,
        member.door_no,
        member.street_name,
        member.landmark,
        member.native_city,
        member.native_state,
        member.qualification,
        member.occupation,
        member.exact_nature_of_duties,
        member.blood_group,
        member.social_media_link
    ]

a=1
print("hello")
def export_all_to_sheet():
    print("inside")
    

    heads = FamilyHead.objects.all()
    members = Member.objects.all()

    combined = sorted(chain(heads, members), key=attrgetter('created_at'))

    for obj in combined:
        if isinstance(obj, FamilyHead):
            row = format_family_head_row(obj)
        else:
            row = format_member_row(obj)

        worksheet.append_row(row)  # ✅ Append row to Google Sheet


export_all_to_sheet()
