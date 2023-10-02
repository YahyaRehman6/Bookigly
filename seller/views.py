from django.shortcuts import render
from .forms import *
from accounts.models import User as Seller
from .tasks import *
from django.http import HttpResponse ,HttpResponseRedirect
from django.contrib import messages
import uuid
import random
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
# Create your views here.

@transaction.atomic()
def SellerCreation(request):
    """
    creating a function for sing-up
    """
    try:

        if request.method == "POST":
            detail = SellerCreationForm(request.POST)

            if detail.is_valid():
                token = str(uuid.uuid4())
                hotel_name = detail.cleaned_data['hotel_name']
                username = detail.cleaned_data['username']
                email = detail.cleaned_data['email']
                phone_number = detail.cleaned_data['phone_number']
                password = request.POST.get('password1')
                address = detail.cleaned_data['hotel_address']

                seller = Seller(
                    hotel_name=hotel_name,
                    username = username,
                    email = email,
                    phone_number=phone_number,
                    hotel_address = address,
                    is_seller = True,
                    token=token
                )

                seller.set_password(password)
                seller.save()
                sending_mail_token.delay(
                    username=username,
                    email = email,
                    token = token
                )

                return HttpResponse("Check Mail")

            else:
                messages.error(request, "Invalid Information")

        else:
            detail = SellerCreationForm()

        return render(request, "seller/signup.html", {'detail': detail})

    except Exception as e:
        return HttpResponse(f"Something Went Wrong , and error is \n {str(e)}")



def Gmail_Token_Verification(request, token, username):
    """
    In this we verify the seller and make is_seller True if the correct token is hittrd by seller
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        try:
            seller_obj = Seller.objects.get(username=username)
            seller_token = seller_obj.token
            if seller_token == token:
                seller_obj.is_verified = True
                seller_obj.save()
                messages.success(request, "Your Verification is Complete now you can login")
                return HttpResponseRedirect('/seller/login/')
            else:
                return HttpResponse("Invalid Token")
        except Exception as e:
            return HttpResponse(str(e))
    else:
        return HttpResponseRedirect('/seller/login/')


def seller_forgot_password_mail(request):
    """
    In this function we send a otp to that email which user entered for forgot password , if valid
    """

    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/seller/home/')

    else:

        if request.method == "POST":
            password_form = Seller_Forgot_Password_Mail_Form(request.POST)

            if password_form.is_valid():
                mail = password_form.cleaned_data['email']
                seller_obj = Seller.objects.get(email=mail)
                otp = random.randint(100000, 999999)
                seller_obj.otp = otp
                seller_obj.save()
                sending_mail_otp.delay(
                    username = seller_obj.username,
                    email = mail,
                    otp = otp
                )
                return HttpResponseRedirect(f'/seller/otp_verification/{seller_obj.id}/')

        else:
            password_form = Seller_Forgot_Password_Mail_Form()

        return render(request, "seller/forgot_pass.html", {'password_form': password_form})


def seller_forgot_password_otp_verification(request,id):
    """
    In this we get seller id and verify the token , if valid then redirect to reset password form
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/seller/home/')

    else:

        if request.method == "POST":
            otp_form = Seller_OTP_Form(request.POST)

            if otp_form.is_valid():
                otp = otp_form.cleaned_data['otp']
                print("entered otp : ",otp)

                try:
                    seller_obj = Seller.objects.get(id = id)

                    if otp == seller_obj.otp:
                        seller_obj.otp = 0
                        seller_obj.save()
                        return HttpResponseRedirect(f'/seller/reset_password/{id}/')

                    else:
                        messages.error(request, 'Wrong OTP!')
                        return HttpResponseRedirect(f'/seller/otp_verification/{id}/')

                except Exception as e :
                    return HttpResponse(f"Something Went Wrong , and error is \n {str(e)}")
                    # return HttpResponseRedirect('/seller/forgot_pass_mail/')

        else:
            otp_form = Seller_OTP_Form()
        return render(request,"seller/seller_otp.html",{'otp_form':otp_form})


def seller_reset_pass(request,id):
    """
    Find object and update his password
    """

    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/customer/home/')

    else:

        try:

            if request.method == "POST":
                pass_reset_form = SellerResetPassChangeForm(request.POST)

                if pass_reset_form.is_valid():
                    new_pass = pass_reset_form.cleaned_data['newpassword1']
                    seller_obj = Seller.objects.get(id=id,is_seller=True)
                    seller_obj.set_password(new_pass)
                    seller_obj.save()
                    messages.success(request,"Password Updated!")
                    return HttpResponseRedirect('/seller/login/')

            else:
                pass_reset_form = SellerResetPassChangeForm()

            return render(request,'seller/reset_password.html',{'pass_reset_form':pass_reset_form})

        except Exception as e:
            return HttpResponse(f"Something Went Wrong , and error is \n {str(e)}")


