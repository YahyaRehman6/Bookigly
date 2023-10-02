from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(User)
class User_Admin(admin.ModelAdmin):
    list_display = ['id','username','email','phone_number','is_seller','is_verified']

@admin.register(Hotel_Images)
class room_admin(admin.ModelAdmin):
    list_display = ['id','seller','image']

@admin.register(Room)
class room_admin(admin.ModelAdmin):
    list_display = ['id','room_number','seller','created_at']

@admin.register(Room_Amenities)
class room_admin(admin.ModelAdmin):
    list_display = ['id','amenity','room',"seller"]

@admin.register(Room_Images)
class room_admin(admin.ModelAdmin):
    list_display = ['id','room','image',"seller"]

@admin.register(Room_Reservation)
class reservation_admin(admin.ModelAdmin):
    list_display = ['id',"username","room_number","email",'check_in_date',"check_out_date","is_accepted"]
