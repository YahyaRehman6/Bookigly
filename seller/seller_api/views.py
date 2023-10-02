from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import *
import random
import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.response import Response
from accounts.models import User
from .tasks import *
from rest_framework.generics import RetrieveAPIView,CreateAPIView,ListAPIView,DestroyAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView,RetrieveDestroyAPIView,RetrieveUpdateAPIView,ListCreateAPIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate,logout,login
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import renderer_classes
from .renderer import *



def get_tokens_for_user(user):
    tokens = RefreshToken.for_user(user)
    return {
        'refresh_token':str(tokens),
        'access_token':str(tokens.access_token)
    }


@api_view(['POST'])
@transaction.atomic()
@renderer_classes([Seller_Signup_Renderer])
def seller_creation(request):
    data = request.data
    try:
        serializer = Seller_Serializers(data=data)
        if serializer.is_valid():
            username = serializer.data['username']
            hotel_name = serializer.data['hotel_name']
            email = serializer.data['email']
            phone = serializer.data['phone_number']
            address = serializer.data['hotel_address']
            password = serializer.data['password1']
            otp = random.randint(100000,999999)
            seller = User(
                hotel_name=hotel_name,
                username=username,
                email=email,
                phone_number=phone,
                hotel_address=address,
                is_seller=True,
                otp=otp
            )
            seller.set_password(password)
            seller.save()
            sending_otp.delay(
                email=email,
                otp = otp
            )
            return Response({"message":"Account Created please verify it","seller detail":serializer.data})


        return Response(serializer.errors)
    except Exception as e:
        return Response({"error":str(e)});


@api_view(['post'])
# @renderer_classes([Seller_Signup_OTP_Verification_Renderer])
@renderer_classes([Seller_Renderer])
def seller_otp_Verification(request,username):
    """
    In this function we verify the otp which we save in session and create the object if verify
    """
    try:
        data = request.data
        serializer = seller_otp_serializer(data=data)
        if serializer.is_valid():

            seller_obj = Seller.objects.get(username=username)
            seller_otp = seller_obj.otp
            print("seller otp is : ",seller_otp)
            if serializer.data['otp'] == seller_otp:
                seller_obj.is_verified = True
                seller_obj.save()
                return Response({'message':"Otp Verified"})
            else:
                return Response({'otp error':"Wrong Otp"})

        else:
            return Response(serializer.errors)

    except Exception as e:
        return Response({"error":str(e)})

@method_decorator(csrf_exempt,name='dispatch')
class seller_forget_password_otp_mail(APIView):
    """
    generate a token and send it to the seller
    """
    renderer_classes = [Seller_Renderer]
    def post(self,request):

        try:

            serializer = seller_forget_password_otp_mail_serializer(data=request.data)

            if serializer.is_valid():
                otp = random.randint(100000,999999)
                email = serializer.data['email']
                seller_obj = Seller.objects.get(email=email)
                seller_obj.otp = otp
                seller_obj.save()

                # sending task to celery
                sending_token_mail.delay(
                    seller_username=seller_obj.username,
                    email=email,
                    otp = otp
                )

                return Response({"message":f"{seller_obj.username} Check your email "})

            else:
                return Response(serializer.errors)

        except Exception as e:
            return Response({'error':str(e)})


class Forget_Password_OTP_Verificaton(APIView):
    renderer_classes = [Seller_Renderer]
    def post(self,request,seller_username):
        try:
            data = request.data
            serializer = seller_otp_serializer(data=data)
            if serializer.is_valid():

                seller_obj = Seller.objects.get(username=seller_username)
                seller_otp = seller_obj.otp
                print("seller otp is : ", seller_otp)
                if serializer.data['otp'] == seller_otp:
                    seller_obj.is_verified = True
                    seller_obj.save()
                    return Response({'message': "Otp Verified"})
                else:
                    return Response({'otp error': "Wrong Otp"})

            else:
                return Response(serializer.errors)

        except Exception as e:
            return Response({"error": str(e)})


class Seller_Reset_Password(APIView):
    renderer_classes = [Seller_Renderer]
    def post(self,request,seller_username):
        try:
            serializer = Seller_Forget_Password_Serialzier(data=request.data)
            if serializer.is_valid():
                password = serializer.data['password1']
                seller_obj = Seller.objects.get(username=seller_username)
                seller_obj.set_password(password)
                seller_obj.save()
                return Response({'message': "Password is Updated"})
            else:
                return Response(serializer.errors)

        except Exception as e :
            return Response({'error':str(e)})

