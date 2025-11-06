"""
Email and SMS Testing Alternatives

Multiple options for testing email/SMS without production API keys:
1. Console/Logging - Print to console (default for development)
2. Mailtrap - Email testing service (free tier available)
3. MailHog - Local email server (Docker)
4. Twilio Test Credentials - Free test account
5. MockSMS - Simple SMS testing service
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
import httpx
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailProvider:
    """Email provider with multiple testing options"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider
        Returns True if sent successfully
        """
        from_email = from_email or settings.SENDGRID_FROM_EMAIL
        test_mode = settings.EMAIL_TEST_MODE.lower()
        
        if test_mode == "console":
            return EmailProvider._send_console(to_email, subject, body, from_email)
        elif test_mode == "mailtrap":
            return EmailProvider._send_mailtrap(to_email, subject, body, from_email)
        elif test_mode == "mailhog":
            return EmailProvider._send_mailhog(to_email, subject, body, from_email)
        elif test_mode == "sendgrid":
            return EmailProvider._send_sendgrid(to_email, subject, body, from_email)
        elif test_mode == "ses":
            return EmailProvider._send_ses(to_email, subject, body, from_email)
        else:
            logger.warning(f"Unknown email test mode: {test_mode}, using console")
            return EmailProvider._send_console(to_email, subject, body, from_email)
    
    @staticmethod
    def _send_console(to_email: str, subject: str, body: str, from_email: str) -> bool:
        """Print email to console (for testing)"""
        print("\n" + "="*80)
        print("📧 EMAIL (Console Mode)")
        print("="*80)
        print(f"From: {from_email}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
        logger.info(f"Email sent (console): {to_email} - {subject}")
        return True
    
    @staticmethod
    def _send_mailtrap(to_email: str, subject: str, body: str, from_email: str) -> bool:
        """Send via Mailtrap API (email testing service)"""
        if not settings.MAILTRAP_API_TOKEN:
            logger.error("MAILTRAP_API_TOKEN not configured, falling back to console")
            return EmailProvider._send_console(to_email, subject, body, from_email)
        
        try:
            # Mailtrap API endpoint
            url = "https://send.api.mailtrap.io/api/send"
            headers = {
                "Authorization": f"Bearer {settings.MAILTRAP_API_TOKEN}",
                "Content-Type": "application/json"
            }
            data = {
                "from": {"email": from_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "text": body,
                "html": body.replace("\n", "<br>")
            }
            
            response = httpx.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Email sent via Mailtrap: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Mailtrap error: {e}, falling back to console")
            return EmailProvider._send_console(to_email, subject, body, from_email)
    
    @staticmethod
    def _send_mailhog(to_email: str, subject: str, body: str, from_email: str) -> bool:
        """Send via MailHog (local SMTP server)"""
        try:
            # MailHog SMTP server
            server = smtplib.SMTP(settings.MAILHOG_HOST, settings.MAILHOG_PORT)
            server.set_debuglevel(0)  # Set to 1 for debug output
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent via MailHog: {to_email}")
            return True
        except Exception as e:
            logger.error(f"MailHog error: {e}, falling back to console")
            return EmailProvider._send_console(to_email, subject, body, from_email)
    
    @staticmethod
    def _send_sendgrid(to_email: str, subject: str, body: str, from_email: str) -> bool:
        """Send via SendGrid API"""
        if not settings.SENDGRID_API_KEY:
            logger.error("SENDGRID_API_KEY not configured")
            return False
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            response = sg.send(message)
            logger.info(f"Email sent via SendGrid: {to_email}, status: {response.status_code}")
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False
    
    @staticmethod
    def _send_ses(to_email: str, subject: str, body: str, from_email: str) -> bool:
        """Send via AWS SES"""
        try:
            import boto3
            ses = boto3.client('ses')
            response = ses.send_email(
                Source=from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            logger.info(f"Email sent via SES: {to_email}, message_id: {response['MessageId']}")
            return True
        except Exception as e:
            logger.error(f"AWS SES error: {e}")
            return False


class SMSProvider:
    """SMS provider with multiple testing options"""
    
    @staticmethod
    def send_sms(
        to_phone: str,
        message: str,
        from_number: Optional[str] = None
    ) -> bool:
        """
        Send SMS using configured provider
        Returns True if sent successfully
        """
        from_number = from_number or settings.TWILIO_FROM_NUMBER
        test_mode = settings.SMS_TEST_MODE.lower()
        
        if test_mode == "console":
            return SMSProvider._send_console(to_phone, message, from_number)
        elif test_mode == "twilio_test":
            return SMSProvider._send_twilio_test(to_phone, message, from_number)
        elif test_mode == "twilio":
            return SMSProvider._send_twilio(to_phone, message, from_number)
        elif test_mode == "mocksms":
            return SMSProvider._send_mocksms(to_phone, message, from_number)
        else:
            logger.warning(f"Unknown SMS test mode: {test_mode}, using console")
            return SMSProvider._send_console(to_phone, message, from_number)
    
    @staticmethod
    def _send_console(to_phone: str, message: str, from_number: Optional[str]) -> bool:
        """Print SMS to console (for testing)"""
        print("\n" + "="*80)
        print("📱 SMS (Console Mode)")
        print("="*80)
        print(f"From: {from_number or 'N/A'}")
        print(f"To: {to_phone}")
        print("-"*80)
        print(message)
        print("="*80 + "\n")
        logger.info(f"SMS sent (console): {to_phone}")
        return True
    
    @staticmethod
    def _send_twilio_test(to_phone: str, message: str, from_number: Optional[str]) -> bool:
        """Send via Twilio Test Credentials (free, no charges)"""
        account_sid = settings.TWILIO_TEST_ACCOUNT_SID or settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_TEST_AUTH_TOKEN or settings.TWILIO_AUTH_TOKEN
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured, falling back to console")
            return SMSProvider._send_console(to_phone, message, from_number)
        
        try:
            from twilio.rest import Client
            
            client = Client(account_sid, auth_token)
            
            # Use test number format or provided from_number
            test_from = from_number or "+15005550006"  # Twilio test number
            
            message_obj = client.messages.create(
                body=message,
                from_=test_from,
                to=to_phone
            )
            logger.info(f"SMS sent via Twilio Test: {to_phone}, sid: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Twilio Test error: {e}, falling back to console")
            return SMSProvider._send_console(to_phone, message, from_number)
    
    @staticmethod
    def _send_twilio(to_phone: str, message: str, from_number: Optional[str]) -> bool:
        """Send via Twilio Production API"""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.error("Twilio credentials not configured")
            return False
        
        if not from_number:
            logger.error("TWILIO_FROM_NUMBER not configured")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            logger.info(f"SMS sent via Twilio: {to_phone}, sid: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Twilio error: {e}")
            return False
    
    @staticmethod
    def _send_mocksms(to_phone: str, message: str, from_number: Optional[str]) -> bool:
        """Send via MockSMS service (for testing)"""
        try:
            # MockSMS API endpoint (example - adjust based on actual service)
            url = "https://api.mocksms.com/send"
            data = {
                "to": to_phone,
                "from": from_number or "TEST",
                "message": message
            }
            
            response = httpx.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"SMS sent via MockSMS: {to_phone}")
            return True
        except Exception as e:
            logger.error(f"MockSMS error: {e}, falling back to console")
            return SMSProvider._send_console(to_phone, message, from_number)

