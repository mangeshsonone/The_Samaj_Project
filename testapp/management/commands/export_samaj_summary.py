import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member


class Command(BaseCommand):
    help = 'Export Samaj summary to a CSV file'

    def handle(self, *args, **kwargs):
        # Create output directory if it doesn't exist
        output_dir = 'exports'
        os.makedirs(output_dir, exist_ok=True)

        # File name with current date
        filename = f"samaj_summary_{datetime.now().strftime('%Y-%m-%d')}.csv"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Header row
            writer.writerow([
                f"Samaj Summary Report - {datetime.now().strftime('%Y-%m-%d')}"
            ])
            writer.writerow([])  # Empty row
            writer.writerow(['Samaj Name', 'Total Family', 'Total Members', 'Actual Member Count Needed', 'Missing Member Count'])

            # Totals counters
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

                # Write row
                writer.writerow([
                    samaj.samaj_name,
                    total_heads,
                    actual_entries,
                    total_expected,
                    remaining
                ])

                # Update grand totals
                grand_total_heads += total_heads
                grand_actual_members += actual_entries
                grand_expected_members += total_expected
                grand_remaining += remaining

            # Write total row
            writer.writerow([])
            writer.writerow([
                'Total',
                grand_total_heads,
                grand_actual_members,
                grand_expected_members,
                grand_remaining
            ])

        self.stdout.write(self.style.SUCCESS(f'CSV file "{filename}" created successfully at "{file_path}"!'))
