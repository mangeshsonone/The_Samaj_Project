import logging
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from testapp.models import FamilyHead, Member
from .serializers import FamilyHeadSerializer, MemberSerializer

# Set up logger
logger = logging.getLogger(__name__)
import boto3
import logging
import hmac
import hashlib
import base64
from django.conf import settings
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


logger = logging.getLogger(__name__)

AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')
AWS_COGNITO_CLIENT_SECRET = os.environ.get('AWS_COGNITO_CLIENT_SECRET')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')

# AWS Credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# Initialize the Cognito client directly with AWS credentials (NOT RECOMMENDED for production)
cognito_client = boto3.client(
    'cognito-idp',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def calculate_secret_hash(username):
    message = username + AWS_COGNITO_CLIENT_ID
    dig = hmac.new(
        str(AWS_COGNITO_CLIENT_SECRET).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()
class LoginAPIView(APIView):
    """
    API view to handle user login via Cognito Custom Auth flow
    """
    
    def calculate_secret_hash(self, username):
        message = username + AWS_COGNITO_CLIENT_ID
        dig = hmac.new(
            str(AWS_COGNITO_CLIENT_SECRET).encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for login"""
        logger.info("Login API endpoint accessed")
        
        # Get phone number from request data
        phone_number = request.data.get('phone_number')
        if not phone_number:
            logger.warning("Phone number not provided in request")
            return Response(
                {"error": "Phone number is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        logger.info(f"Login attempt for phone number: {phone_number}")
        
        # Add country code if missing
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number  # Default to Indian numbers
            logger.debug(f"Added country code to phone number: {phone_number}")

        # Import Cognito client
        import boto3
        cognito_client = boto3.client('cognito-idp',
                                     region_name=settings.AWS_REGION)
        
        # First attempt to check if user exists
        try:
            user = cognito_client.admin_get_user(
                UserPoolId=settings.AWS_COGNITO_USER_POOL_ID,
                Username=phone_number
            )
            logger.info(f"User found in Cognito: {phone_number}")
            logger.debug(f"User status: {user['UserStatus']}, Enabled: {user['Enabled']}")
            
            # Check if user is enabled
            if not user.get('Enabled', True):
                logger.warning(f"Disabled user attempted login: {phone_number}")
                return Response(
                    {"error": "This account has been disabled. Please contact support."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except cognito_client.exceptions.UserNotFoundException:
            logger.warning(f"User not found in Cognito: {phone_number}")
            return Response(
                {"error": "User does not exist"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error validating user: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Generate secret hash
        try:
            secret_hash = self.calculate_secret_hash(phone_number)
            logger.debug("Secret hash generated successfully")
        except Exception as e:
            logger.error(f"Failed to calculate secret hash: {str(e)}", exc_info=True)
            return Response(
                {"error": "Authentication error. Please try again."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Initiate auth flow
        try:
            logger.info(f"Initiating CUSTOM_AUTH flow for: {phone_number}")
            response = cognito_client.initiate_auth(
                ClientId=settings.AWS_COGNITO_CLIENT_ID,
                AuthFlow='CUSTOM_AUTH',
                AuthParameters={
                    'USERNAME': phone_number,
                    'SECRET_HASH': secret_hash,
                }
            )
            
            logger.info(f"Authentication initiated successfully for: {phone_number}")
            
            # Store session in request.session for API consumers that maintain session
            request.session['cognito_session'] = {
                'username': phone_number,
                'session': response['Session'],
            }
            
            # Return session info in response for stateless API consumers
            return Response({
                "message": "Authentication initiated successfully",
                "username": phone_number,
                "session": response['Session'],
                "next_step": "verify_otp"
            }, status=status.HTTP_200_OK)
            
        except cognito_client.exceptions.UserNotFoundException:
            logger.warning(f"User not found during auth: {phone_number}")
            return Response(
                {"error": "User does not exist"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        except cognito_client.exceptions.NotAuthorizedException as e:
            logger.warning(f"Not authorized: {str(e)}")
            return Response(
                {"error": "Invalid credentials. Please try again."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        except cognito_client.exceptions.UserNotConfirmedException:
            logger.warning(f"User not confirmed: {phone_number}")
            return Response(
                {"error": "Account not confirmed. Please complete registration."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Login error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class VerifyOTPAPIView(APIView):
    """
    API view to handle OTP verification for Cognito Custom Auth flow
    """
    
    def post(self, request, *args, **kwargs):
        logger.info("OTP verification API accessed")
        
        otp = request.data.get('otp')
        logger.debug(f"OTP received of length: {len(otp) if otp else 0}")
        
        cognito_session = request.session.get('cognito_session')
        
        if not cognito_session:
            logger.warning("OTP verification attempted with expired session")
            return Response(
                {"error": "Session expired. Try login again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = cognito_session.get('username')
        logger.info(f"Verifying OTP for user: {username}")
        
        try:
            # Calculate the SECRET_HASH
            logger.debug("Calculating secret hash for OTP verification")
            secret_hash = calculate_secret_hash(username)
            
            # Verify the OTP with Cognito
            logger.info(f"Sending OTP verification request to Cognito for user: {username}")
            response = cognito_client.respond_to_auth_challenge(
                ClientId=settings.AWS_COGNITO_CLIENT_ID,
                ChallengeName='CUSTOM_CHALLENGE',
                Session=cognito_session['session'],
                ChallengeResponses={
                    'USERNAME': username,
                    'ANSWER': otp,
                    'SECRET_HASH': secret_hash
                }
            )
            
            # Check response for authentication result
            if 'AuthenticationResult' in response:
                logger.info(f"OTP verification successful for user: {username}")
                
                # Extract tokens
                id_token = response['AuthenticationResult']['IdToken']
                access_token = response['AuthenticationResult']['AccessToken']
                logger.debug("Authentication tokens received successfully")
                
                # Store tokens in session or return in response
                request.session['id_token'] = id_token
                request.session['access_token'] = access_token
                logger.debug("Authentication tokens stored in session")
                
                logger.info(f"User {username} successfully authenticated")
                
                return Response(
                    {"message": "OTP verification successful", "id_token": id_token, "access_token": access_token},
                    status=status.HTTP_200_OK
                )
            else:
                # This case handles when Cognito requires additional challenges
                logger.warning(f"Additional challenge required for user: {username}")
                challenge_name = response.get('ChallengeName')
                logger.debug(f"Next challenge: {challenge_name}")
                
                return Response(
                    {"message": f"Additional verification required: {challenge_name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except cognito_client.exceptions.CodeMismatchException:
            logger.warning(f"Invalid OTP provided for user: {username}")
            return Response(
                {"error": "Invalid verification code. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except cognito_client.exceptions.ExpiredCodeException:
            logger.warning(f"Expired OTP code for user: {username}")
            return Response(
                {"error": "Verification code has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except cognito_client.exceptions.NotAuthorizedException as e:
            logger.warning(f"Not authorized during OTP verification: {str(e)}")
            return Response(
                {"error": "Authentication failed. Please try again."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        except cognito_client.exceptions.TooManyRequestsException:
            logger.warning(f"Too many OTP verification attempts for user: {username}")
            return Response(
                {"error": "Too many attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
        except Exception as e:
            logger.error(f"OTP verification error for user {username}: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Verification error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





















class FamilyInformationView(APIView):
    """
    API View to retrieve family head and member information based on phone number passed as URL parameter
    """
   
    def get(self, request, phone_number, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Family information request received for phone: {phone_number}")

        if not phone_number:
            logger.warning("API request made with empty phone number")
            return Response({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to get the FamilyHead
            family_head = FamilyHead.objects.filter(phone_no=phone_number).first()
            if family_head:
                logger.info(f"Found family head: {family_head.name_of_head} (ID: {family_head.id})")
                members = Member.objects.filter(family_head=family_head)
                member_count = members.count()
                total_members_needed = family_head.family.total_family_members
                total_members_added = member_count + 1
                remaining_members = total_members_needed - total_members_added

                family_head_data = FamilyHeadSerializer(family_head).data
                family_head_data['full_name'] = f"{family_head.name_of_head} {family_head.middle_name or ''} {family_head.last_name}".title().strip()

                members_data = MemberSerializer(members, many=True).data
                for i, member in enumerate(members):
                    members_data[i]['full_name'] = f"{member.name} {member.middle_name or ''} {member.last_name}".title().strip()

                elapsed_time = time.time() - start_time
                logger.info(f"Family information request processed successfully in {elapsed_time:.2f} seconds")

                return Response({
                    'status': 'success',
                    'person_type': 'FamilyHead',
                    'FamilyHead':True,
                    'family_head': family_head_data,
                    'members': members_data,
                    'total_members_added': total_members_added,
                    'total_members_needed': total_members_needed,
                    'remaining_members': remaining_members
                }, status=status.HTTP_200_OK)

            # If not family head, try member
            member = Member.objects.filter(phone_no=phone_number).first()
            if member:
                logger.info(f"Phone number belongs to a member: {member.name} (ID: {member.id})")
                member_data = MemberSerializer(member).data
                member_data['full_name'] = f"{member.name} {member.middle_name or ''} {member.last_name}".title().strip()

                elapsed_time = time.time() - start_time
                logger.info(f"Member information request processed successfully in {elapsed_time:.2f} seconds")

                return Response({
                    'status': 'success',
                    'person_type': 'Member',
                    'Member': True,
                    'member': member_data
                }, status=status.HTTP_200_OK)

            logger.warning(f"No family head or member found with phone number: {phone_number}")
            return Response({
                'status': 'error',
                'message': 'No family head or member found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error processing family information for phone {phone_number}: {str(e)}", exc_info=True)
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
        start_time = time.time()
        logger.info(f"Family head edit request received for ID: {family_head_id}")
        
        try:
            # Get the family head with the provided ID
            logger.debug(f"Looking up family head with ID: {family_head_id}")
            try:
                family_head = get_object_or_404(FamilyHead, id=family_head_id)
                logger.info(f"Found family head: {family_head.name_of_head} (Phone: {family_head.phone_no})")
            except:
                logger.warning(f"No family head found with ID: {family_head_id}")
                return Response({
                    'status': 'error',
                    'message': 'No family head found with this ID'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Log the incoming data for debugging
            logger.debug(f"Received update data: {request.data}")
            
            # Update the family head with provided data
            logger.debug("Validating and updating family head data")
            serializer = FamilyHeadSerializer(family_head, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Log what fields are being updated
                updated_fields = [field for field in request.data.keys()]
                logger.info(f"Updating fields: {', '.join(updated_fields)}")
                
                # Save the updated data
                serializer.save()
                
                # Calculate execution time
                elapsed_time = time.time() - start_time
                logger.info(f"Family head updated successfully in {elapsed_time:.2f} seconds")
                
                return Response({
                    'status': 'success',
                    'message': 'Family head details updated successfully',
                    'family_head': serializer.data
                }, status=status.HTTP_200_OK)
            
            # Log validation errors
            logger.warning(f"Validation errors when updating family head ID {family_head_id}: {serializer.errors}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"Failed update request completed in {elapsed_time:.2f} seconds")
            
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error updating family head ID {family_head_id}: {str(e)}", exc_info=True)
            logger.info(f"Failed update request completed in {elapsed_time:.2f} seconds")
            
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberEditView(APIView):
    """
    API View to edit member information based on ID
    """
   
    
    def put(self, request, member_id, *args, **kwargs):
        """
        Update member information
        
        URL format: /api/member/edit/{member_id}/
        """
        start_time = time.time()
        logger.info(f"Member edit request received for ID: {member_id}")
        
        try:
            # Get the member with the provided ID
            logger.debug(f"Looking up member with ID: {member_id}")
            try:
                member = get_object_or_404(Member, id=member_id)
                logger.info(f"Found member: {member.name} (Family Head ID: {member.family_head.id})")
            except:
                logger.warning(f"No member found with ID: {member_id}")
                return Response({
                    'status': 'error',
                    'message': 'No member found with this ID'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Log the incoming data for debugging
            logger.debug(f"Received update data: {request.data}")
            
            # Update the member with provided data
            logger.debug("Validating and updating member data")
            serializer = MemberSerializer(member, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Log what fields are being updated
                updated_fields = [field for field in request.data.keys()]
                logger.info(f"Updating fields: {', '.join(updated_fields)}")
                
                # Save the updated data
                serializer.save()
                
                # Calculate execution time
                elapsed_time = time.time() - start_time
                logger.info(f"Member updated successfully in {elapsed_time:.2f} seconds")
                
                return Response({
                    'status': 'success',
                    'message': 'Member details updated successfully',
                    'member': serializer.data
                }, status=status.HTTP_200_OK)
            
            # Log validation errors
            logger.warning(f"Validation errors when updating member ID {member_id}: {serializer.errors}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"Failed update request completed in {elapsed_time:.2f} seconds")
            
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error updating member ID {member_id}: {str(e)}", exc_info=True)
            logger.info(f"Failed update request completed in {elapsed_time:.2f} seconds")
            
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
        start_time = time.time()
        logger.info(f"Member delete request received for ID: {member_id}")
        
        try:
            # Get the member with the provided ID
            logger.debug(f"Looking up member with ID: {member_id}")
            try:
                member = get_object_or_404(Member, id=member_id)
                logger.info(f"Found member: {member.name} (Family Head ID: {member.family_head.id})")
            except:
                logger.warning(f"No member found with ID: {member_id}")
                return Response({
                    'status': 'error',
                    'message': 'No member found with this ID'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Store family head information before deletion for the response
            family_head = member.family_head
            member_name = member.name
            
            logger.info(f"Deleting member: {member_name} (ID: {member_id}) from family head: {family_head.name_of_head}")
            
            # Delete the member
            member.delete()
            logger.debug(f"Member {member_id} successfully deleted from database")
            
            # Get updated members list
            remaining_members = Member.objects.filter(family_head=family_head)
            remaining_count = remaining_members.count()
            logger.info(f"Family now has {remaining_count} remaining members (excluding head)")
            
            elapsed_time = time.time() - start_time
            logger.info(f"Member deletion completed successfully in {elapsed_time:.2f} seconds")
            
            return Response({
                'status': 'success',
                'message': f'Member "{member_name}" deleted successfully',
                'family_head': FamilyHeadSerializer(family_head).data,
                'remaining_members': MemberSerializer(remaining_members, many=True).data,
                'total_members': remaining_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error deleting member ID {member_id}: {str(e)}", exc_info=True)
            logger.info(f"Failed deletion request completed in {elapsed_time:.2f} seconds")
            
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CreateMemberAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, familyhead_id, *args, **kwargs):
        family_head = get_object_or_404(FamilyHead, pk=familyhead_id)
        total_members_allowed = family_head.family.total_family_members - 1  # excluding head
        current_member_count = Member.objects.filter(family_head=family_head).count()

        if current_member_count >= total_members_allowed:
            return Response({
                'status': 'error',
                'message': 'All family members already added. Update total members in family to add more.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save(family_head=family_head)
            return Response({
                'status': 'success',
                'message': 'Family member added successfully.',
                'member': MemberSerializer(member).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
