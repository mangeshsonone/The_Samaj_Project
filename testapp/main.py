from gspread import worksheet
import gspread



gc=gspread.service_account(filename="testapp/credentials.json")

# sh=gc.open_by_key('1FGVaIV1Hk_YDRpr71wWx-J65MV0YeZpA4yGw3K0lCrA')
sh=gc.open_by_key('1qdJcSbquB9-guAeqxsWRTr7sn33GjkCa_8ZERYpIf2M')

for ws in sh.worksheets():
    print(ws.title)

worksheet = sh.worksheet("Sheet1")



student=["jay",20,"mumbai"]
worksheet.insert_row(student,1)
# res=worksheet.get_all_records()
# print(res) 
# ws = sh.worksheet("Samaj_sheet1")
