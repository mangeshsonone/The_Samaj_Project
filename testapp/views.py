from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404,JsonResponse
from .models import Samaj, Family, FamilyHead, Member,Profile,User
from .forms import SamajForm, FamilyForm, FamilyHeadForm, MemberForm
import random
from .mixins import MessageHandler
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import requests
import logging
from django.utils import timezone
# from .google_sheet_data import adddata
# from .main import a
# from .google_sheet_data2 import a


# Define logging for this module
logger = logging.getLogger(__name__)





COUNTRIES_API_URL="https://restcountries.com/v3.1/all"
INDIA_API_URL = "https://api.countrystatecity.in/v1/states"
DISTRICT_API_URL = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"


#############################################aws otp

import hmac
import hashlib
import base64
import boto3
from django.shortcuts import render, redirect
from django.contrib import messages
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Cognito credentials directly in the view
AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')
AWS_COGNITO_CLIENT_SECRET = os.environ.get('AWS_COGNITO_CLIENT_SECRET')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')

# AWS Credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# Initialize the Cognito client directly with AWS credentials (NOT RECOMMENDED for production)
cognito_client = boto3.client(
    'cognito-idp',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def create_user_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email', 'dummy@example.com')
        name = request.POST.get('name', 'Anonymous')

        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number

        try:
            cognito_client.admin_create_user(
                UserPoolId=AWS_COGNITO_USER_POOL_ID,
                Username=phone_number,
                UserAttributes=[
                    {'Name': 'phone_number', 'Value': phone_number},
                    {'Name': 'phone_number_verified', 'Value': 'true'},
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'name', 'Value': name}
                ],
                MessageAction='SUPPRESS'
            )

            # ✅ Set a permanent dummy password (won’t be used in OTP auth)
            cognito_client.admin_set_user_password(
                UserPoolId=AWS_COGNITO_USER_POOL_ID,
                Username=phone_number,
                Password='TempSecurePass123!',  # This won't be used
                Permanent=True
            )

            # ✅ Confirm the user manually (needed if suppressing email/SMS)
            cognito_client.admin_confirm_sign_up(
                UserPoolId=AWS_COGNITO_USER_POOL_ID,
                Username=phone_number
            )

            messages.success(request, "User created successfully.")
            return redirect('login')
        except cognito_client.exceptions.UsernameExistsException:
            messages.info(request, "User already exists.")
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')

    return render(request, 'register.html')