class Seller_Login(APIView):
    """
    Login View For Seller
    """
    renderer_classes = [Seller_Renderer]
    def post(self,request):
        try:
            data = request.data
            serializer = Seller_Login_Serializer(data=data)
            if serializer.is_valid():
                username = serializer.data['username']
                password = serializer.data['password']
                seller = authenticate(
                    username=username,
                    password=password
                )

                seller_obj = Seller.objects.get(username=username).is_seller
                seller_verified_or_not = Seller.objects.get(username=username).is_verified

                if seller is not None:
                    if (seller_obj) and seller_verified_or_not:
                        login(request, seller)
                        tokens = get_tokens_for_user(seller)
                        return Response({"message": "successfully logged-in", 'tokens': tokens})
                else:
                    return Response({'password':"Wrong Password"})
            else:
                return Response(serializer.errors, status=401)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class Seller_Retrieve_Update_Destroy(RetrieveUpdateDestroyAPIView):
    renderer_classes = [Seller_RUD_Renderer]
    queryset = Seller.objects.filter(is_seller=True,is_verified=True)
    serializer_class = Seller_Retrieve_Update_Destroy_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        response = {'Seller':serializer.data}
        return Response(response)


    def update(self, request, *args, **kwargs):
        # getting the value of partial and set default as True
        partial = self.kwargs.pop('partial',True)
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance,data=request.data,partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = {'Seller': serializer.data,"message":"Updated Successfully"}
        return Response(response)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        response = {"message":f"{instance} Deleted Successfully"}
        return Response(response)



class Seller_Change_Password_With_Old_Password(APIView):
    def post(self,request):
        serializer = Seller_Change_Password_With_Old_Password_Serializer(data=request.data)
        if serializer.is_valid():

            password = serializer.data['new_password1']
            username = serializer.data['username']
            seller_obj = Seller.objects.get(username=username)
            seller_obj.set_password(password)
            seller_obj.save()
            return Response({'message':"Password Changed Successfully Done"})

        else:
            return Response(serializer.errors)

class Hotel_Image_LC(ListCreateAPIView):
    """
    List and Create View for hotel Images
    """

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        queryset = Hotel_Images.objects.filter(seller_id=seller_id)
        seller_obj = Seller.objects.filter(id=seller_id)
        if queryset.exists():
            return queryset
        elif seller_obj.exists():
            return queryset
        else:
            raise NotFound("No user is found with the given id ")

    serializer_class = Hotel_Images_Serializer
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [Hotel_Image_LCRD_Renderer]

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        serializers = self.serializer_class(query_set,many=True)
        response = {'Images':serializers.data}
        return Response(response)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        self.perform_create(serializer)
        response = {"message":"Hotel Image is added","Image":serializer.data}
        return Response(response)


class Hotel_Image_RD(RetrieveDestroyAPIView):
    """
    Retrieve and Destroy View of Seller
    """
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        queryset = Hotel_Images.objects.filter(seller_id=seller_id)

        seller_obj = Seller.objects.filter(id=seller_id)
        if queryset.exists():
            return queryset
        elif seller_obj.exists():
            return queryset
        else:
            raise NotFound("No user is found with ")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        response = {"Image":serializer.data}
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        response = {"message":"Image is Deleted"}
        return Response(response)

    serializer_class = Hotel_Images_Serializer
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [Hotel_Image_LCRD_Renderer]


