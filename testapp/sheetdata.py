from .models import Samaj, Family, FamilyHead, Member

from gspread import worksheet
import gspread

# from .models import Samaj,Family,FamilyHead,Member



gc=gspread.service_account(filename="testapp/credentials.json")

sh=gc.open_by_key('1GT5mk7bnFBIzCBrQgF1G8AmQfW024WRt-IREw9dLN2g')
for ws in sh.worksheets():
    print(ws.title)

worksheet = sh.worksheet("Sheet1")



# student=["jay",20,"mumbai"]
# worksheet.insert_row(student,1)
# res=worksheet.get_all_records()
# print(res) 








def add_headers_if_missing_for_members(worksheet):
    current_headers = worksheet.row_values(1)

    # Dynamically create headers based on the FamilyHead and Member models
    # valid_head_fields = get_model_fields(FamilyHead)
    # valid_member_fields = get_model_fields(Member)
    

    # Combine valid fields to create a comprehensive header list
    all_headers =[
            'samaj',
            'total members',
            'head'
            "name",
            "middle_name",
            "last_name",
            "birth_date",
            "age",
            
            "gender",
            "marital_status",
            "relation_with_family_head",
            
           # Contact Details
            "phone_no",
            "alternative_no",
            "landline_no",
            "email_id",

           # Address
            "country",
            "state",
            "district",
            "pincode",
            "building_name",
            "flat_no",  # Includes Ward No/Flat No
            "door_no",
            "street_name",
            "landmark",
            "native_city",
            "native_state",
            
            
            # Professional Details
            "qualification",
            "occupation",
            "exact_nature_of_duties",
            
            # Medical Details
            "blood_group",
            "social_media_link",
] 
    # + list(valid_member_fields)

    # Check if the current headers match the expected headers
    if not current_headers or current_headers != all_headers:
        worksheet.insert_row(all_headers, 1)
        print("Headers added to the Google Sheet.")
    else:
        print("Headers already exist in the Google Sheet, skipping header addition.")

add_headers_if_missing_for_members(worksheet)

# samaj_list = Samaj.objects.all().prefetch_related(
#     'family_set__familyhead_set__member_set'
# )

# # Iterate through the Samaj objects and their related data
# for samaj in samaj_list:
#     print(f"Samaj: {samaj.samaj_name}")
    
#     # For each Family in the Samaj
#     for family in samaj.family_set.all():
#         print(f"  Family: {family.id} - Total Members: {family.total_family_members}")
        
#         # For each FamilyHead in the Family
#         for head in family.familyhead_set.all():
#             print(f"    Family Head: {head.name_of_head}")
            
#             # For each Member related to the FamilyHead
#             for member in head.member_set.all():
#                 print(f"      Member: {member.name} ({member.relation_with_family_head})")


samaj=Samaj.objects.all()
for i in samaj:
    print(i)

family=FamilyHead.objects.all()
for j in family:
    print(j)