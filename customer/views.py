from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from .forms import *
from accounts.models import *
import uuid
import random
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from accounts.models import User as Customer
from .tasks import sending_mail,sending_mail_for_customer_forget_password
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.contrib import messages
# Create your views here.
@transaction.atomic()
def Customer_Creation(request):
    """
    Customer Creation view
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer/home/')

    else:
        try:
            if request.method == "POST":
                detail = CustomUserCreationForm(request.POST)

                if detail.is_valid():

                    token = str(uuid.uuid4())
                    username = detail.cleaned_data['username']
                    email = detail.cleaned_data['email']
                    first_name = detail.cleaned_data['first_name']
                    last_name = detail.cleaned_data['last_name']
                    password = detail.cleaned_data['password1']
                    phone = detail.cleaned_data['phone_number']

                    customer = Customer(
                        username=username,
                        email = email,
                        first_name=first_name,
                        last_name=last_name,
                        phone_number = phone,
                        token=token,
                        is_seller = False,
                    )
                    customer.set_password(password)
                    customer.save()

                    # sending task to tasks.py file

                    sending_mail.delay(username=username, token=token, email=email)
                    return HttpResponse("Check Mail")

            else:
                detail = CustomUserCreationForm()

            return render(request, "customer/login_signin.html", {'detail': detail, "signin": True})

        except Exception as e:
            return HttpResponse(str(e))


def Gmail_Token_Verification(request,token,username):
    """
    Token Verification of customer email
    """
    try:
        customer = Customer.objects.get(username=username,is_seller=False)


        if customer.token == token:

            customer.is_verified = True
            customer.save()
            messages.success(request,"Your Verification is Complete now you can login")
            return HttpResponseRedirect("/customer/login/")

        else:
            return HttpResponse("Invalid Token")

    except Exception as e:
        return HttpResponse(str(e))



def Customer_Login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer/home/')
    else:
        try:
            if request.method == "POST":
                detail = AuthenticationForm(request=request,data=request.POST)

                if detail.is_valid():
                    username = detail.cleaned_data['username']
                    password = detail.cleaned_data['password']
                    obj = authenticate(username=username,password=password)

                    user = Customer.objects.get(username=username,is_seller=False)

                    if (obj is not None) and (user.is_verified) and (not user.is_seller):
                        login(request,obj)
                        return HttpResponseRedirect("/customer/home/")

                    elif (obj is not None) and (user.is_verified) and (user.is_seller):
                        return HttpResponse("Go to the seller application")

                    else:
                        messages.error(request,"User not found")

                else:
                    messages.error(request,"Invalid Information")

            else:
                detail = AuthenticationForm()

            return render(request,"customer/login_signin.html",{'detail':detail,"login":True})

        except Exception as e:
            return HttpResponse(str(e))


def Customer_Home(request):
    if request.user.is_authenticated:

        try:
            objects = Customer.objects.filter(is_seller=True)
            images = Hotel_Images.objects.all()
            return render(request, 'customer/home.html', {'name': request.user, 'objects': objects, "images": images})

        except Exception as e:
            return HttpResponse(str(e))

    else:
        return HttpResponseRedirect('/customer/login/')

def customer_total_reservations(request):
    if request.user.is_authenticated:
        resevations = Room_Reservation.objects.filter(username=request.user.username)
        return render(request,'customer/total_reservations.html',{'reservations':resevations})
    else:
        return HttpResponseRedirect('/customer/login/')



def customer_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect('/customer/login/')


@transaction.atomic()
def Edit_Customer_Information(request):
    if request.user.is_authenticated:
        user = Customer.objects.get(username=request.user)
        if request.method == "POST":
            detail = CustomerChangeForm(request.POST,instance=user)
            if detail.is_valid():
                detail.save()
        else:
            detail = CustomerChangeForm(instance=user)
        return render(request,"customer/login_signin.html",{'detail':detail,"change":True})



@transaction.atomic()
def Customer_Password_Change(request):

    if request.user.is_authenticated:

        if request.method == "POST":
            detail = PasswordChangeForm(data=request.POST,user=request.user)

            if detail.is_valid():
                detail.save()
                messages.success(request,"Password Updated")
                return HttpResponseRedirect('/customer/home/')

            else:
                messages.error(request,"Invalid Information")

        else:
            detail = PasswordChangeForm(user=request.user)
        return render(request,"customer/login_signin.html",{"detail":detail,"password":True})

    else:
        return HttpResponseRedirect('/customer_login/')



def hotel_detail(request,seller_id):
    if request.user.is_authenticated:
        object = Customer.objects.get(id=seller_id)
        rooms = Room.objects.filter(seller_id=seller_id)
        amenities = Room_Amenities.objects.filter(seller_id=seller_id)
        images = Room_Images.objects.filter(seller_id=seller_id)
        return render(request,"customer/hotel_rooms.html",{
            'object':object,
            'rooms':rooms,
            'amenities':amenities,
            'images':images,
            })
    else:
        return HttpResponseRedirect('/customer/login/')

from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def customer_reservation(request, room_id, seller_id, room_number):

    if request.user.is_authenticated:

        customer = Customer.objects.get(username=request.user)
        room = Room.objects.filter(id=room_id, seller_id=seller_id, room_number=room_number).exists()
        room_number = Room.objects.get(id=room_id).room_number
        reserved_dates = Room_Reservation.objects.filter(seller_id=seller_id, room_id=room_id)
        group_name = Customer.objects.get(id=seller_id).username

        if request.method == "POST":
            detail = Room_Reservation_Form(request.POST)
            if detail.is_valid():

                if room:
                    check_in_date = detail.cleaned_data['check_in_date']
                    check_out_date = detail.cleaned_data['check_out_date']
                    check = Room_Reservation.objects.filter(
                                Q(seller = seller_id,room_id = room_id,check_in_date__range = (check_in_date,check_out_date))
                                | Q(seller = seller_id,room_id = room_id,check_out_date__range = (check_in_date,check_out_date))

                                ).exists()
                    print("Checking ",check)
                    if check:
                        messages.error(request, "Room is reserved during your check in ")
                        return HttpResponseRedirect(
                            f'/customer/customer_reservation/{room_id}/{seller_id}/{room_number}/')
                    else:
                        reservation_obj = Room_Reservation(
                            seller_id=seller_id,
                            room_id=room_id,
                            room_number=room_number,
                            email=customer.email,
                            username=request.user.username,
                            name=detail.cleaned_data['name'],
                            phone_number=detail.cleaned_data['phone_number'],
                            check_in_date=check_in_date,
                            check_out_date=check_out_date
                        )
                        reservation_obj.save()

                        # we alredy create a group of seller name now we send message in that group
                        channel_layer = get_channel_layer()
                        message = {
                            "type": "noti.app",
                            "text": json.dumps({"message": f"Reservation is received of room number {room_number}"})
                        }
                        async_to_sync(channel_layer.group_send)(group_name, message)
                        messages.success(request, "Reservation Complete wait for response from hotel")

                    return HttpResponseRedirect('/customer/home/')
                else:
                    raise ValueError("Invalid Data")
        else:
            detail = Room_Reservation_Form()

        return render(request, 'customer/customer_reservation.html', {
            "room_reservation_form": detail, "room_number": room_number, 'reserved_dates': reserved_dates
            , "hotel_id": seller_id})
    else:
        return HttpResponseRedirect('/customer/login/')


def customer_forgot_password_mail(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer/home/')
    else:
        if request.method == "POST":
            password_form = Customer_Forgot_Password_mail_Form(request.POST)
            if password_form.is_valid():
                mail = password_form.cleaned_data['email']
                customer_obj = Customer.objects.get(email=mail)
                otp = random.randint(100000, 999999)
                customer_obj.otp = otp
                customer_obj.save()
                sending_mail_for_customer_forget_password.delay(
                    username = customer_obj.username,
                    email = mail,
                    otp = otp
                )

                return HttpResponseRedirect(f'/customer/otp_verification/{customer_obj.id}/')

        else:
            password_form = Customer_Forgot_Password_mail_Form()
        return render(request, "customer/forgot_pass.html", {'password_form': password_form})


def customer_otp_verification(request, id):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer/home/')
    else:
        if request.method == "POST":
            otp_form = Customer_OTP_Form(request.POST)
            if otp_form.is_valid():
                otp = otp_form.cleaned_data['otp']
                try:
                    customer_obj = Customer.objects.get(id=id)
                    if otp == customer_obj.otp:
                        customer_obj.otp = 0
                        customer_obj.save()
                        return HttpResponseRedirect(f'/customer/reset_password/{id}/')
                    else:
                        messages.error(request, 'Wrong OTP!')
                        return HttpResponseRedirect('/customer/pass_otp_mail/')
                except:
                    messages.error(request, "Something Went Wrong")
                    return HttpResponseRedirect('/customer/pass_otp_mail/')
        else:
            otp_form = Customer_OTP_Form()
        return render(request, "customer/customer_otp.html", {'otp_form': otp_form})


@transaction.atomic()
def customer_reset_pass(request, id):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer/home/')
    else:
        if request.method == "POST":
            pass_reset_form = CustomerResetPassChangeForm(request.POST)
            if pass_reset_form.is_valid():
                new_pass = pass_reset_form.cleaned_data['newpassword1']
                customer_obj = Customer.objects.get(id=id)
                customer_obj.set_password(new_pass)
                customer_obj.save()
                messages.success(request, "Password Updated!")
                return HttpResponseRedirect('/customer/login/')
        else:
            pass_reset_form = CustomerResetPassChangeForm()
        return render(request, 'customer/reset_pass.html', {'pass_reset_form': pass_reset_form})

def reservation_deleting_confirmation(request,reservation_id):
    if request.user.is_authenticated:
        print("Reservation Id : ",reservation_id)
        return render(request,'customer/reservation_deleting_confirm.html/',{'reservation_id':reservation_id})
    else:
        return HttpResponseRedirect('/customer/login/')

def delete_reservation(request,reservation_id):
    if request.user.is_authenticated:
        reservation_obj = Room_Reservation.objects.get(id=reservation_id)
        reservation_obj.delete()
        messages.success(request,f"Reservation is delete of {reservation_obj.seller.hotel_name} hotel room number {reservation_obj.room_number}")
        return HttpResponseRedirect('/customer/home/')
    else:
        return HttpResponseRedirect('customer/login/')