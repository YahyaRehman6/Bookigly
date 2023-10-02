from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def sending_mail(self,username,token,email):
    print(f"Hey {username} please click on the link for verification http://127.0.0.1:8000/customer/token/{token}/{username}/",)
    # send_mail(
    # "Account Verification",
    # f"Hey {username} please click on the link for verification http://127.0.0.1:8000/customer/token/{token}/{username}/",
    # settings.EMAIL_HOST_USER,
    # [email,]
    # )
    return "Task Done"


@shared_task(bind=True)
def sending_mail_for_customer_forget_password(self,username,otp,email):
    print(otp)
    # send_mail(
    #     "Otp Verification",
    #     f"Your{username} OTP is {otp}",
    #     settings.EMAIL_HOST_USER,
    #     [email, ]
    # )
    return "Otp sent"