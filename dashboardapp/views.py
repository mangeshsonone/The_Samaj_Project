from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member
import requests
from django.http import JsonResponse

class DashboardDataAPIView(APIView):
    def get(self, request):
        b=20
        samaj_data = []
        incomplete_heads = []
        a=10
        samajs = Samaj.objects.all()
        for samaj in samajs:
            families = Family.objects.filter(samaj=samaj)
            valid_families = families.filter(
                id__in=FamilyHead.objects.filter(family__in=families).values('family_id')
            )
            family_heads = FamilyHead.objects.filter(family__in=valid_families)
            members = Member.objects.filter(family_head__in=family_heads)

            total_heads = family_heads.count()
            total_expected = valid_families.aggregate(total=Sum('total_family_members'))['total'] or 0
            actual_members = members.count() + total_heads
            remaining = max(total_expected - actual_members, 0)

            samaj_data.append({
                "name": samaj.samaj_name,
                "families": total_heads,
                "members": actual_members,
                "needed": total_expected,
            })

            for head in family_heads:
                expected = head.family.total_family_members
                entered = Member.objects.filter(family_head=head).count()
                with_head = entered + 1
                missing = expected - with_head
                if missing > 0:
                    incomplete_heads.append({
                        "samaj": samaj.samaj_name,
                        "head": head.name_of_head,
                        "phone": head.phone_no,
                        "expected": expected,
                        "entered": with_head,
                        "missing": missing
                    })

        return Response({
            "chart_data": samaj_data,
            "incomplete_heads": incomplete_heads,
        })


def send_to_google_sheet(request):
    

    GOOGLE_SHEETS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwbpJTHWrz4GRZtKzAJSppQN0eEOT3LOlQC3LFE4Rg8U7vBegnHlaKznFi-KQ1jqQh_Gw/exec"

    payload = {
        "created_at": "2025-04-25 12:00",
        "samaj": "Test Samaj",
        "head_name": "John Middle Doe",
        "total_members": "4",
        "entered_members": "3",
        "remaining_members": "1",

        "name": "John",
        "middle_name": "Middle",
        "last_name": "Doe",
        "birth_date": "1980-01-01",
        "age": "45",
        "gender": "Male",
        "marital_status": "Married",
        "relation_with_head": "Self",
        "phone_no": "1234567890",
        "alternative_no": "0987654321",
        "landline_no": "",
        "email_id": "john.doe@example.com",
        "country": "India",
        "state": "Gujarat",
        "district": "Ahmedabad",
        "pincode": "380015",
        "building_name": "Green Towers",
        "flat_no": "202",
        "door_no": "",
        "street_name": "CG Road",
        "landmark": "Near XYZ Mall",
        "native_city": "Surat",
        "native_state": "Gujarat",
        "qualification": "MBA",
        "occupation": "Manager",
        "duties": "HR",
        "blood_group": "B+",
        "social_media": "https://linkedin.com/in/johndoe"
    }
    payload = {k: str(v) if v is not None else '' for k, v in payload.items()}

    headers = {"Content-Type": "application/json"}
    response = requests.post(GOOGLE_SHEETS_SCRIPT_URL, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

import requests
from django.http import JsonResponse
import json

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbz6J3rfOkqg5X8PGC6Vy0MjSPl622imPlR_Pmt5ugk8hqtu17QEsu39prNJ77Xh-34C/exec"

@csrf_exempt
def send_datatosheet(request):
    if request.method == 'GET':  # Using GET so you can hit it from the browser
        payload = {
            'name': 'HardcodedUser',
            'age': 30,
            'pin': '400001'
        }

        try:
            headers = {'Content-Type': 'application/json'}  # Set the content type to JSON
            response = requests.post(GOOGLE_SHEET_URL, data=json.dumps(payload), headers=headers)

            if response.status_code == 200:
                return JsonResponse({"message": "Data sent to Google Sheets!"}, status=200)
            else:
                return JsonResponse({"error": "Google Sheet error"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only GET allowed for testing"}, status=405)

    # else:
    #     return JsonResponse({"error": "Invalid HTTP method"}, status=405)


