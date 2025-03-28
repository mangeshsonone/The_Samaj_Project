from django.shortcuts import render

from twilio.rest import Client
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
import json 
import os
from dotenv import load_dotenv
from .models import Samaj,Family,Member,FamilyHead
from django.core.exceptions import ObjectDoesNotExist
import logging
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
import requests

# account_sid = os.getenv('TWILIO_ACCOUNT_SID')
# auth_token = os.getenv('TWILIO_AUTH_TOKEN')

class MessageHandler:
    phone_number=None
    otp=None
    def __init__(self,phone_number,otp):
        self.phone_number=phone_number
        self.otp=otp

    def send_otp_on_phone(self):
        url = "https://graph.facebook.com/v22.0/608304119029688/messages"

        headers = {
            "Authorization": "Bearer EAAYS0hvZA8I4BOZCDUvYpeATA1GZA7pVqqfYc700yZCnqUPxRNivzyn1FelRpDSNBWW9wStK1KupFwRbSGTdjfiurFebt7EzTVM8UXkcoZAr3kSa8HyjTnOpgA9GjEcYblI97u2ZAoEy42T3R4DgiJehr30LSv4sQadVB7yVP2XXEgdpMMgxhMGcx0uoIOglF3swaW5tvFnqBwkTwcs1qNi2jOTl2Txri5rDEZD",
            "Content-Type": "application/json"
        }

        data = {
            "messaging_product": "whatsapp",
            "to": "917620777405",
            "type": "template",
            "template": {
                "name": "my_firstcode",  # Your approved template name
                "language": {"code": "en_US"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": str(self.otp)}  # OTP Code
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": 0,
                        "parameters": [
                            {"type": "text", "text": str(self.otp)}  # Value for {{1}} in template URL
                        ]
                    }
                ]
            }
        }




        response = requests.post(url, headers=headers, json=data)

        print(response.status_code)
        print(response.json())

    #      data = {
    #     "messaging_product": "whatsapp",
    #     "to": "917620777405",
    #     "type": "template",
    #     "template": {
    #         "name": "otp_template",
    #         "language": {"code": "en_US"},
            
            
    #     }
    # }

    #      response = requests.post(url, headers=headers, json=data)





        # account_sid = 'AC2a1a0262c585836beb7b01d152d0487a'
        # auth_token = '76f9d695369a5cdcf1dddbbbc4b006eb'  # ✅ Remove the square brackets!
        # client = Client(account_sid, auth_token)
        
        # message = client.messages.create(
        #     from_='+15856481063',
        #     body=f'Your OTP is {self.otp}',  # ✅ Send the actual OTP
        #     to='+91'+self.phone_number
        # )

        # print("OTP sent successfully:", message.sid)
        


# def send_whatsapp_message(request):
#     url = "https://graph.facebook.com/v22.0/608304119029688/messages"
    
#     headers = {
#         "Authorization": "Bearer YOUR_ACCESS_TOKEN",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "messaging_product": "whatsapp",
#         "to": "917620777405",
#         "type": "template",
#         "template": {
#             "name": "hello_world",
#             "language": {"code": "en_US"}
#         }
#     }

#     response = requests.post(url, headers=headers, json=data)
    
#     return JsonResponse(response.json())
