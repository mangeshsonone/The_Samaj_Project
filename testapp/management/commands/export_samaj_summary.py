import csv
import os
from itertools import chain
from operator import attrgetter
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member


class Command(BaseCommand):
    help = 'Export Samaj summary, incomplete family heads, and all family heads/members to CSV files'

    def handle(self, *args, **kwargs):
        output_dir = 'exports'
        os.makedirs(output_dir, exist_ok=True)

        today_str = datetime.now().strftime('%Y-%m-%d')

        samajs = Samaj.objects.all()

        # === File 1: Samaj Summary CSV ===
        summary_filename = f"samaj_summary_{today_str}.csv"
        summary_path = os.path.join(output_dir, summary_filename)

        if os.path.exists(summary_path):
            os.remove(summary_path)

        with open(summary_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"Samaj Summary Report - {today_str}"])
            writer.writerow([])
            writer.writerow(['Samaj Name', 'Total Family', 'Total Members Entered', 'Actual Member Count Needed', 'Missing Member Count'])

            grand_total_heads = 0
            grand_actual_members = 0
            grand_expected_members = 0
            grand_remaining = 0

            for samaj in samajs:
                families = Family.objects.filter(samaj=samaj)
                family_ids_with_heads = FamilyHead.objects.filter(family__in=families).values_list('family_id', flat=True).distinct()
                valid_families = families.filter(id__in=family_ids_with_heads)

                family_heads = FamilyHead.objects.filter(family__in=valid_families)
                members = Member.objects.filter(family_head__in=family_heads)

                total_heads = family_heads.count()
                total_expected = valid_families.aggregate(total=Sum('total_family_members'))['total'] or 0
                actual_entries = total_heads + members.count()
                remaining = total_expected - actual_entries

                writer.writerow([
                    samaj.samaj_name,
                    total_heads,
                    actual_entries,
                    total_expected,
                    remaining
                ])

                grand_total_heads += total_heads
                grand_actual_members += actual_entries
                grand_expected_members += total_expected
                grand_remaining += remaining

            writer.writerow([])
            writer.writerow([
                'Total',
                grand_total_heads,
                grand_actual_members,
                grand_expected_members,
                grand_remaining
            ])

        # === File 2: Incomplete Family Heads CSV ===
        incomplete_filename = f"incomplete_members_family_heads_{today_str}.csv"
        incomplete_path = os.path.join(output_dir, incomplete_filename)

        if os.path.exists(incomplete_path):
            os.remove(incomplete_path)

        with open(incomplete_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"Family Heads with Missing Members - {today_str}"])
            writer.writerow([])
            writer.writerow(['Samaj Name', 'Family Head', 'Phone No', 'Total Members Entered', 'Actual Member Count Needed', 'Missing Member Count'])

            total_entered_all = 0
            total_expected_all = 0
            total_missing_all = 0

            for samaj in samajs:
                families = Family.objects.filter(samaj=samaj)
                family_heads = FamilyHead.objects.filter(family__in=families)

                for head in family_heads:
                    expected_total = head.family.total_family_members
                    entered_members = Member.objects.filter(family_head=head).count()
                    total_with_head = entered_members + 1
                    missing = expected_total - total_with_head

                    if missing > 0:
                        writer.writerow([
                            samaj.samaj_name,
                            f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
                            head.phone_no,
                            total_with_head,
                            expected_total,
                            missing
                        ])
                        total_entered_all += total_with_head
                        total_expected_all += expected_total
                        total_missing_all += missing

            writer.writerow([])
            writer.writerow([
                'Total', '', '',
                total_entered_all,
                total_expected_all,
                total_missing_all
            ])

        # === File 3: Family Heads and Members Combined CSV ===
        combined_filename = f"family_heads_and_members_{today_str}.csv"
        combined_path = os.path.join(output_dir, combined_filename)

        if os.path.exists(combined_path):
            os.remove(combined_path)

        with open(combined_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"Family Heads and Members - {today_str}"])
            writer.writerow([])
            writer.writerow([
                'Created At', 'Samaj Name', 'Head of Family',
                'Total Members Needed', 'Total Members Entered', 'Remaining Members',
                'First Name', 'Middle Name', 'Last Name', 'Birth Date', 'Age', 'Gender',
                'Marital Status', 'Relation with Head',
                'Phone No', 'Alternative No', 'Landline No', 'Email ID',
                'Country', 'State', 'District', 'Pincode',
                'Building Name', 'Flat No', 'Door No', 'Street Name', 'Landmark',
                'Native City', 'Native State',
                'Qualification', 'Occupation', 'Nature of Duties', 'Blood Group', 'Social Media Link'
            ])

            heads = FamilyHead.objects.all()
            members = Member.objects.all()

            combined = sorted(
                chain(heads, members),
                key=attrgetter('created_at')
            )

            for obj in combined:
                if isinstance(obj, FamilyHead):
                    row = self.format_family_head_row(obj)
                else:
                    row = self.format_member_row(obj)
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(
            f'CSV files "{summary_filename}", "{incomplete_filename}", and "{combined_filename}" created successfully in "{output_dir}/"!'
        ))

    def format_family_head_row(self, head):
        family = head.family
        samaj = family.samaj
        number_of_members = Member.objects.filter(family_head=head).count() + 1
        remaining_members = family.total_family_members - number_of_members

        return [
            head.created_at.strftime('%Y-%m-%d %H:%M:%S') if head.created_at else '',
            samaj.samaj_name,
            f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
            family.total_family_members,
            number_of_members,
            remaining_members,
            
            head.name_of_head,
            head.middle_name,
            head.last_name,
            head.birth_date.strftime('%Y-%m-%d') if head.birth_date else '',
            head.age,
            head.gender,
            head.marital_status,
            "Self",
            head.phone_no,
            head.alternative_no,
            head.landline_no,
            head.email_id,
            head.country,
            head.state,
            head.district,
            head.pincode,
            head.building_name,
            head.flat_no,
            head.door_no,
            head.street_name,
            head.landmark,
            head.native_city,
            head.native_state,
            head.qualification,
            head.occupation,
            head.exact_nature_of_duties,
            head.blood_group,
            head.social_media_link
        ]

    def format_member_row(self, member):
        head = member.family_head
        family = head.family
        samaj = family.samaj
        number_of_members = Member.objects.filter(family_head=head).count() + 1
        remaining_members = family.total_family_members - number_of_members

        return [
            member.created_at.strftime('%Y-%m-%d %H:%M:%S') if member.created_at else '',
            samaj.samaj_name,
            f"{head.name_of_head} {head.middle_name} {head.last_name}".title().strip(),
            family.total_family_members,
            number_of_members,
            remaining_members,
            
            member.name,
            member.middle_name,
            member.last_name,
            member.birth_date.strftime('%Y-%m-%d') if member.birth_date else '',
            member.age,
            member.gender,
            member.marital_status,
            member.relation_with_family_head,
            member.phone_no,
            member.alternative_no,
            member.landline_no,
            member.email_id,
            member.country,
            member.state,
            member.district,
            member.pincode,
            member.building_name,
            member.flat_no,
            member.door_no,
            member.street_name,
            member.landmark,
            member.native_city,
            member.native_state,
            member.qualification,
            member.occupation,
            member.exact_nature_of_duties,
            member.blood_group,
            member.social_media_link
        ]
