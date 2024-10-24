# backend/app/services/twillo_services/twillo_service.py
import os
from twilio.rest import Client


def send_sms(to_number, message):
    try:
        from_number = '+14437207185'
        token = 'd2d834dbbd44eb147ff25e06ce86f5be'
        sid = 'AC9c94883f42735af2696953c2d4f1a2cb'
        #twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        #twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        #twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')

        if not sid or not token or not from_number:
            raise ValueError("Twilio configuration not found in environment variables")

        client = Client(sid, token)
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print(f"SMS sent successfully. Message SID: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")


# Test the send_sms function
#to_number = "+12563440264"
#message = "Hello, this is a test SMS message from Q! I can now reach your phone. \nPlease do once again attempt to register.\nQ, just Q"
#send_sms(to_number, message)