def calculate_secret_hash(username):
    message = username + AWS_COGNITO_CLIENT_ID
    dig = hmac.new(
        str(AWS_COGNITO_CLIENT_SECRET).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def login_view(request):
    """
    View function to handle user login via Cognito Custom Auth flow
    """
    logger.info("Login view accessed")
    
    if request.method == 'POST':
        logger.debug("Processing POST request for login")
        phone_number = request.POST.get('phone_number')
        logger.info(f"Login attempt for phone number: {phone_number}")
        
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number  # Default to Indian numbers
            logger.debug(f"Added country code to phone number: {phone_number}")

        # First attempt to check if user exists
        try:
            user = cognito_client.admin_get_user(
                UserPoolId=AWS_COGNITO_USER_POOL_ID,
                Username=phone_number
            )
            logger.info(f"User found in Cognito: {phone_number}")
            logger.debug(f"User status: {user['UserStatus']}, Enabled: {user['Enabled']}")
            
            # Check if user is enabled
            if not user.get('Enabled', True):
                logger.warning(f"Disabled user attempted login: {phone_number}")
                messages.error(request, "This account has been disabled. Please contact support.")
                return render(request, 'login.html')
                
        except cognito_client.exceptions.UserNotFoundException:
            logger.warning(f"User not found in Cognito: {phone_number}")
            messages.error(request, "User does not exist in Cognito.")
            return render(request, 'login.html')
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}", exc_info=True)
            messages.error(request, f"Error validating user: {str(e)}")
            return render(request, 'login.html')

        # Generate secret hash
        try:
            secret_hash = calculate_secret_hash(phone_number)
            logger.debug("Secret hash generated successfully")
        except Exception as e:
            logger.error(f"Failed to calculate secret hash: {str(e)}", exc_info=True)
            messages.error(request, "Authentication error. Please try again.")
            return render(request, 'login.html')

        # Initiate auth flow
        try:
            logger.info(f"Initiating CUSTOM_AUTH flow for: {phone_number}")
            response = cognito_client.initiate_auth(
                ClientId=AWS_COGNITO_CLIENT_ID,
                AuthFlow='CUSTOM_AUTH',
                AuthParameters={
                    'USERNAME': phone_number,
                    'SECRET_HASH': secret_hash,
                }
            )
            
            logger.info(f"Authentication initiated successfully for: {phone_number}")
            
            # Store session information
            request.session['cognito_session'] = {
                'username': phone_number,
                'session': response['Session'],
            }
            logger.debug("Session information stored in request.session")
            
            return redirect('verify_otp')
            
        except cognito_client.exceptions.UserNotFoundException:
            logger.warning(f"User not found during auth: {phone_number}")
            messages.error(request, "User does not exist.")
            
        except cognito_client.exceptions.NotAuthorizedException as e:
            logger.warning(f"Not authorized: {str(e)}")
            messages.error(request, "Invalid credentials. Please try again.")
            
        except cognito_client.exceptions.UserNotConfirmedException:
            logger.warning(f"User not confirmed: {phone_number}")
            messages.error(request, "Account not confirmed. Please complete registration.")
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            messages.error(request, f"Login error: {str(e)}")

    logger.debug("Rendering login template")
    return render(request, 'login.html')


def verify_otp_view(request):
    """
    View function to handle OTP verification for Cognito Custom Auth flow
    """
    logger.info("OTP verification view accessed")
    
    if request.method == 'POST':
        logger.debug("Processing POST request for OTP verification")
        otp = request.POST.get('otp')
        logger.debug(f"OTP received of length: {len(otp) if otp else 0}")
        
        cognito_session = request.session.get('cognito_session')
        
        if not cognito_session:
            logger.warning("OTP verification attempted with expired session")
            messages.error(request, "Session expired. Try login again.")
            return redirect('login')
        
        username = cognito_session.get('username')
        logger.info(f"Verifying OTP for user: {username}")
        
        try:
            # Calculate the SECRET_HASH
            logger.debug("Calculating secret hash for OTP verification")
            secret_hash = calculate_secret_hash(username)
            
            # Verify the OTP with Cognito
            logger.info(f"Sending OTP verification request to Cognito for user: {username}")
            response = cognito_client.respond_to_auth_challenge(
                ClientId=AWS_COGNITO_CLIENT_ID,
                ChallengeName='CUSTOM_CHALLENGE',
                Session=cognito_session['session'],
                ChallengeResponses={
                    'USERNAME': username,
                    'ANSWER': otp,
                    'SECRET_HASH': secret_hash
                }
            )
            
            # Check response for authentication result
            if 'AuthenticationResult' in response:
                logger.info(f"OTP verification successful for user: {username}")
                
                # Extract tokens
                id_token = response['AuthenticationResult']['IdToken']
                access_token = response['AuthenticationResult']['AccessToken']
                logger.debug("Authentication tokens received successfully")
                
                # Store tokens in session
                request.session['id_token'] = id_token
                request.session['access_token'] = access_token
                logger.debug("Authentication tokens stored in session")
                
                logger.info(f"User {username} successfully authenticated, redirecting to create_family")
                return redirect('create_family')
            else:
                # This case handles when Cognito requires additional challenges
                logger.warning(f"Additional challenge required for user: {username}")
                challenge_name = response.get('ChallengeName')
                logger.debug(f"Next challenge: {challenge_name}")
                messages.warning(request, f"Additional verification required: {challenge_name}")
                return redirect('verify_otp')
                
        except cognito_client.exceptions.CodeMismatchException:
            logger.warning(f"Invalid OTP provided for user: {username}")
            messages.error(request, "Invalid verification code. Please try again.")
            
        except cognito_client.exceptions.ExpiredCodeException:
            logger.warning(f"Expired OTP code for user: {username}")
            messages.error(request, "Verification code has expired. Please request a new one.")
            
        except cognito_client.exceptions.NotAuthorizedException as e:
            logger.warning(f"Not authorized during OTP verification: {str(e)}")
            messages.error(request, "Authentication failed. Please try again.")
            
        except cognito_client.exceptions.TooManyRequestsException:
            logger.warning(f"Too many OTP verification attempts for user: {username}")
            messages.error(request, "Too many attempts. Please try again later.")
            
        except Exception as e:
            logger.error(f"OTP verification error for user {username}: {str(e)}", exc_info=True)
            messages.error(request, f"Verification error: {str(e)}")
            
        # If we reached here, verification failed
        return redirect('verify_otp')
    
    logger.debug("Rendering OTP verification template")
    return render(request, 'otp.html')


