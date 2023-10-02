from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True)
def sending_otp(self,email,otp):
    try:
        send_mail(
            "Well Come to Bookingly",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email, ]
        )
    except Exception as e:
        return str(e)
    return "OTP is sent"

@shared_task(bind=True)
def sending_token_mail(self,email,otp,seller_username):
    try:
        send_mail(
            "Bookingly Email Verification",
            f"{seller_username} Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email, ]
        )
    except Exception as e:
        return str(e)
    return "OTP is sent for forget password"