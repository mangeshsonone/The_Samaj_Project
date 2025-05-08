from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member
import requests
from django.http import JsonResponse
import logging
import time
logger = logging.getLogger(__name__)

class DashboardDataAPIView(APIView):
    def get(self, request):
        logger.info("Dashboard data API requested")
        start_time = time.time()
        
        b = 20
        c = 50
        samaj_data = []
        incomplete_heads = []
        a = 10
        
        try:
            logger.debug("Fetching all Samaj records")
            samajs = Samaj.objects.all()
            logger.info(f"Found {samajs.count()} Samaj records")
            
            for samaj in samajs:
                logger.debug(f"Processing Samaj: {samaj.samaj_name}")
                
                try:
                    # Get families for this samaj
                    families = Family.objects.filter(samaj=samaj)
                    logger.debug(f"Found {families.count()} families for Samaj: {samaj.samaj_name}")
                    
                    # Filter for valid families (those that have family heads)
                    valid_families = families.filter(
                        id__in=FamilyHead.objects.filter(family__in=families).values('family_id')
                    )
                    logger.debug(f"Valid families with heads: {valid_families.count()}")
                    
                    # Get family heads and members
                    family_heads = FamilyHead.objects.filter(family__in=valid_families)
                    logger.debug(f"Found {family_heads.count()} family heads")
                    
                    members = Member.objects.filter(family_head__in=family_heads)
                    logger.debug(f"Found {members.count()} members (excluding heads)")
                    
                    # Calculate statistics
                    total_heads = family_heads.count()
                    total_expected = valid_families.aggregate(total=Sum('total_family_members'))['total'] or 0
                    actual_members = members.count() + total_heads
                    remaining = max(total_expected - actual_members, 0)
                    
                    logger.info(f"Samaj {samaj.samaj_name} stats - Families: {total_heads}, Members: {actual_members}, Expected: {total_expected}, Remaining: {remaining}")
                    
                    # Add to chart data
                    samaj_data.append({
                        "name": samaj.samaj_name,
                        "families": total_heads,
                        "members": actual_members,
                        "needed": total_expected,
                    })
                    
                    # Process incomplete family heads
                    logger.debug(f"Checking for incomplete family records in Samaj: {samaj.samaj_name}")
                    for head in family_heads:
                        expected = head.family.total_family_members
                        entered = Member.objects.filter(family_head=head).count()
                        with_head = entered + 1
                        missing = expected - with_head
                        
                        if missing > 0:
                            logger.debug(f"Incomplete family found: {head.name_of_head}, Missing: {missing} members")
                            incomplete_heads.append({
                                "samaj": samaj.samaj_name,
                                "head": head.name_of_head,
                                "phone": head.phone_no,
                                "expected": expected,
                                "entered": with_head,
                                "missing": missing
                            })
                
                except Exception as e:
                    logger.error(f"Error processing Samaj {samaj.samaj_name}: {str(e)}", exc_info=True)
            
            execution_time = time.time() - start_time
            logger.info(f"Dashboard data API completed in {execution_time:.2f} seconds")
            logger.info(f"Returning {len(samaj_data)} samaj records and {len(incomplete_heads)} incomplete family records")
            
            return Response({
                "chart_data": samaj_data,
                "incomplete_heads": incomplete_heads,
            })
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}", exc_info=True)
            return Response({
                "error": "An error occurred while generating dashboard data",
                "detail": str(e)
            }, status=500)




class DashbordSamajAPIView(APIView):
    def get(self, request):
        total_samaj = Samaj.objects.count()

        # Stats for each Samaj
        stats = []

        for samaj in Samaj.objects.all():
            families = Family.objects.filter(samaj=samaj)
            family_ids = families.values_list('id', flat=True)

            family_heads_count = FamilyHead.objects.filter(family__in=family_ids).count()
            families_count=family_heads_count
            members_count = Member.objects.filter(family_head__family__in=family_ids).count()

            stats.append({
                'samaj_name': samaj.samaj_name,
                'total_families': families_count,
                'total_family_heads': family_heads_count,
                'total_members': members_count + family_heads_count,  # include family heads as members
            })

        return Response({
            'total_samaj': total_samaj,
            'samaj_stats': stats
        }, status=200)



























































































































































































































































import requests
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@csrf_exempt  # Only use this if you need to bypass CSRF protection for this view
def send_to_google_sheet(request):
    """
    Send the specified data to Google Sheets via Apps Script
    """
    # Your Google Apps Script URL - this should be the web app URL from your deployed script
    GOOGLE_SHEETS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx-kFLcNx3VLlqiddhWkMQMhIrR_uZ46Z91WftDCVLIPLs1QYcSDkQfqaCCl4_wedNS/exec"
    
    # If this is a POST request, use the form data or request body
    if request.method == 'POST':
        try:
            # Try to get JSON data if sent as application/json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            # Otherwise use POST data
            else:
                data = request.POST.dict()
                
            # If no data was provided, use the test payload
            if not data:
                data = get_test_payload()
        except:
            # If any error occurs, use test payload
            data = get_test_payload()
    else:
        # For GET requests, use the test payload
        data = get_test_payload()
    
    try:
        # Set headers for JSON content
        headers = {'Content-Type': 'application/json'}
        
        # Add timestamp if not already in the data
        if 'created_at' not in data:
            data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Send POST request to the Google Apps Script
        response = requests.post(
            GOOGLE_SHEETS_SCRIPT_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=30  # Set a timeout to avoid hanging requests
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            try:
                result = response.json()
                return JsonResponse(result)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': f"Failed to parse response: {response.text}"
                })
        else:
            # Return error if the request failed
            return JsonResponse({
                'success': False,
                'error': f"HTTP error {response.status_code}: {response.text}"
            })
            
    except requests.exceptions.RequestException as e:
        # Handle requests-specific exceptions with more detail
        return JsonResponse({
            'success': False,
            'error': f"Request error: {str(e)}"
        })
    except Exception as e:
        # Return error for any other exceptions
        return JsonResponse({
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        })
    
    # This fallback should never be reached due to the return statements above
    return render(request, 'dashboard/success.html', {'message': 'Request processed'})

def get_test_payload():
    """Return a test payload with sample data"""
    return {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
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


