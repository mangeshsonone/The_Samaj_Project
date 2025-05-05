from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from testapp.models import FamilyHead, Member
from .serializers import FamilyHeadSerializer, MemberSerializer

class FamilyInformationView(APIView):
    """
    API View to retrieve family head and member information based on phone number passed as URL parameter
    """
    permission_classes = [AllowAny]
    
    def get(self, request, phone_number, *args, **kwargs):
        """
        Get family information using phone number from URL parameter
        
        URL format: /api/family-info/{phone_number}/
        """
        if not phone_number:
            return Response({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the family head with the provided phone number
            family_head = get_object_or_404(FamilyHead, phone_no=phone_number)
            
            # Get all members associated with this family head
            members = Member.objects.filter(family_head=family_head)
            
            # Get the total members needed from the family model
            total_members_needed = family_head.family.total_family_members
            
            # Calculate total members added (family head + members)
            total_members_added = len(members) + 1
            
            # Calculate remaining members
            remaining_members = total_members_needed - total_members_added
            
            # Serialize the data
            family_head_data = FamilyHeadSerializer(family_head).data
            # Add full name to family head data
            first_name = family_head.name_of_head
            middle_name = family_head.middle_name if family_head.middle_name else ""
            last_name = family_head.last_name
            family_head_data['full_name'] = f"{first_name} {middle_name} {last_name}".title().strip()
            
            members_data = MemberSerializer(members, many=True).data
            # Add full name to each member
            for i, member in enumerate(members):
                first_name = member.name
                middle_name = member.middle_name if member.middle_name else ""
                last_name = member.last_name
                members_data[i]['full_name'] = f"{first_name} {middle_name} {last_name}".title().strip()
            
            return Response({
                'status': 'success',
                'family_head': family_head_data,
                'members': members_data,
                'total_members_added': total_members_added,
                'total_members_needed': total_members_needed,
                'remaning_members': remaining_members
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FamilyHeadEditView(APIView):
    """
    API View to edit family head information based on ID
    """
    permission_classes = [AllowAny]
    
    def put(self, request, family_head_id, *args, **kwargs):
        """
        Update family head information
        
        URL format: /api/family-head/edit/{family_head_id}/
        """
        try:
            # Get the family head with the provided ID
            family_head = get_object_or_404(FamilyHead, id=family_head_id)
            
            # Update the family head with provided data
            serializer = FamilyHeadSerializer(family_head, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Family head details updated successfully',
                    'family_head': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberEditView(APIView):
    """
    API View to edit member information based on ID
    """
    permission_classes = [AllowAny]
    
    def put(self, request, member_id, *args, **kwargs):
        """
        Update member information
        
        URL format: /api/member/edit/{member_id}/
        """
        try:
            # Get the member with the provided ID
            member = get_object_or_404(Member, id=member_id)
            
            # Update the member with provided data
            serializer = MemberSerializer(member, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Member details updated successfully',
                    'member': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyBulkEditView(APIView):
    """
    API View to edit both family head and all associated members in one request
    """
    permission_classes = [AllowAny]
    
    def put(self, request, family_head_id, *args, **kwargs):
        """
        Update family head and member information
        
        URL format: /api/family/bulk-edit/{family_head_id}/
        
        Expected request format:
        {
            "family_head": {
                "name": "Updated Name",
                ...
            },
            "members": [
                {
                    "id": 1,
                    "name": "Updated Member Name",
                    ...
                },
                ...
            ]
        }
        """
        try:
            # Get the family head with the provided ID
            family_head = get_object_or_404(FamilyHead, id=family_head_id)
            
            # Update family head if data is provided
            if 'family_head' in request.data:
                head_serializer = FamilyHeadSerializer(
                    family_head, 
                    data=request.data['family_head'], 
                    partial=True
                )
                
                if not head_serializer.is_valid():
                    return Response({
                        'status': 'error',
                        'message': 'Invalid family head data',
                        'errors': head_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                head_serializer.save()
                head_data = head_serializer.data
            else:
                head_data = FamilyHeadSerializer(family_head).data
            
            # Update members if data is provided
            members_data = []
            if 'members' in request.data and isinstance(request.data['members'], list):
                for member_data in request.data['members']:
                    if 'id' not in member_data:
                        return Response({
                            'status': 'error',
                            'message': 'Member ID is required for updating members'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    try:
                        member = get_object_or_404(Member, id=member_data['id'])
                        
                        # Verify member belongs to this family head
                        if member.family_head.id != family_head.id:
                            return Response({
                                'status': 'error',
                                'message': f'Member with ID {member_data["id"]} does not belong to this family'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        member_serializer = MemberSerializer(member, data=member_data, partial=True)
                        
                        if member_serializer.is_valid():
                            member_serializer.save()
                            members_data.append(member_serializer.data)
                        else:
                            return Response({
                                'status': 'error',
                                'message': f'Invalid data for member with ID {member_data["id"]}',
                                'errors': member_serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)
                            
                    except Exception as e:
                        return Response({
                            'status': 'error',
                            'message': f'Error updating member with ID {member_data["id"]}: {str(e)}'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # If no members were updated, get all members for the response
            if not members_data:
                members = Member.objects.filter(family_head=family_head)
                members_data = MemberSerializer(members, many=True).data
            
            return Response({
                'status': 'success',
                'message': 'Family information updated successfully',
                'family_head': head_data,
                'members': members_data,
                'total_members': len(members_data)
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MemberDeleteView(APIView):
    """
    API View to delete a member from a family based on member ID
    """
    permission_classes = [AllowAny]
    
    def delete(self, request, member_id, *args, **kwargs):
        """
        Delete a member from the database
        
        URL format: /api/member/delete/{member_id}/
        """
        try:
            # Get the member with the provided ID
            member = get_object_or_404(Member, id=member_id)
            
            # Store family head information before deletion for the response
            family_head = member.family_head
            member_name = member.name  # Assuming Member model has a name field
            
            # Delete the member
            member.delete()
            
            # Get updated members list
            remaining_members = Member.objects.filter(family_head=family_head)
            
            return Response({
                'status': 'success',
                'message': f'Member "{member_name}" deleted successfully',
                'family_head': FamilyHeadSerializer(family_head).data,
                'remaining_members': MemberSerializer(remaining_members, many=True).data,
                'total_members': remaining_members.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