class Room_View_LC(ListCreateAPIView):
    serializer_class = Room_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [Room_LCRUD_Renderer]

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        seller = Seller.objects.filter(id=seller_id).exists()
        if seller:
            queryset = Room.objects.filter(seller_id=seller_id)
            return queryset
        else:
            return None

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        if query_set is None:
            response = {"error":"Seller Does Not Exist"}
            return Response(response)
        serializer = self.serializer_class(query_set,many=True)
        data = serializer.data
        new_data = {"Rooms":data}
        return Response(new_data)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        print("serializer : ",serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response = {'message':"Room Created"}
        return Response(response)

class Room_View_URD(RetrieveUpdateDestroyAPIView):
    serializer_class = Room_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [Room_LCRUD_Renderer]

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        queryset = Room.objects.filter(seller_id=seller_id)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        response = {'Room':serializer.data}
        return Response(response)




class Room_Images_View_Lc(ListCreateAPIView):
    """
    Room Images List and create api
    """
    serializer_class = Room_Images_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [Room_Images_LCRUD_Renderer]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        seller_id = self.kwargs['seller_id']
        seller = Seller.objects.filter(id=seller_id).exists()
        room = Room_Images.objects.filter(seller_id=seller_id,id=room_id).exists()
        if seller and room:
            queryset = Room_Images.objects.filter(room=room_id, seller=seller_id)
            return queryset
        else:
            return None

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        if query_set is None :
            response = 'Something went wrong'
            return Response(response)
        serializer = self.serializer_class(query_set,many=True)
        data = {"Room Images":serializer.data}
        return Response(data)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        self.perform_create(serializer)
        response = {'message':"Room Image is Added",}
        return Response(response)






class Room_Images_View_RD(RetrieveDestroyAPIView):
    """
    room images retrieve and destroy view
    """
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        seller_id = self.kwargs['seller_id']
        queryset = Room_Images.objects.filter(room=room_id,seller=seller_id)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        response = {"Room Image":serializer.data}
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response = {'message':"Room Image Deleted"}
        return Response(response)

    renderer_classes = [Room_Images_LCRUD_Renderer]
    serializer_class = Room_Images_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]



class Room_Amenities_View_Lc(ListCreateAPIView):
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        room_id = self.kwargs['room_id']
        seller = Seller.objects.filter(id=seller_id).exists()
        room = Room.objects.filter(id=room_id,seller=seller_id).exists()
        if seller and room:
            querset = Room_Amenities.objects.filter(
                seller = seller_id,
                room = room_id
            )
            return querset
        else:
            return None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            response = {'message':"Not Found"}
            return Response(response)
        serializer = self.serializer_class(queryset,many=True)
        response = {"amenities":serializer.data}
        return Response(response)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response = {"amenity":"Amenity is added"}
        return Response(response)

    renderer_classes = [Room_Amenities_LCRUD_Renderer]
    serializer_class = Room_Amenities_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]

class Room_Amenity_View_URD(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        room_id = self.kwargs['room_id']
        querset = Room_Amenities.objects.filter(
            seller = seller_id,
            room = room_id
        )
        return querset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance)
        response = {"amenity":serializer.data}
        return Response(response)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance,data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = {"message":"Amenity Updated",'amenity':serializer.data}
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        """
        passing amenity key to get True in if statment of render method of Room_Amenities_LCRUD_Renderer
        if we dont do this then we have to pass one more value in that if statment
        """
        self.perform_destroy(instance)
        response = {'amenity':"Amenity Deleted"}
        return Response(response)

    renderer_classes = [Room_Amenities_LCRUD_Renderer]
    serializer_class = Room_Amenities_Serializer
    authentication_classes = [BasicAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]



class Pending_Reservations_API(ListAPIView):
    renderer_classes = [Pending_Reservations_LU_Rendrer]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    serializer_class = Pending_Room_Reservations_Serializer
    def get_queryset(self):
        seller_id = self.kwargs.get("seller_id")
        seller = Seller.objects.filter(id=seller_id,is_seller=True).exists()
        if seller:
            query_set = Room_Reservation.objects.filter(seller_id=seller_id,is_accepted=False)
            return query_set
        else:
            return None
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            response = {'message':"User Does Not Exist"}
            return Response(response)
        serializer = self.serializer_class(queryset,many=True)
        response = {"reservations":serializer.data}
        return Response(response)

from rest_framework.generics import UpdateAPIView
class Accept_Reservations(UpdateAPIView):
    renderer_classes = [Pending_Reservations_LU_Rendrer]
    serializer_class = Accept_Resevation_Serializer
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        seller_id = self.kwargs.get("seller_id")
        query_set = Room_Reservation.objects.filter(seller_id=seller_id, is_accepted=False)
        return query_set

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance,data=data,partial=True)
        serializer.is_valid()
        self.perform_update(serializer)
        response = {'message':"Reservation Accepted",'reservation':serializer.data}
        return Response(response)
