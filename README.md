# Django Family and Samaj Management

## Overview
This **Django-based application** provides functionalities to manage **families, family heads, and members**. Users can create, update, list, and delete families, family heads, and members. The application also integrates with external APIs to fetch location data.

---

## Features 🚀
✅ **CRUD Operations** for Families, Family Heads, and Members  
✅ **Fetch States & Districts** from External APIs  
✅ **Session Management** for seamless user experience  
✅ **Error Handling & Validations**  
✅ **Authentication & User Management**  
✅ **RESTful API Endpoints**  

---



📌 Models
1️⃣ Profile
This model stores additional user profile data for each Django user.

user: One-to-one relation with Django’s built-in User model.

phone_number: A character field to store the user's phone number.

otp: A character field for storing a one-time password (optional).

uuid: A unique UUID field automatically generated on creation.

2️⃣ PersonsData (Abstract Base Model)
This abstract model holds common fields related to personal data. Other models (such as FamilyHead and Member) inherit these fields.

middle_name: Middle name of the person.

last_name: Last name of the person.

birth_date: Date field for the person’s birth date.

age: An integer field with choices ranging from 1 to 120.

gender: A choice field with options like "Male" and "Female".

marital_status: A choice field with options like "Single", "Married", "Divorced", "Widowed", "Widower".

qualification: A character field for educational qualifications.

occupation: A character field for the person’s occupation.

exact_nature_of_duties: A field to describe the nature of duties.

native_place: A character field for the native place (defaults to empty string).

country: A character field for the country (default is "India").

state: A character field for the state.

district: A character field for the district.

city: A character field for the city (default empty).

street_name: A character field for the street name (default empty).

landmark: A character field for a landmark (default empty).

building_name: A character field for the building name (default empty).

door_no: A character field for the door number (default empty).

flat_no: A character field for the flat number (default empty).

pincode: A character field for the postal code (default empty).

landline_no: An optional character field for the landline number.

phone_no: A character field for the phone number.

alternative_no: An optional character field for an alternative phone number.

email_id: An optional email field.

blood_group: A choice field for blood group (e.g., "A+", "O-", etc.).

social_media_link: An optional URL field for a social media link.

photo_upload: An optional image field for uploading a photo (stored in the 'photos/' directory).

Note: This model is marked as abstract, so it won’t create its own database table but provides common fields for child models.

3️⃣ Samaj
This model represents the community or group to which families belong.

samaj_name: A unique name for the community.

created_at: A timestamp automatically set when the record is created.

4️⃣ Family
This model represents a family within a given community.

samaj: A foreign key linking to a Samaj instance.

total_family_members: An integer representing the total number of members in the family.

created_at: A timestamp indicating when the family record was created.

5️⃣ FamilyHead
This model represents the head of a family and inherits personal data from PersonsData.

name_of_head: The name of the family head.

family: A foreign key linking to the Family the head belongs to.

created_at: A timestamp set when the record is created.

Inherits all personal data fields from PersonsData.

6️⃣ Member
This model represents a family member and also inherits from PersonsData.

family_head: A foreign key linking to the FamilyHead.

relation_with_family_head: A choice field indicating the member’s relationship with the family head (options include "son", "daughter", "spouse", "father", "mother", "brother", "sister", "other").

name: A character field for the member's name.

created_at: A timestamp set on record creation.

Also inherits the common personal data fields from PersonsData.

These models together provide a comprehensive structure for managing community data (Samaj), families, and individuals (both heads and other members) along with user profiles. Let me know if you need any further modifications!


---

## 🌐 API Endpoints
### **Family Endpoints**
- `POST /create_family/` → Create a new family
- `GET /family_list/<int:family_id>/` → Get family details
- `PUT /update_family/<int:family_id>/` → Update family details
- `DELETE /delete_family/<int:family_id>/` → Delete a family

### **Family Head Endpoints**
- `POST /create_familyhead/<int:family_id>/` → Create a family head
- `GET /familyhead_list/<int:familyhead_id>/` → Get family head details
- `PUT /update_familyhead/<int:familyhead_id>/` → Update family head details
- `DELETE /delete_familyhead/<int:familyhead_id>/` → Delete a family head

### **Member Endpoints**
- `POST /create_member/<int:familyhead_id>/` → Create a member
- `GET /member_list/<int:familyhead_id>/` → List members under a family head
- `PUT /update_member/<int:member_id>/` → Update member details
- `DELETE /delete_member/<int:member_id>/` → Delete a member
- `GET /detail_member/<int:member_id>/` → Get member details

### **Location Endpoints**
- `GET /get_districts/<int:state_id>/` → Fetch districts based on the selected state