#############################################aws otp




def create_family(request):
    try:
        if request.method == 'POST':
            form = FamilyForm(request.POST)
            if form.is_valid():
                fm = form.save()
                family_id = fm.id
                logger.info("Family created with id: %s", family_id)
                return redirect('family_list', family_id=family_id)
        else:
            # adddata()
            form = FamilyForm()
        return render(request, 'create_family.html', {'form': form})
    except Exception as e:
        # messages.error(request, f"An error occurred: {e}")
        logger.exception("Error in create_family: %s", e)
        return redirect('create_family')

# List Family
def family_list(request, family_id=None):
    try:
        family = Family.objects.get(id=family_id)
        context = {'family_list': family}

        logger.info("Displaying family list for family id: %s", family_id)
        return render(request, 'family_list.html', context)

    except ObjectDoesNotExist:
        logger.error("Family not found: id %s", family_id)
    except MultipleObjectsReturned:
        logger.error("Multiple families returned for id %s", family_id)
    except Exception as e:
        logger.exception("Unexpected error in family_list: %s", e)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# Update Family
def update_family(request, family_id=None):
    try:
        family = get_object_or_404(Family, pk=family_id)
        if request.method == 'POST':
            form = FamilyForm(request.POST, instance=family)
            if form.is_valid():
                fm = form.save()
                logger.info("Family updated: id %s", fm.id)
                return redirect('family_list', family_id=fm.id)
        else:
            form = FamilyForm(instance=family)
        return render(request, 'create_family.html', {'form': form})
    except Exception as e:
        logger.exception("Error in update_family: %s", e)
        return redirect('create_family')

# Delete Family
def delete_family(request, family_id=None):
    try:
        family = get_object_or_404(Family, pk=family_id)
        family.delete()
        logger.info("Family deleted: id %s", family_id)
        return redirect('create_family')
    except Exception as e:
        logger.exception("Error deleting family id %s: %s", family_id, e)
        return redirect('create_family')
    
