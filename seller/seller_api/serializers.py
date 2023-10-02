from accounts.models import User as Seller
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from accounts.models import *
class Seller_Serializers(ModelSerializer):
    """
    Seller Sign-up Serializer class , it also check validation
    in this we override password1 field of Seller(User as Seller) because we don't want override
    then we cant validate both password because Seller(User as Seller) don't have password2 field
    """
    password1 = serializers.CharField(style={'input_type': 'password'})
    password2 = serializers.CharField(style={'input_type': 'password'})
    class Meta:
        model = Seller
        fields = ["id",'hotel_name','username','email','phone_number','hotel_address','password1','password2']

    def validate(self,data):
        pass1 = data.get('password1')
        pass2 = data.get('password2')
        if pass1 != pass2:
            raise serializers.ValidationError("Passwords don't match")
        return data

class seller_otp_serializer(serializers.Serializer):
    # seller otp verification
    otp = serializers.IntegerField()


class seller_forget_password_otp_mail_serializer(serializers.Serializer):
    """
    Getting email and check validation and verification of it
    """
    email = serializers.EmailField(max_length=225)

    def validate_email(self,value):
        verification = Seller.objects.filter(email=value,is_seller=True).exists()
        if not verification:
            raise ValidationError("Email does not exist")
        return value


class Seller_Forget_Password_Serialzier(serializers.Serializer):
    """
    After verification of token seller will access this
    """
    password1 = serializers.CharField(style={'input-type':'password'})
    password2 = serializers.CharField(style={'input-type':'password'})

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        if password1 != password2 :
            raise ValidationError("Password Does not match")

        return attrs



class Seller_Login_Serializer(serializers.ModelSerializer):
    """
    Login Serializer Class for Seller
    """
    username = serializers.CharField()
    class Meta:
        model = Seller
        fields = ['username','password']

    def validate_username(self,value):
        seller_obj = Seller.objects.filter(username=value).exists()
        if not seller_obj:
            raise ValidationError("No User is Found with this username")
        return value


class Seller_Retrieve_Update_Destroy_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['hotel_name','username','email','phone_number','hotel_address']


class Seller_Change_Password_With_Old_Password_Serializer(serializers.Serializer):
    username = serializers.CharField()
    old_password = serializers.CharField(style={'input-type':'password'})
    new_password1 = serializers.CharField(style={'input-type': 'password'})
    new_password2 = serializers.CharField(style={'input-type': 'password'})

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')
        username = attrs.get('username')

        seller_obj = Seller.objects.get(username=username)
        check_password_verification = check_password(old_password,seller_obj.password)

        if not check_password_verification:
            raise ValidationError("Old Password Does not Match")

        if new_password1 != new_password2:
            raise ValidationError("Password Does Not Match")

        return attrs

class Hotel_Images_Serializer(serializers.ModelSerializer):
    """
    Serializer Class For Seller Hotel
    """
    class Meta:
        model = Hotel_Images
        fields = ['id','seller','image']


class Room_Serializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", 'seller', 'room_number']

    def validate(self, attrs):
        try:
            seller_id = attrs.get('seller')
            room_number = attrs.get('room_number')
            existance = Room.objects.filter(seller=seller_id, room_number=room_number).exists()
            print("Checking Existance : ",existance)
            if existance:
                raise ValidationError("Room is already exists")
            return attrs
        except Exception as e:
            raise ValidationError(str(e))


class Room_Images_Serializer(ModelSerializer):
    class Meta:
        model = Room_Images
        fields = ['id','seller','room','image']


class Room_Amenities_Serializer(ModelSerializer):
    class Meta:
        model = Room_Amenities
        fields = ['id', 'seller', "room", 'amenity']

    def validate(self, attrs):
        seller_id = attrs.get('seller')
        room_id = attrs.get('room')
        amenity = attrs.get('amenity')
        existance = Room_Amenities.objects.filter(
            seller=seller_id,
            room=room_id,
            amenity=amenity
        ).exists()

        if existance:
            raise ValidationError("Emenity already exist")
        return attrs


class Pending_Room_Reservations_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Reservation
        fields = ['id','seller','room','room_number','name','username','email','phone_number','check_in_date','check_out_date','is_accepted']

class Accept_Resevation_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Reservation
        fields = ['id','seller','room','is_accepted']