def SellerLogin(request):
    """
    For Seller Login
    """

    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/seller/home/')

    else:

        if request.method == "POST":
            form = AuthenticationForm(request=request,data=request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                obj = authenticate(username=username,password=password)
                user = Seller.objects.get(username=username)
                user_verification = Seller.objects.get(username=username).is_verified

                if (user.is_seller == True) and (obj is not None) and (user_verification) and (user.is_seller==True):
                    login(request,obj)
                    return HttpResponseRedirect('/seller/home/')

                else:
                 messages.error(request,"Invalid Information")

            else:
                 messages.error(request,"Invalid Information")

        else:
            form = AuthenticationForm()

        return render(request,"seller/login.html",{'form':form})


def home(request):
    """
    Seller Home Page
    """

    if (request.user.is_authenticated) and (request.user.is_seller):

        seller = request.user
        seller_object = Seller.objects.get(username=seller)
        hotel_for_noti = Seller.objects.get(username=seller).username
        reservations = Room_Reservation.objects.filter(seller=seller_object)
        return render(request,'seller/home.html',{'seller':seller,'reservations':reservations,'hotel':hotel_for_noti})

    else:
        return HttpResponseRedirect('/seller/login/')


def seller_logout(request):
    """
    simple function which logout the current user
    """
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect("/seller/login/")

    else:
        return HttpResponseRedirect("/seller/login/")




def SellerChange(request):
    """
    with this seller change his hotal and hotel information
    """
    if (request.user.is_authenticated) and (request.user.is_seller):

        if request.method == "POST":
            detail = SellerChangeForm(request.POST , instance=request.user)

            if detail.is_valid():
                detail.save()
                messages.success(request,"Information Updated!!!")
                return HttpResponseRedirect('/seller/home/')

        else:
            detail = SellerChangeForm(instance=request.user)

        return render(request,'seller/seller_changed.html',{'detail':detail})

    else:
        return HttpResponseRedirect('/seller/login/')



def Change_Password(request):
    """
    This is use to change password of seller account with old password
    """
    if (request.user.is_authenticated) and (request.user.is_seller):

        if request.method == "POST":
            detail = PasswordChangeForm(data=request.POST,user=request.user)

            if detail.is_valid():
                detail.save()
                messages.success(request,"Password Updated !!!")

            else:
                messages.error(request,"Invalid Password")

        else:
            detail = PasswordChangeForm(user=request.user)

        return render(request,"seller/password_change.html",{'detail':detail})

    else:
        return HttpResponseRedirect("/seller/login/")



def Add_Hotel_Image(request):
    """
    this logic will use to save the images of hotel but in end we pass all
    images of hotel of current hotel
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        seller = Seller.objects.get(username=request.user)
        # seller is use to save image with seller.id

        if request.method == "POST":
            detail = HotelImagesForm(request.POST, request.FILES)

            if detail.is_valid():
                image = detail.cleaned_data['image']
                image_obj = Hotel_Images(seller_id=seller.id, image=image)
                image_obj.save()
                messages.success(request, 'Image is saved')
                return HttpResponseRedirect('/seller/add_hotel_image/')

        else:
            detail = HotelImagesForm()

        all_images = Hotel_Images.objects.filter(seller_id=seller.id)

        return render(request, "seller/add_hotel_image.html", {'detail': detail, "images": all_images})

    else:
        return HttpResponseRedirect('/seller/login/')



def conirm_delete(request, id):
    """
    it render a template which consist delete button , when client
    press this it hit url with that id which is passed in context
    and after that hotel_image_delete function will executed
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        return render(request, "seller/confirmation_for_delete.html", {'id': id, "hotel": True})
    else:
        return HttpResponseRedirect('/seller/login/')


def hotel_image_delete(request, id):
    """
    this delete the image whose id is given
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        image = Hotel_Images.objects.get(id=id)
        image.delete()
        messages.success(request, 'Image is deleted')
        return HttpResponseRedirect('/seller/add_hotel_image/')

    else:
        return HttpResponseRedirect('/seller/login/')


def adding_room(request):
    """
    add a room if the room is already exist then we give a message that room is alredy exist
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        user = Seller.objects.get(username=request.user)

        if request.method == "POST":
            detail = RoomCreationForm(request.POST)

            if detail.is_valid():
                room_no = detail.cleaned_data['room_number']
                room = Room.objects.filter(seller_id=user.id,room_number=room_no)

                if room.exists():
                    messages.error(request,"room number already exists")
                    return HttpResponseRedirect(f'/seller/adding_room/')

                else:
                    room_object = Room(seller_id=user.id,room_number=room_no)
                    room_object.save()
                    room_id = Room.objects.get(Q(room_number=room_no) & Q(seller_id=user.id)).id
                    return HttpResponseRedirect(f'/seller/room_detail/{user.id}/{room_id}/')

        else:
            detail = RoomCreationForm()

        return render(request,"seller/adding_room.html",{'detail':detail})

    else:
        return HttpResponseRedirect('/seller/login/')


def room_detail(request, seller_id, room_id):
    """
    This function will render all amenities of a room whose room_id is given
    and it provide a function to upload images of that room and delete or edit
    amenities of the room and seller can also delete the room
    """
    # here room_id is the id(serial number) of the room
    if (request.user.is_authenticated) and (request.user.is_seller):

        if request.method == "POST":
            detail = RoomImagesForm(request.POST, request.FILES)
            form = AmenityForm(request.POST)

            if form.is_valid():
                f_amenity = form.cleaned_data['amenity']

                if len(f_amenity):
                    check = Room_Amenities.objects.filter(amenity=f_amenity, seller_id=seller_id, room_id=room_id)

                    if check.exists():
                        messages.warning(request, "Amenity already exist")
                        return HttpResponseRedirect(f'/seller/room_detail/{seller_id}/{room_id}/')

                    else:
                        Room_Amenities.objects.create(room_id=room_id, amenity=f_amenity, seller_id=seller_id)
                        messages.success(request, f"{f_amenity} is added into your hotel amenites")
                        return HttpResponseRedirect(f'/seller/room_detail/{seller_id}/{room_id}/')

            else:
                messages.error(request, "Invalid Information")

            if detail.is_valid():
                url = detail.cleaned_data['image']
                Room_Images.objects.create(
                    image=url,
                    seller_id=seller_id,
                    room_id=room_id
                )
                messages.success(request, 'Image is added')

            else:
                messages.error(request, "invalid file")

        else:
            detail = RoomImagesForm()
            form = AmenityForm()

        room_amenities_objects = Room_Amenities.objects.filter(room_id=room_id, seller_id=seller_id)
        room_number = Room.objects.get(id=room_id).room_number
        Images = Room_Images.objects.filter(seller_id=seller_id, room_id=room_id)

        return render(request, 'seller/room_detail.html', {
            'room_amenities_objects': room_amenities_objects,
            "room": room_number,
            "seller_id": seller_id,
            "detail": detail,
            'images': Images,
            "form": form,
            "room_id": room_id
        })

    else:
        return HttpResponseRedirect('/seller/login/')


def total_rooms(request,seller_id):
    """
    It give the total rooms,created by a seller
    """
    if (request.user.is_authenticated) and (request.user.is_seller):

        seller_id = Seller.objects.get(username=request.user).id
        total_rooms = Room.objects.filter(seller_id=seller_id)
        return render(request,'seller/total_rooms.html',{'rooms':total_rooms,"seller_id":seller_id})

    else:
        return HttpResponseRedirect('/seller/login/')


def confirmation_delete_room_image(request, image_id, seller_id, room_id):
    """
    confirmation of deleting room image
    """
    if (request.user.is_authenticated) and (request.user.is_seller):

        return render(
            request, "seller/confirmation_for_delete.html",
            {
                "room": True, "image_id": image_id, "seller_id": seller_id, "room_id": room_id
            }
        )

    else:
        return HttpResponseRedirect('/seller/login/')


def delete_room_image(request, image_id, seller_id, room_id):
    """
    It delete room image whose image_id is given
    """
    if (request.user.is_authenticated) and (request.user.is_seller):

        try:
            obj = Room_Images.objects.get(id=image_id, seller_id=seller_id, room_id=room_id)
            obj.delete()
            messages.success(request, "Image is deleted")

        except Exception as e:
            messages.error(request, f"error is : {e}")
        return HttpResponseRedirect(f'/seller/room_detail/{seller_id}/{room_id}/')

    else:
        return HttpResponseRedirect('/seller/login/')



def AmenityChange(request,amenity_id,room_id,seller_id):
    """
    it update the value of amenity
    """
    if (request.user.is_authenticated) and (request.user.is_seller):
        instance = Room_Amenities.objects.get(id=amenity_id,room_id=room_id,seller_id=seller_id)

        if request.method == "POST":
            detail = AmenityForm(request.POST,instance=instance)

            if detail.is_valid():
                f_amenity = detail.cleaned_data['amenity']

                if len(f_amenity):
                    # checking that new value of amenity already exits or not
                    check = Room_Amenities.objects.filter(amenity=f_amenity,seller_id=seller_id,room_id=room_id)

                    if check.exists():
                        messages.warning(request,"Amenity already exist")
                        return HttpResponseRedirect(f'/seller/amenity_change/{amenity_id}/{room_id}/{seller_id}/')

                    else:
                        detail.save()
                        messages.success(request,"Amenity Updated")
                        return HttpResponseRedirect(f"/seller/room_detail/{seller_id}/{room_id}/")

            else:
                messages.error("Invlid Information")

        else:
            detail = AmenityForm(instance=instance)
        return render(request,"seller/amenity_change.html",{
            'detail':detail,"room_id":room_id,"seller_id":seller_id,"amenity_id":amenity_id
            })

    else:
        return HttpResponseRedirect('/seller/login/')


def confirmation_amenity_delete(request, amenity_id, room_id, seller_id):
    if (request.user.is_authenticated) and (request.user.is_seller):
        return render(request, "seller/confirmation_for_delete.html", {
            "amenity": True,
            "amenity_id": amenity_id,
            "room_id": room_id,
            "seller_id": seller_id
        })

    else:
        return HttpResponseRedirect("/seller/login/")


def delete_amenity(request, amenity_id, room_id, seller_id):

    if (request.user.is_authenticated) and (request.user.is_seller):

        try:
            amenity_object = Room_Amenities.objects.get(
                id=amenity_id,
                room_id=room_id,
                seller_id=seller_id
            )
            amenity_value = amenity_object.amenity
            amenity_object.delete()
            messages.success(request, f"{amenity_value} Deleted")

        except Exception as e:
            messages.error(request, f"Error is : {e}")

        return HttpResponseRedirect(
            f'/seller/room_detail/{seller_id}/{room_id}/'
        )

    else:
        return HttpResponseRedirect('/seller/login/')


def seller_forgot_password_mail(request):
    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/seller/home/')

    else:

        if request.method == "POST":
            password_form = Seller_Forgot_Password_Mail_Form(request.POST)

            if password_form.is_valid():
                mail = password_form.cleaned_data['email']
                seller_obj = Seller.objects.get(email=mail)
                otp = random.randint(100000, 999999)
                seller_obj.otp = otp
                print(otp)
                seller_obj.save()

                sending_seller_forgot_password_otp_mail.delay(otp,mail)

                return HttpResponseRedirect(f'/seller/otp_verification/{seller_obj.id}/')

        else:
            password_form = Seller_Forgot_Password_Mail_Form()
        return render(request, "seller/forgot_pass.html", {'password_form': password_form})


def seller_otp_verification(request, id):
    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/seller/home/')

    else:

        if request.method == "POST":
            otp_form = Seller_OTP_Form(request.POST)

            if otp_form.is_valid():
                otp = otp_form.cleaned_data['otp']
                print("entered otp : ", otp)

                try:
                    seller_obj = Seller.objects.get(id=id)

                    if otp == seller_obj.otp:
                        seller_obj.otp = 0
                        seller_obj.save()
                        return HttpResponseRedirect(f'/seller/reset_password/{id}/')

                    else:
                        messages.error(request, 'Wrong OTP!')
                        return HttpResponseRedirect(f'/seller/otp_verification/{id}/')

                except:
                    messages.error(request, "Something Went Wrong")

        else:
            otp_form = Seller_OTP_Form()
        return render(request, "seller/seller_otp.html", {'otp_form': otp_form})


def seller_reset_pass(request, id):
    if (request.user.is_authenticated) and (request.user.is_seller):
        return HttpResponseRedirect('/customer/home/')

    else:

        if request.method == "POST":
            pass_reset_form = SellerResetPassChangeForm(request.POST)

            if pass_reset_form.is_valid():
                new_pass = pass_reset_form.cleaned_data['newpassword1']
                seller_obj = Seller.objects.get(id=id, is_seller=True)
                seller_obj.set_password(new_pass)
                seller_obj.save()
                messages.success(request, "Password Updated!")
                return HttpResponseRedirect('/seller/login/')

        else:
            pass_reset_form = SellerResetPassChangeForm()
        return render(request, 'seller/reset_password.html', {'pass_reset_form': pass_reset_form})


def pending_reservations(request,seller_id):
    if (request.user.is_authenticated) and (request.user.is_seller):
        pending = Room_Reservation.objects.filter(seller_id=seller_id, is_accepted=False)
        return render(request,'seller/pending_reservations.html',{'pending':pending})
    else:
        return HttpResponseRedirect('/seller/login/')

def accept_reservation(request,reservation_id):
    if (request.user.is_authenticated) and (request.user.is_seller):
        reservation_obj = Room_Reservation.objects.get(id=reservation_id)
        reservation_obj.is_accepted = True
        reservation_obj.save()
        return HttpResponseRedirect(f'/seller/pending_reservations/{reservation_obj.seller.id}/')
    else:
        return HttpResponseRedirect('/seller/login/')