def get_districts(request, state_id):
    """Fetch districts based on the selected state."""
    try:
        response = requests.get(f"{DISTRICT_API_URL}{state_id}")
        if response.status_code == 200:
            data = response.json()
            districts = [{"id": dist["district_id"], "name": dist["district_name"]} for dist in data["districts"]]
            logger.info("Districts fetched for state_id %s", state_id)
            return JsonResponse({"districts": districts})  # Ensure full district list is sent
    except Exception as e:
        logger.exception("Error fetching districts for state_id %s: %s", state_id, e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Failed to fetch districts"}, status=500)



# Create Family Head
def create_familyhead(request, family_id=None):
    try:
        print("entering in family head")
        family = get_object_or_404(Family, pk=family_id)
        existing_family_head = FamilyHead.objects.filter(family=family).first()

        if existing_family_head:
            logger.warning("FamilyHead already exists for family id: %s", family_id)
            messages.error(request, "A Family Head is created for this family. You can edit the details if needed.")
            return redirect('familyhead_list', familyhead_id=existing_family_head.id)

        if request.method == "POST":
            form = FamilyHeadForm(request.POST, request.FILES)
            if form.is_valid():
                family_head = form.save(commit=False)
                family_head.family = family
                family_head.save()
                logger.info("FamilyHead created with id: %s", family_head.id)
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
                    del request.session[ip]  # Deletes only form_dat
                    request.session.modified = True # Ensure session updates
                    logger.info("Deleted session data for IP: %s", ip)

                else:
                    ip = request.META.get("REMOTE_ADDR", "unknown")
                    logger.info("No session data found for IP: %s", ip)
                    logger.debug("Session after deletion: %s", dict(request.session))
                return redirect('familyhead_list', familyhead_id=family_head.id)
        else:
            print("entering in else")
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
            else:
                ip = request.META.get("REMOTE_ADDR", "unknown")
            logger.info("Using IP for session retrieval: %s", ip)
            saved_data = request.session.get(ip, {})
            form = FamilyHeadForm(initial=saved_data)  
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Origin": "https://cdn-api.co-vin.in",
                "Referer": "https://cdn-api.co-vin.in",
            }
            response = requests.get(INDIA_API_URL, headers=headers)
            if response.status_code == 200:
                states = response.json().get("states", [])
                logger.info("Fetched states from INDIA_API_URL")
            else:
                states = []
                logger.error("Failed to fetch states from INDIA_API_URL, status: %s", response.status_code)
        logger.info("Rendering familyhead_form.html")
        return render(request, 'familyhead_form.html', {'form': form,'states': states})
    except Exception as e:
        logger.exception("Error in create_familyhead: %s", e)
        return redirect(request.META.get('HTTP_REFERER', '/'))

            
# List Family Heads
def familyhead_list(request, familyhead_id=None):
    try:
        familyhead = FamilyHead.objects.get(id=familyhead_id)
        return render(request, 'familyhead_list.html', {'familyhead': familyhead})
    except ObjectDoesNotExist:
        
        # messages.error(request, "Family Head not found.")
        pass
    except MultipleObjectsReturned:
        
        # messages.error(request, "Multiple Family Heads found with the same ID.")
        pass
    except Exception as e:
       
        # messages.error(request, f"An unexpected error occurred: {e}")
        pass

    return redirect(request.META.get('HTTP_REFERER', '/'))


