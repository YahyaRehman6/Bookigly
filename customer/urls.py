from django.urls import path
from .views import *

urlpatterns = [
    path('signin/',Customer_Creation,name='customer_signin'),
    path('token/<slug:token>/<str:username>/',Gmail_Token_Verification,name="customer_verification"),
    path('login/',Customer_Login,name="customer_login"),
    path('home/',Customer_Home,name="customer_home"),
    path('logout/',customer_logout,name="customer_logout"),
    path("edit_info/",Edit_Customer_Information,name="edit_info"),
    path('pass_change/',Customer_Password_Change,name="pass_change"),
    path('hotel_detail/<int:seller_id>/',hotel_detail,name="hotel_detail"),
    path('customer_reservation//<int:seller_id><int:room_id>/<int:room_number>/',
         customer_reservation, name="customer_reservation"),
    path('pass_otp_mail/',customer_forgot_password_mail,name="customer-pass_otp_mail"),
    path('otp_verification/<int:id>/',customer_otp_verification,name="otp_verification"),
    path('reset_password/<int:id>/',customer_reset_pass,name="customr_reset_password"),
    path("total_reservations/",customer_total_reservations,name="total_reservations"),
    path('reservation_deleting_confirmation/<int:reservation_id>/',reservation_deleting_confirmation,name="reservation_deleting_confirm"),
    path('delete_reservation/<int:reservation_id>/',delete_reservation,name="delete_reservation")
]

