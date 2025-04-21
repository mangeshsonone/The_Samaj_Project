from gspread import worksheet
import gspread
from testapp.models import Samaj, FamilyHead, Member


gc=gspread.service_account(filename="testapp/credentials.json")

# sh=gc.open_by_key('1FGVaIV1Hk_YDRpr71wWx-J65MV0YeZpA4yGw3K0lCrA')
sh=gc.open_by_key('1oNshnFH2JhTdxSx7-7NZz8D1Aq15_Qp9jj9Pt0VMkQo')
worksheet = sh.worksheet("Sheet1")
a=10
# worksheet.clear()

# Pre-calculate totals
worksheet.append_row(["Samaj Name", "Family Heads Count", "Total Members (incl. Heads)"])

# Counters
grand_total_family_heads = 0
grand_total_members = 0

# Loop through each Samaj
for samaj in Samaj.objects.all():
    family_heads_count = FamilyHead.objects.filter(family__samaj=samaj).count()
    members_count = Member.objects.filter(family_head__family__samaj=samaj).count()
    total_people = family_heads_count + members_count

    grand_total_family_heads += family_heads_count
    grand_total_members += total_people

    worksheet.append_row([
        samaj.samaj_name,
        family_heads_count,
        total_people
    ])

# Grand Total row
worksheet.append_row([])
worksheet.append_row(["Grand Total", grand_total_family_heads, grand_total_members])

# student=["jay",20,"mumbai"]
# worksheet.insert_row(student,1)
# # res=worksheet.get_all_records()
# # print(res) 
# # ws = sh.worksheet("Samaj_sheet1")
