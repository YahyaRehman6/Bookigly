from accounts.models import User as Customer
from accounts.models import User as Seller
from rest_framework import serializers
from accounts.models import *
import datetime

class Customer_Serializers(serializers.ModelSerializer):
    password1 = serializers.CharField(style={'input_type': 'password'})
    password2 = serializers.CharField(style={'input_type': 'password'})
    class Meta:
        model = Customer
        fields = ['username','first_name','last_name','email','phone_number','password1','password2']

    def validate(self,data):
        pass1 = data.get('password1')
        pass2 = data.get('password2')
        if pass1 != pass2:
            raise serializers.ValidationError("Passwords don't match")
        return data

class Customer_Login_Serializer(serializers.ModelSerializer):
    username = serializers.CharField()
    class Meta:
        model = Customer
        fields = ['username','password']


class Customer_OTP_Verification_Serializer(serializers.Serializer):
    otp = serializers.IntegerField()



class Hotel_Serializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    class Meta:
        model = Seller
        fields=['id','hotel_name', 'hotel_address','phone_number','images']

class Hotel_Image_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel_Images
        fields = ['id','seller','image']


class Hotel_Room_Serializer(serializers.ModelSerializer):
    amenities = serializers.SlugRelatedField(many=True,read_only=True,slug_field='amenity')
    class Meta:
        model = Room
        fields = ['id','seller','room_number','amenities','room_images']

class Hotel_Room_Images_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Images
        fields = ['id','seller','room','image']

class Hotel_Room_Amenities_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Amenities
        fields = ['id','seller','room','amenity']

from django.db.models import Q
class Room_Reservation_Serializer(serializers.ModelSerializer):
    # username = serializers.CharField(read_only=True)
    class Meta:
        model = Room_Reservation
        fields = ['id','seller','room','room_number','name','username','email','phone_number','check_in_date','check_out_date','is_accepted']


    def validate(self,atts):
        current_date = timezone.now().date()
        seller_id = atts.get('seller')
        room_id = atts.get('room')
        check_in_date = atts.get('check_in_date')
        check_out_date = atts.get('check_out_date')

        if check_in_date >= check_out_date:
            raise ValidationError("Check-out date must be greater than the check-in date.")

        if (check_in_date < current_date) or (check_out_date<current_date):
            raise ValidationError("Entered Date must be greater then current date")


        reservation_validation = Room_Reservation.objects.filter(
            Q(seller = seller_id,room_id = room_id,check_in_date__range = (check_in_date,check_out_date))
            | Q(seller = seller_id,room_id = room_id,check_out_date__range = (check_in_date,check_out_date))

        ).exists()

        if (reservation_validation is True):
            raise ValidationError("Reservation already exists")

        return atts


