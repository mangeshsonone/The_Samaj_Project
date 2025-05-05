from rest_framework import serializers
from testapp.models import FamilyHead, Member, Family, Samaj

class SamajSerializer(serializers.ModelSerializer):
    class Meta:
        model = Samaj
        fields = ['id', 'samaj_name', 'created_at']

class FamilySerializer(serializers.ModelSerializer):
    samaj = SamajSerializer(read_only=True)
    
    class Meta:
        model = Family
        fields = ['id', 'samaj', 'total_family_members', 'created_at']

class FamilyHeadSerializer(serializers.ModelSerializer):
    family = FamilySerializer(read_only=True)
    
    class Meta:
        model = FamilyHead
        fields = [
            'id', 'name_of_head', 'middle_name', 'last_name', 'birth_date', 
            'age', 'gender', 'marital_status', 'qualification', 'occupation',
            'exact_nature_of_duties', 'native_city', 'native_state', 'country',
            'state', 'district', 'city', 'street_name', 'landmark', 'building_name',
            'door_no', 'flat_no', 'pincode', 'landline_no', 'phone_no',
            'alternative_no', 'email_id', 'blood_group', 'social_media_link',
            'photo_upload', 'family', 'created_at', 'updated_at'
        ]

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'id', 'name', 'middle_name', 'last_name', 'birth_date', 
            'age', 'gender', 'marital_status', 'qualification', 'occupation',
            'exact_nature_of_duties', 'native_city', 'native_state', 'country',
            'state', 'district', 'city', 'street_name', 'landmark', 'building_name',
            'door_no', 'flat_no', 'pincode', 'landline_no', 'phone_no',
            'alternative_no', 'email_id', 'blood_group', 'social_media_link',
            'photo_upload', 'relation_with_family_head', 'created_at', 'updated_at'
        ]