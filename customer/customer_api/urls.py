from django.urls import path
from .views import *
urlpatterns = [
    path('customer_creation/',Customer_Creation_View.as_view()),
    path('customer_otp_verification/<str:username>/',Customer_OTP_Verification),
    path('customer_login/',Customer_Login_API.as_view()),
    path('hotels/',Hotel_View.as_view()),
    path('rooms/<int:seller_id>/',Hotel_Room_View.as_view()),
    path('reservation_lc/<str:customer_username>/',Room_Reservation_View_LC.as_view()),
    path('reservation_rd/<str:customer_username>/<int:pk>/',Room_Reservation_View_RD.as_view())
]