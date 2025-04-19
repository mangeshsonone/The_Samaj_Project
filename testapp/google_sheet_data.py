

# # Set the path for Django settings
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Set up Django settings module
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "The_Samaj_Project.settings")
# django.setup()

# # Now you can import the models after Django setup
# from testapp.models import Samaj, Family, FamilyHead, Member

from gspread import worksheet
import gspread

from .models import Samaj,Family,FamilyHead,Member



gc=gspread.service_account(filename="testapp/credentials.json")

sh=gc.open_by_key('1qdJcSbquB9-guAeqxsWRTr7sn33GjkCa_8ZERYpIf2M')
for ws in sh.worksheets():
    print(ws.title)

worksheet = sh.worksheet("Sheet1")



# student=["jay",20,"mumbai"]
# worksheet.insert_row(student,1)
# res=worksheet.get_all_records()
# print(res) 







# def adddata():
#     def add_headers_if_missing_for_members(worksheet):
#         current_headers = worksheet.row_values(1)

#         # Dynamically create headers based on the FamilyHead and Member models
#         # valid_head_fields = get_model_fields(FamilyHead)
#         # valid_member_fields = get_model_fields(Member)
        

#         # Combine valid fields to create a comprehensive header list
#         all_headers =[
#                 "Created At",
#                 'Samaj',
#                 'Total Members',
#                 'Number of Members Entered',
#                 'Remaining Members to Enter',
#                 'Head',
#                 "Name",
#                 "Middle Name",
#                 "Last Name",
#                 "Birth Date",
#                 "Age",
                
#                 "Gender",
#                 "Marital Status",
#                 "Relation with Head",
                
#             # Contact Details
#                 "Phone_no",
#                 "Alternative_no",
#                 "Landline_no",
#                 "Email_id",

#             # Address
#                 "Country",
#                 "State",
#                 "District",
#                 "Pincode",
#                 "Building Name",
#                 "Flat_no",  # Includes Ward No/Flat No
#                 "Door_no",
#                 "Street Name",
#                 "Landmark",
#                 "Native City",
#                 "Native State",
                
                
#                 # Professional Details
#                 "Qualification",
#                 "Occupation",
#                 "Exact nature of duties",
                
#                 # Medical Details
#                 "Blood Group",
#                 "Social Media Link"
                
#     ] 
#         # + list(valid_member_fields)

#         # Check if the current headers match the expected headers
#         if not current_headers or current_headers != all_headers:
#             worksheet.insert_row(all_headers, 1)
#             print("Headers added to the Google Sheet.")
#         else:
#             print("Headers already exist in the Google Sheet, skipping header addition.")

        


#     add_headers_if_missing_for_members(worksheet)


#     # Iterate through the Samaj objects and their related data
# rows_to_append = []

#     # Iterate through the Samaj objects and their related data

# family_heads = FamilyHead.objects.select_related('family__samaj').order_by('created_at')
# for head in family_heads:
#     samaj = head.family.samaj
#     family = head.family
#     number_of_members = Member.objects.filter(family_head=head).count()+1

#                 # Prepare Family Head data to insert into Google Sheet
#     remaning_members=family.total_family_members-number_of_members
#     head_row = [
#         head.created_at.strftime('%Y-%m-%d %H:%M:%S') if head.created_at else '',
#         samaj.samaj_name,                    # samaj
#         family.total_family_members,         # total members
#         number_of_members,
#         remaning_members,
#         head.name_of_head,                   # head name
#         head.name_of_head,
#         head.middle_name,                    # middle name
#         head.last_name,                      # last name
#         head.birth_date.strftime('%Y-%m-%d') if head.birth_date else '',  # birth date (converted to string)
#         head.age,                            # age
#         head.gender,                         # gender
#         head.marital_status,                 # marital status
#         "self",                              # relation with family head (self for head)
#         head.phone_no,                       # phone no
#         head.alternative_no,                 # alternative no
#         head.landline_no,                    # landline no
#         head.email_id,                       # email id
#         head.country,                        # country
#         head.state,                          # state
#         head.district,                       # district
#         head.pincode,                        # pincode
#         head.building_name,                  # building name
#         head.flat_no,                        # flat no
#         head.door_no,                        # door no
#         head.street_name,                    # street name
#         head.landmark,                       # landmark
#         head.native_city,                    # native city
#         head.native_state,                   # native state
#         head.qualification,                  # qualification
#         head.occupation,                     # occupation
#         head.exact_nature_of_duties,         # exact nature of duties
#         head.blood_group,                    # blood group
#         head.social_media_link               # social media link
        
#     ]
    
#     # Add Family Head row to the list
#     rows_to_append.append(head_row)
#     # worksheet.append_row(head_row)
#     print(f"Prepared Family Head: {head.name_of_head} to be added to the Google Sheet")


#     members = Member.objects.filter(family_head=head)
#     # Now, for each Member related to the FamilyHead
#     for member in members:
#         # Prepare Member data to insert into Google Sheet
#         member_row = [
#             member.created_at.strftime('%Y-%m-%d %H:%M:%S') if member.created_at else '',
#             samaj.samaj_name,                    # samaj
#             family.total_family_members,         # total members
#             "",
#             "",
#             head.name_of_head,                   # head name
#             member.name,
#             member.middle_name,                  # middle name
#             member.last_name,                    # last name
#             member.birth_date.strftime('%Y-%m-%d') if member.birth_date else '',  # birth date (converted to string)
#             member.age,                          # age
#             member.gender,                       # gender
#             member.marital_status,               # marital status
#             member.relation_with_family_head,                              # relation with family head (self for head)
#             member.phone_no,                     # phone no
#             member.alternative_no,               # alternative no
#             member.landline_no,                  # landline no
#             member.email_id,                     # email id
#             member.country,                      # country
#             member.state,                        # state
#             member.district,                     # district
#             member.pincode,                      # pincode
#             member.building_name,                # building name
#             member.flat_no,                      # flat no
#             member.door_no,                      # door no
#             member.street_name,                  # street name
#             member.landmark,                     # landmark
#             member.native_city,                  # native city
#             member.native_state,                 # native state
#             member.qualification,                # qualification
#             member.occupation,                   # occupation
#             member.exact_nature_of_duties,       # exact nature of duties
#             member.blood_group,                  # blood group
#             member.social_media_link             # social media link
            
#         ]
        
#         # Add Member row to the list
#         rows_to_append.append(member_row)
#         # worksheet.append_row(member_row)
#         print(f"Prepared Member: {member.name} to be added to the Google Sheet")


# adddata()

# # # Once all rows are collected, append them all at once
# if rows_to_append:
#     worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
#     print(f"Added {len(rows_to_append)} rows to the Google Sheet")
# # # Call the function to add the data

