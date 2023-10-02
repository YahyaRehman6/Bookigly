import rest_framework.generics

from .serializer import *
from accounts.models import *
from accounts.models import User as Customer
from accounts.models import User as Seller
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from .tasks import sending_otp_mail_api_task
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate,logout,login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .renderer import *
from rest_framework.decorators import renderer_classes
def get_tokens_for_user(user):
    """
    generate access and refresh tokens for user
    """
    tokens = RefreshToken.for_user(user)
    return {
        'refresh_token': str(tokens),
        'access_token': str(tokens.access_token)
    }


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class Customer_Creation_View(APIView):
    @csrf_exempt
    def post(self, request):
        serializer = Customer_Serializers(data=request.data)
        if serializer.is_valid():

            username = serializer.data['username']
            email = serializer.data['email']
            phone = serializer.data['phone_number']
            password = serializer.data['password1']
            f_name = serializer.data['first_name']
            l_name = serializer.data['last_name']

            otp = random.randint(100000, 999999)
            customer = Customer(
                username = username,
                email=email,
                phone_number = phone,
                first_name = f_name,
                last_name = l_name,
                otp=otp
            )
            customer.set_password(password)
            customer.save()
            # sending_otp_mail_api_task.delay(
            #     username=username,
            #     otp=otp,
            #     email=email
            # )
            return Response({"msg": 'Account Created Please Verify your Account', 'Customer': serializer.data})


        return Response({"msg": serializer.errors})

    renderer_classes = [Customer_Renderer]

@api_view(['POST'])
@renderer_classes([Customer_Renderer])
def Customer_OTP_Verification(request, username):
    try:
        data = request.data
        print("data")
        serializer = Customer_OTP_Verification_Serializer(data=data)
        if serializer.is_valid():
            customer_otp = Customer.objects.get(username=username).otp
            if serializer.data['otp'] == customer_otp:
                customer = Customer.objects.get(username=username)
                customer.is_verified = True
                customer.save()
                return Response({'message': "Otp Verified"})

            else:
                return Response({'error': "Wrong Otp"})

        else:
            return Response({'error': serializer.errors})

    except Exception as e:
        return Response({'error': str(e)})






class Customer_Login_API(APIView):
    renderer_classes = [Customer_Renderer]
    def post(self, request):
        try:
            serializer = Customer_Login_Serializer(data=request.data)
            if serializer.is_valid():
                print(serializer)
                username = serializer.data['username']
                password = serializer.data['password']
                customer = authenticate(
                    username=username,
                    password=password
                )

                seller_obj = Customer.objects.get(username=username).is_seller
                customer_verified_or_not = Customer.objects.get(username=username).is_verified

                if customer is not None:
                    if (not seller_obj) and customer_verified_or_not:
                        login(request,customer)
                        tokens = get_tokens_for_user(customer)
                        return Response({"message": "successfully logged-in", 'tokens': tokens})
                else:
                    return Response({'error': "Unauthenticated User"}, status=401)
            else:
                return Response(serializer.errors)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class Hotel_View(APIView):
    renderer_classes = [Customer_Renderer]
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        hotels = Seller.objects.filter(is_seller=True, is_verified=True)
        serializer = Hotel_Serializer(hotels, many=True)
        hotel_images = Hotel_Images.objects.all()
        hotel_image_serializer = Hotel_Image_Serializer(hotel_images, many=True)
        return Response({"hotel": serializer.data, "hotel images": hotel_image_serializer.data})


class Hotel_Room_View(APIView):
    renderer_classes = [Customer_Renderer]
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request,seller_id):
        seller = User.objects.filter(id=seller_id,is_seller=True).exists()
        if seller:
            rooms = Room.objects.filter(seller_id=seller_id)
            room_amenities = Room_Amenities.objects.filter(seller_id=seller_id)
            room_images = Room_Images.objects.filter(seller_id=seller_id)

            room_serializer = Hotel_Room_Serializer(rooms, many=True)
            amenities_serializer = Hotel_Room_Amenities_Serializer(room_amenities, many=True)
            room_images_serializer = Hotel_Room_Images_Serializer(room_images, many=True)

            return Response(
                {
                    "Rooms": room_serializer.data,
                    "Room Amenities": amenities_serializer.data,
                    "Room Images": room_images_serializer.data
                }
            )
        else:
            return Response("Something wrong")
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,RetrieveDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated



class Room_Reservation_View_LC(ListCreateAPIView):
    def get_queryset(self):
        customer_username = self.kwargs['customer_username']
        customer = Customer.objects.filter(username=customer_username).exists()
        if customer:
            queryset = Room_Reservation.objects.filter(username=customer_username)
            return queryset
        else:
            return None

    serializer_class = Room_Reservation_Serializer
    renderer_classes = [Customer_Renderer]
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            response = {}
            return Response(response)
        serializer = self.serializer_class(queryset,many=True)
        response = {'reservations':serializer.data}
        return Response(response)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response = {'reservation':serializer.data}
        return Response(response)
    
    
class Room_Reservation_View_RD(RetrieveDestroyAPIView):
    def get_queryset(self):
        customer_username = self.kwargs['customer_username']
        queryset = Room_Reservation.objects.filter(username=customer_username)
        return queryset

    renderer_classes = [Customer_Renderer]
    serializer_class = Room_Reservation_Serializer
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        return Response({'reservation':serializer.data})
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response = {'message':"reservation deleted"}
        return Response(response)





