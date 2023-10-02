from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
# Create your models here.
def validate_phone_number(value):
    if len(value) < 11:
        raise ValidationError("length of phone number should be greater then 10 and less then 14")
class User(AbstractUser):
    """
    Creating a model with some additiona fields for Sellers
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100,blank=False,null=False,unique=True)
    hotel_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13,unique=True,validators=[validate_phone_number])
    hotel_address = models.CharField(max_length=60)
    is_verified = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    token = models.CharField(unique=True,max_length=256,blank=True,null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    otp = models.IntegerField(unique_for_date="created_at",blank=True,null=True)
    def __str__(self):
        return str(self.username)



class Hotel_Images(models.Model):
    """
    Images of the hotel environment
    """
    seller = models.ForeignKey(User,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to='Media/hotel_images')
    created_at = models.DateField(auto_now_add=True)


class Room(models.Model):
    """
    room detail of a assosiated hotel
    """
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room_number)


class Room_Amenities(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='amenities')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, default=0, related_name='amenities')
    amenity = models.CharField(max_length=30)


class Room_Images(models.Model):
    """
    Images of a each room
    """
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_images')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_images')
    image = models.ImageField(upload_to='Media/room_images')



from django.core.exceptions import ValidationError
from django.utils import timezone




class Room_Reservation(models.Model):
    """
    Room Reservation for customer
    Here username is customer username
    """
    seller = models.ForeignKey(User,on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
    room_number = models.IntegerField()
    name = models.CharField(null=False,max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=50,default=None)
    phone_number = models.CharField(max_length=13,null=False)
    check_in_date = models.DateField(null=False)
    check_out_date = models.DateField(null=False)
    is_accepted = models.BooleanField(default=False)

    def clean_check_out_date(self):
        check_in_date = self.check_in_date
        print("check in date")
        check_out_date = self.check_out_date
        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise ValidationError("Check-out date must be greater than the check-in date.")

        return check_out_date

    def clean_check_in_date(self):
        current_date = timezone.now().date()
        check_in_date = self.check_in_date
        if check_in_date < current_date:
            raise ValidationError("Check in date must be greater then current date")
        return check_in_date