---

## 🌍 External APIs Used
- **Countries Data** → [`https://restcountries.com/v3.1/all`](https://restcountries.com/v3.1/all)
- **States in India** → [`https://cdn-api.co-vin.in/api/v2/admin/location/states`](https://cdn-api.co-vin.in/api/v2/admin/location/states)
- **Districts based on State ID** → [`https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state_id>`](https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state_id>)

---

## ⚠️ Error Handling
✅ **Handles exceptions gracefully** (`ObjectDoesNotExist`, `MultipleObjectsReturned`, etc.)  
✅ **Uses Django Messages Framework** for user notifications  

---

## 🔐 Authentication
✅ Uses Django's **built-in authentication system**  
✅ **Requires login** for certain actions  

---

## 🔄 Session Management
✅ **Stores form data in session** to prevent data loss  
✅ **Deletes session data** upon successful form submission  

---

## 🚀 Deployment Guide
### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2️⃣ Apply Migrations**
```bash
python manage.py migrate
```

### **3️⃣ Run the Server**
```bash
python manage.py runserver
```

---

## 🤝 Contributing
Want to contribute? Follow these steps:
1️⃣ **Fork the repository**  
2️⃣ **Create a new branch**  
3️⃣ **Make changes & test thoroughly**  
4️⃣ **Submit a pull request**  





# 📊 Samaj Data Export System

This project includes a custom Django management command and Celery task to export summary reports related to `Samaj`, `Family`, `FamilyHead`, and `Member` models. It automatically generates daily CSV reports with summary and missing data insights.

---

## 📝 Features

- ✅ Export **Samaj Summary** to a CSV file.
- ✅ Export **Incomplete Family Heads** to a CSV file.
- ✅ Automatically runs every day at **6:00 AM** via Celery Beat.
- ✅ Creates an `exports/` directory and stores dated reports.

---

## 📁 CSV Reports

### 1. `samaj_summary_<YYYY-MM-DD>.csv`

**Location**: `exports/samaj_summary_<date>.csv`

**Description**: Provides summary data per Samaj.

| Column                     | Description                                          |
|---------------------------|------------------------------------------------------|
| Samaj Name                | Name of the Samaj                                     |
| Total Family              | Number of families with a registered head            |
| Total Members             | Head + all members                                    |
| Actual Member Count Needed | Expected number of members based on family data      |
| Missing Member Count      | Difference between expected and actual members       |

Includes a **final row** with grand totals.

---

### 2. `incomplete_members_family_heads_<YYYY-MM-DD>.csv`

**Location**: `exports/incomplete_members_family_heads_<date>.csv`

**Description**: Lists family heads where entered members are fewer than expected.

| Column                 | Description                          |
|------------------------|--------------------------------------|
| Samaj Name             | Name of the Samaj                     |
| Family Head            | Full name of the head of the family  |
| Phone No               | Contact number of the head           |
| Total Members Expected | Value from `total_family_members`    |
| Entered Members        | Actual count (including the head)    |
| Missing Members        | Difference between expected and entered |

---

## ⚙️ Management Command

**Location**: `testapp/management/commands/export_samaj_summary.py`

### ▶️ Usage (Manual Run)

```bash
python manage.py export_samaj_summary
Behavior:

Creates an exports/ directory if not present.

Writes two CSV files.

Outputs success message with file names.

🔁 Celery Task Integration
File: testapp/tasks.py

python
Copy
Edit
@shared_task
def export_samaj_summary():
    call_command('export_samaj_summary')
Wraps the Django management command to be used as an asynchronous task.

⏰ Scheduled Task (Celery Beat)
Configuration:
python
Copy
Edit
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'run-export-samaj-summary-every-morning-6am': {
        'task': 'testapp.tasks.export_samaj_summary',
        'schedule': crontab(hour=6, minute=0),  # Runs daily at 6:00 AM
    },
}
🕕 This ensures the export runs automatically every morning.

🧪 Testing
Manual Command Test
bash
Copy
Edit
python manage.py export_samaj_summary
Manual Task Test via Django Shell
python
Copy
Edit
from testapp.tasks import export_samaj_summary
export_samaj_summary.delay()
✅ Requirements
Django models:

Samaj, Family, FamilyHead, Member

Celery configured and running

Celery Beat configured

Redis or another message broker

exports/ folder will be created automatically

📂 Output Folder Structure
bash
Copy
Edit
/exports/
├── samaj_summary_2025-04-25.csv
└── incomplete_members_family_heads_2025-04-25.csv

📌 **Happy Coding!** 🚀

