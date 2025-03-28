from django import forms
from .models import Samaj, Family, FamilyHead, Member

class SamajForm(forms.ModelForm):
    class Meta:
        model = Samaj
        fields = ['samaj_name']

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['samaj', 'surname', 'total_family_members']
        labels = {
            'surname': 'Family Name',  
        }

    def clean_total_family_members(self):
        total = self.cleaned_data.get('total_family_members')
        if total is None or total <= 0:
            raise forms.ValidationError("Total family members must be greater than zero.")
        return total
        

class FamilyHeadForm(forms.ModelForm):
    email_id = forms.EmailField(required=False)
    class Meta:
        model = FamilyHead
        fields = fields = [
            # Basic Details
            "name_of_head",
            "age",
            "birth_date",
            "gender",
            "marital_status",
            
            # Contact Details
            "phone_no",
            "alternative_no",
            "landline_no",
            "email_id",
            
            
            # Address
            "state",
            "district",
            "permanent_address",
            
            # Professional Details
            "qualification",
            "occupation",
            "exact_nature_of_duties",
            
            # Family & Other Information
            
            "blood_group",
            "social_media_link",
            "photo_upload",
            
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "permanent_address": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            'name_of_head': 'Full Name',  # Change label here
            'photo_upload': 'Upload photo'
        }


    def clean_phone_no(self):
        phone = self.cleaned_data.get('phone_no')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Phone number must be numeric and exactly of 10 digits.")
        return phone

    def clean_alternative_no(self):
        alternative = self.cleaned_data.get('alternative_no')
        # Allow alternative number to be empty; if provided, validate it.
        if alternative:
            if not alternative.isdigit() or len(alternative) != 10:
                raise forms.ValidationError("Alternative number must be numeric and exactly of 10 digits.")
        return alternative


class MemberForm(forms.ModelForm):
    email_id = forms.EmailField(required=False)
    class Meta:
        model = Member
        fields = [
            # Personal Details
            "name",
            "age",
            "birth_date",
            "gender",
            "marital_status",
            "relation_with_family_head",
            
            # Contact Details
            "phone_no",
            "email_id",
            "alternative_no",
            "landline_no",
            
            # Address Details
            "state",
            "district",
            "permanent_address",
            
            # Professional Details
            "qualification",
            "occupation",
            "exact_nature_of_duties",
            
            # Medical Details
            "blood_group",
            "social_media_link",
            "photo_upload",
            
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "permanent_address": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            'name': 'Full Name',  # Change label here
            'photo_upload': 'Upload photo'
        }
    def clean_phone_no(self):
        phone = self.cleaned_data.get('phone_no')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Phone number must be numeric and exactly of 10 digits.")
        return phone

    def clean_alternative_no(self):
        alternative = self.cleaned_data.get('alternative_no')
        # Allow alternative number to be empty; if provided, validate it.
        if alternative:
            if not alternative.isdigit() or len(alternative) != 10:
                raise forms.ValidationError("Alternative number must be numeric and exactly of 10 digits.")
        return alternative