def familyhead_template(request, familyhead_id=None):
    try:
        familyhead = FamilyHead.objects.get(id=familyhead_id)
        return render(request, 'familyhead_template.html', {'familyhead': familyhead})
    except ObjectDoesNotExist:
        
        messages.error(request, "Family Head not found.")
    except MultipleObjectsReturned:
        
        messages.error(request, "Multiple Family Heads found with the same ID.")
    except Exception as e:
       
        messages.error(request, f"An unexpected error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))

# Update Family Head
def update_familyhead(request, familyhead_id):
    try:
        family_head = get_object_or_404(FamilyHead, pk=familyhead_id)
        if request.method == "POST":
            form = FamilyHeadForm(request.POST, request.FILES, instance=family_head)
            if form.is_valid():
                fm = form.save(commit=False)
                fm.updated_at = timezone.now()  # Set updated_at to the current date/time
                fm.save()
                return redirect('familyhead_list', familyhead_id=fm.id)
        else:
            form = FamilyHeadForm(instance=family_head)
            response = requests.get(INDIA_API_URL)
            states = response.json().get("states", []) if response.status_code == 200 else []

        return render(request, 'familyhead_form.html', {'form': form, 'edit_mode': True,'states': states})
    except Exception as e:
        # messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))

# Delete Family Head
def delete_familyhead(request, familyhead_id):
    
    # family_head = get_object_or_404(FamilyHead, pk=familyhead_id)

    # try:
    #     family_id = family_head.family.id  # Get family ID before deleting
    #     family_head.delete()
    #     messages.success(request, "Family Head deleted successfully!")

    #     return redirect('family_list', family_id=family_id)  # Redirect to family list instead of familyhead_list

    # except Exception as e:
    #     messages.error(request, f"An error occurred: {e}")
    #     return redirect('family_list', family_id=family_id)
    return redirect('familyhead_list', familyhead_id=familyhead_id)


di = {}

# Create Member
def create_member(request, familyhead_id=None):
    try:
        family_head = get_object_or_404(FamilyHead, pk=familyhead_id)
        total_members = family_head.family.total_family_members-1


        existing_members_count = Member.objects.filter(family_head=family_head).count()
        
        print('existing_members_count',existing_members_count, "...", total_members)

        if total_members == 0:
            messages.error(
                request, 
                "You have already added all family members. If you need to add more,go back to Family Details and edit the total members in your family."
            )
            print("hellloooo")
            return redirect('familyhead_list', familyhead_id=familyhead_id)

        if existing_members_count >= total_members:
            messages.error(
                request, 
                "You have already added all family members. If you need to add more,go back to Family Details and edit the total members in your family."
            )
            return redirect('member_list', familyhead_id=familyhead_id)

        if existing_members_count ==0:
            di['member_count'] = 0  
        else:
            di['member_count']=existing_members_count

        member_count = di['member_count']
        print('(member_count',member_count,"...",total_members)


        if request.method == "POST":
            form = MemberForm(request.POST, request.FILES)
            print('user in post request')
            if form.is_valid():
                print('user in post request and form is valid')
                member = form.save(commit=False)
                member.family_head = family_head
                member.save()
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
                del request.session[ip]  # Deletes only form_data
                request.session.modified = True
                print("Session After Deletion:", dict(request.session))
                
                di['member_count'] += 1
                t=total_members-di['member_count']
                if t!=0:
                    messages.success(request, f"Family member added successfully. Please add {t} more member(s) to complete your family's total count.")
                else:
                    messages.success(request, f"All Family members are added successfully.")
                return redirect('member_list', familyhead_id=familyhead_id)

                
        else:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
            else:
                ip = request.META.get("REMOTE_ADDR", "unknown")
            saved_data = request.session.get(ip, {})  
            form = MemberForm(initial=saved_data)
            response = requests.get(INDIA_API_URL)
            states = response.json().get("states", []) if response.status_code == 200 else []
            # ,'states': states

        return render(request, 'member_form.html', {'form': form, 'family_head': family_head,'states': states})
    except Exception as e:
        # messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
        

# List Members
def member_list(request, familyhead_id=None):
    try:
        members = Member.objects.filter(family_head__id=familyhead_id)   
        return render(request, 'member_list.html', {'members': members, 'f_id': familyhead_id})
    except Exception as e:
        # messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

def update_member(request, member_id):
    try:
        member = get_object_or_404(Member, pk=member_id)
        family_head_id = member.family_head.id  # To redirect correctly after update

        if request.method == "POST":
            form = MemberForm(request.POST, request.FILES, instance=member)
            if form.is_valid():
                form.save()
                fm = form.save(commit=False)
                fm.updated_at = timezone.now()  # Set updated_at to the current date/time
                fm.save()
                messages.success(request, "Member details updated successfully!")
                return redirect('member_list', familyhead_id=family_head_id)
        else:
            form = MemberForm(instance=member)
            response = requests.get(INDIA_API_URL)
            states = response.json().get("states", []) if response.status_code == 200 else []

        return render(request, 'member_form.html', {'form': form, 'edit_mode': True, 'member': member,'states': states})

    except Exception as e:
        # messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

def delete_member(request, member_id):
    try:
        # Try to get the member
        member = get_object_or_404(Member, id=member_id)
        family_head = member.family_head  # Get related family head
        family_id = family_head.family.id  # Get family ID

        # Delete the member
        member.delete()

        # Check if there are any remaining members in this family
        remaining_members = Member.objects.filter(family_head=family_head)

        if not remaining_members.exists():  # If no members left, redirect to familyhead_list
            messages.info(request, "All members have been deleted. Redirecting to family head list.")
            return redirect('familyhead_list', familyhead_id=family_head.id)

        # Otherwise, redirect back to the member list
        messages.success(request, "Member deleted successfully. You can add a new Member.")
        return redirect('member_list', familyhead_id=family_head.id)

    except Member.DoesNotExist:
        messages.error(request, "Member not found.")
        return redirect('familyhead_list', familyhead_id=family_head.id)

    except FamilyHead.DoesNotExist:
        messages.error(request, "Family Head not found.")
        return redirect('familyhead_list', familyhead_id=family_head.id)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")



def detail_member(request, member_id):
    try:
        member = get_object_or_404(Member, id=member_id)
        return render(request, 'member_detail.html', {'member': member})

    except Http404:
        return render(request, 'error_page.html', {'message': "Member not found!"}, status=404)

    except Exception:
        return render(request, 'error_page.html', {'message': "An unexpected error occurred. Please try again later."}, status=500)
    

# def custom_404_view(request, exception):
#     messages.warning(request, "The page you requested was not found. Redirecting you back.")
#     return redirect(request.META.get('HTTP_REFERER', '/'))

def custom_404(request, exception):
    return redirect(request.META.get('HTTP_REFERER', '/'))



def save_form_data(request):
    if request.method == "POST":
        # Retrieve the client's IP address
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
       

        # Store form data in the session
        request.session[ip] = request.POST.dict()
        request.session.modified = True  # Ensure session updates
        
        return JsonResponse({"message": "Form data saved successfully", "ip": ip}, status=200)
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def save_form_view(request):
    saved_data = {key: request.session.get(key, "") for key in FamilyHeadForm().fields.keys()}
    form = FamilyHeadForm(initial=saved_data)  # Load saved data
    return render(request, "familyhead_form.html", {"form": form})

from datetime import datetime
from django.db.models import Sum
def samaj_dashboard(request):
    today_str = datetime.now().strftime('%Y-%m-%d')

    chart_data = []
    incomplete_heads = []

    samajs = Samaj.objects.all()

    for samaj in samajs:
        families = Family.objects.filter(samaj=samaj)
        family_ids_with_heads = FamilyHead.objects.filter(family__in=families).values_list('family_id', flat=True).distinct()
        valid_families = families.filter(id__in=family_ids_with_heads)

        family_heads = FamilyHead.objects.filter(family__in=valid_families)
        members = Member.objects.filter(family_head__in=family_heads)

        total_heads = family_heads.count()
        total_expected = valid_families.aggregate(total=Sum('total_family_members'))['total'] or 0
        actual_entries = total_heads + members.count()

        # For chart
        chart_data.append({
            'name': samaj.samaj_name,
            'families': total_heads,
            'members': actual_entries,
            'needed': total_expected
        })

        # For incomplete family head list
        for head in family_heads:
            expected_total = head.family.total_family_members
            entered_members = Member.objects.filter(family_head=head).count()
            total_with_head = entered_members + 1
            missing = expected_total - total_with_head

            if missing > 0:
                incomplete_heads.append({
                    'samaj': samaj.samaj_name,
                    'head': f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
                    'phone': head.phone_no,
                    'expected': expected_total,
                    'entered': total_with_head,
                    'missing': missing
                })

    context = {
        'today': today_str,
        'chart_data': chart_data,
        'incomplete_heads': incomplete_heads
    }
    return render(request, 'dashboard.html', context)
