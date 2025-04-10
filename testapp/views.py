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


# Define logging for this module
logger = logging.getLogger(__name__)





COUNTRIES_API_URL="https://restcountries.com/v3.1/all"
INDIA_API_URL = "https://api.countrystatecity.in/v1/states"
DISTRICT_API_URL = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         phone_number = request.POST.get('phone_number')

#         # Check if a profile exists with the given username and phone number
#         profile = Profile.objects.filter(user__username=username, phone_number=phone_number)

        
#         if not profile.exists():
#             return redirect('/register_view/')

#         profile = profile.first()
#         profile.otp = random.randint(1000, 9999)
#         profile.save()
        
#         # Send OTP via Twilio
#         message_handler = MessageHandler(phone_number, profile.otp)
#         message_handler.send_otp_on_phone()
        
#         return redirect(f'/otp_view/{profile.uuid}')

#     return render(request, 'login.html')


# def register_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         phone_number = request.POST.get('phone_number')

#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists. Please choose another one.")
#             return redirect('/')  # Redirect back to registration page

#         user = User.objects.create(username=username)
#         Profile.objects.create(user=user, phone_number=phone_number)

#         return redirect('/login_view/')

#     return render(request, 'register.html')
    
# def otp_view(request, uid):
#     profile = get_object_or_404(Profile, uuid=uid)
    
#     if request.method == 'POST':
#         otp = request.POST.get('otp')
        

#         if otp == profile.otp:
#             login(request, profile.user)
#             return redirect('/create_family/')  # Redirect to home or dashboard

#     return render(request, 'otp.html', {'profile': profile})

# def logout_view(request):
#     logout(request)
#     return redirect('/login_view/')



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
