from django.db import models
from django.contrib.auth.models import User
import uuid






class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    phone_number=models.CharField(max_length=100)
    otp=models.CharField(max_length=100,null=True,blank=True)
    uuid=models.UUIDField(default=uuid.uuid4,unique=True)



class PersonsData(models.Model):
    AGE_CHOICES = [(i, str(i)) for i in range(1, 121)]  # Age choices from 1 to 120
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        
    ]
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
        ('Widower','Widower'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]


    middle_name = models.CharField(max_length=100,blank=True, null=True,default="")
    last_name = models.CharField(max_length=100,default="")
    birth_date = models.DateField()
    age = models.IntegerField(choices=AGE_CHOICES)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=100, choices=MARITAL_STATUS_CHOICES)
    qualification = models.CharField(max_length=100,blank=True, null=True)
    occupation = models.CharField(max_length=100,blank=True, null=True) 
    exact_nature_of_duties = models.CharField(max_length=1000,blank=True, null=True)
    native_city = models.CharField(max_length=100,default="")
    native_state = models.CharField(max_length=100,default="")
    country = models.CharField(max_length=100,default="India")
    state = models.CharField(max_length=100) 
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100,default="")
    street_name = models.CharField(max_length=100,default="")
    landmark = models.CharField(max_length=100,default="")
    building_name = models.CharField(max_length=100,default="")
    door_no = models.CharField(max_length=100,default="")
    flat_no = models.CharField(max_length=100,default="")
    pincode = models.CharField(max_length=100,default="")
    landline_no = models.CharField(max_length=15, blank=True, null=True)
    phone_no = models.CharField(max_length=15)
    alternative_no = models.CharField(max_length=15, blank=True, null=True)
    email_id = models.EmailField(null=True,blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    social_media_link= models.URLField(
        max_length=255,  # Optional: Ensures no duplicate LinkedIn URLs
        blank=True,    # Optional: Allows the field to be empty
        null=True,     # Optional: Stores NULL in the database if not provided
    )
    photo_upload = models.ImageField(upload_to='photos/',null=True,blank=True)
    

    class Meta:
        abstract = True  

class Samaj(models.Model):
    samaj_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.samaj_name

class Family(models.Model):
    
    samaj = models.ForeignKey(Samaj, on_delete=models.CASCADE)
    total_family_members = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"family {self.id}"

class FamilyHead(PersonsData):
    name_of_head = models.CharField(max_length=255)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_of_head

class Member(PersonsData):
    RELATION_CHOICES = [
    ('husband','Husband'),
    ('wife','Wife'),
    ('son', 'Son'),
    ('daughter', 'Daughter'),
    ('father', 'Father'),
    ('mother', 'Mother'),
    ('brother', 'Brother'),
    ('sister', 'Sister'),
    ('son-in-law','Son-in-law'),
    ('daughter-in-law','Daughter-in-law'),
    ('grandson','Grandson'),
    ('granddaughter','Granddaughter'),
    ('great Grandson','great Grandson'),
    ('great granddaughter','Great Granddaughter'),
    ('father-in-law','Father-in-law'),
    ('mother-in-law','Mother-in-law'),

]



    family_head = models.ForeignKey(FamilyHead, on_delete=models.PROTECT)
    relation_with_family_head = models.CharField(max_length=255, choices=RELATION_CHOICES)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name