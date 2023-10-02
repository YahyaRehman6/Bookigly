from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def sending_otp_mail_api_task(self,username,otp,email):
    print(username," your otp is ",otp)
    send_mail(
        "Email Verification",
        f"hey {username} your otp is {otp}",
        settings.EMAIL_HOST_USER,
        [email, ]
    )
    return "OTP Sent"