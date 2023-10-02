from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True)
def sending_mail_token(self,username,email,token):
    try:
        send_mail(
            "Well Come to Bookingly",
            f"Hey {username} please click on the link for verification http://127.0.0.1:8000/seller/token/{username}/{token}/",
            settings.EMAIL_HOST_USER,
            [email, ]
        )
    except Exception as e:
        return e
    return "Task Done"

@shared_task(bind=True)
def sending_mail_otp(self,username,otp,email):
    try:
        send_mail(
            "Bookingly Verifiation",
            f"Hey {username} your otp is {otp}",
            settings.EMAIL_HOST_USER,
            [email,]
        )
        return "Task Done"
    except Exception as e:
        return str(e)


@shared_task(bind=True)
def sending_seller_forgot_password_otp_mail(self,otp,email):
    print(otp)
    print(email)
    send_mail(
        "Otp Verification",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email,]
        )
