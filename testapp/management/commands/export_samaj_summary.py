import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member


class Command(BaseCommand):
    help = 'Export Samaj summary and incomplete family heads to CSV files'

    def handle(self, *args, **kwargs):
        # Create output directory if it doesn't exist
        output_dir = 'exports'
        os.makedirs(output_dir, exist_ok=True)

        today_str = datetime.now().strftime('%Y-%m-%d')

        # === File 1: Samaj Summary CSV ===
        summary_filename = f"samaj_summary_{today_str}.csv"
        summary_path = os.path.join(output_dir, summary_filename)

        with open(summary_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"Samaj Summary Report - {today_str}"])
            writer.writerow([])
            writer.writerow(['Samaj Name', 'Total Family', 'Total Members Entered', 'Actual Member Count Needed', 'Missing Member Count'])

            grand_total_heads = 0
            grand_actual_members = 0
            grand_expected_members = 0
            grand_remaining = 0

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

        self.stdout.write(self.style.SUCCESS(
            f'CSV files "{summary_filename}" and "{incomplete_filename}" created successfully in "{output_dir}/"!'
        ))
