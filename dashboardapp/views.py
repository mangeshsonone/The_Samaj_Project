from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from testapp.models import Samaj, Family, FamilyHead, Member

class DashboardDataAPIView(APIView):
    def get(self, request):
        samaj_data = []
        incomplete_heads = []
        a=10
        samajs = Samaj.objects.all()
        for samaj in samajs:
            families = Family.objects.filter(samaj=samaj)
            valid_families = families.filter(
                id__in=FamilyHead.objects.filter(family__in=families).values('family_id')
            )
            family_heads = FamilyHead.objects.filter(family__in=valid_families)
            members = Member.objects.filter(family_head__in=family_heads)

            total_heads = family_heads.count()
            total_expected = valid_families.aggregate(total=Sum('total_family_members'))['total'] or 0
            actual_members = members.count() + total_heads
            remaining = max(total_expected - actual_members, 0)

            samaj_data.append({
                "name": samaj.samaj_name,
                "families": total_heads,
                "members": actual_members,
                "needed": total_expected,
            })

            for head in family_heads:
                expected = head.family.total_family_members
                entered = Member.objects.filter(family_head=head).count()
                with_head = entered + 1
                missing = expected - with_head
                if missing > 0:
                    incomplete_heads.append({
                        "samaj": samaj.samaj_name,
                        "head": head.name_of_head,
                        "phone": head.phone_no,
                        "expected": expected,
                        "entered": with_head,
                        "missing": missing
                    })

        return Response({
            "chart_data": samaj_data,
            "incomplete_heads": incomplete_heads,
        })
