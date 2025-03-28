from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Samaj, Family, FamilyHead, Member,Profile,User
from .forms import SamajForm, FamilyForm, FamilyHeadForm, MemberForm
import random
from .mixins import MessageHandler
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned



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
                return redirect('family_list', family_id=family_id)
        else:
            form = FamilyForm()
        return render(request, 'create_family.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('create_family')

# List Family
def family_list(request, family_id=None):
    try:
        family = Family.objects.get(id=family_id)
        
        context = {'family_list': family}
        return render(request, 'family_list.html', context)

    except ObjectDoesNotExist:
        messages.error(request, "Family not found.")
    except MultipleObjectsReturned:
        messages.error(request, "Multiple families found with the same ID.")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


# Update Family
def update_family(request, family_id=None):
    try:
        family = get_object_or_404(Family, pk=family_id)
        if request.method == 'POST':
            form = FamilyForm(request.POST, instance=family)
            if form.is_valid():
                fm = form.save()
                return redirect('family_list', family_id=fm.id)
        else:
            form = FamilyForm(instance=family)
        return render(request, 'create_family.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('create_family')

# Delete Family
def delete_family(request, family_id=None):
    try:
        family = get_object_or_404(Family, pk=family_id)
        family.delete()
        return redirect('create_family')
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the family: {e}")
        return redirect('create_family')

# Create Family Head
def create_familyhead(request, family_id=None):
    try:
        family = get_object_or_404(Family, pk=family_id)
        existing_family_head = FamilyHead.objects.filter(family=family).first()

        if existing_family_head:
            messages.error(request, "A Family Head is already created for this family. You can edit the details if needed.")
            return redirect('familyhead_list', familyhead_id=existing_family_head.id)

        if request.method == "POST":
            form = FamilyHeadForm(request.POST, request.FILES)
            if form.is_valid():
                family_head = form.save(commit=False)
                family_head.family = family
                family_head.save()
                return redirect('familyhead_list', familyhead_id=family_head.id)
        else:
            form = FamilyHeadForm()
        return render(request, 'familyhead_form.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))

# List Family Heads
def familyhead_list(request, familyhead_id=None):
    try:
        familyhead = FamilyHead.objects.get(id=familyhead_id)
        return render(request, 'familyhead_list.html', {'familyhead': familyhead})
    except ObjectDoesNotExist:
        
        messages.error(request, "Family Head not found.")
    except MultipleObjectsReturned:
        
        messages.error(request, "Multiple Family Heads found with the same ID.")
    except Exception as e:
       
        messages.error(request, f"An unexpected error occurred: {e}")

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
                fm = form.save()
                return redirect('familyhead_list', familyhead_id=fm.id)
        else:
            form = FamilyHeadForm(instance=family_head)

        return render(request, 'familyhead_form.html', {'form': form, 'edit_mode': True})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
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
            if form.is_valid():
                member = form.save(commit=False)
                member.family_head = family_head
                member.save()
                
                di['member_count'] += 1
                t=total_members-di['member_count']
                if t!=0:
                    messages.success(request, f"Family member added successfully. Please add {t} more member(s) to complete your family's total count.")
                else:
                    messages.success(request, f"Family member added successfully.")
                return redirect('member_list', familyhead_id=familyhead_id)

                
        else:
            form = MemberForm()

        return render(request, 'member_form.html', {'form': form, 'family_head': family_head})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))

# List Members
def member_list(request, familyhead_id=None):
    try:
        members = Member.objects.filter(family_head__id=familyhead_id)   
        return render(request, 'member_list.html', {'members': members, 'f_id': familyhead_id})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

def update_member(request, member_id):
    try:
        member = get_object_or_404(Member, pk=member_id)
        family_head_id = member.family_head.id  # To redirect correctly after update

        if request.method == "POST":
            form = MemberForm(request.POST, request.FILES, instance=member)
            if form.is_valid():
                form.save()
                messages.success(request, "Member details updated successfully!")
                return redirect('member_list', familyhead_id=family_head_id)
        else:
            form = MemberForm(instance=member)

        return render(request, 'member_form.html', {'form': form, 'edit_mode': True, 'member': member})

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    family_head_id = member.family_head.id
    try:
        member.delete()
        print(f"Member {member_id} deleted successfully")
        return redirect('member_list', familyhead_id=family_head_id)
    except Exception as e:
        print(f"Error deleting member: {e}")
        messages.error(request, f"Error deleting member: {e}")
        return redirect('family_list', family_id=member.family_head.family.id)


def detail_member(request, member_id):
    try:
        member = get_object_or_404(Member, id=member_id)
        return render(request, 'member_detail.html', {'member': member})

    except Http404:
        return render(request, 'error_page.html', {'message': "Member not found!"}, status=404)

    except Exception:
        return render(request, 'error_page.html', {'message': "An unexpected error occurred. Please try again later."}, status=500)