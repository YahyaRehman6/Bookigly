from .views import  *
from django.urls import path

urlpatterns = [
    path('signup/',seller_creation),
    path('otp_verification/<str:username>/',seller_otp_Verification),
    path('seller_forget_pass_mail/',seller_forget_password_otp_mail.as_view()),
    path('verify_password_otp/<str:seller_username>/',Forget_Password_OTP_Verificaton.as_view()),
    path('forget_password/<str:seller_username>/',Seller_Reset_Password.as_view()),
    path('seller_login/',Seller_Login.as_view()),
    path('seller_rud/<int:pk>/',Seller_Retrieve_Update_Destroy.as_view()),
    path('seller_password_change/',Seller_Change_Password_With_Old_Password.as_view()),
    path('hotel_image_rd/<int:seller_id>/<int:pk>/',Hotel_Image_RD.as_view()),
    path('hotel_image_lc/<int:seller_id>/', Hotel_Image_LC.as_view()),
    path('room_lc/<int:seller_id>/',Room_View_LC.as_view()),
    path('room_urd/<int:seller_id>/<int:pk>/',Room_View_URD.as_view()),
    path('room_images_lc/<int:seller_id>/<int:room_id>/', Room_Images_View_Lc.as_view()),
    path('room_images_rd/<int:seller_id>/<int:room_id>/<int:pk>/',
         Room_Images_View_RD.as_view()),
    path('room_amenities_lc/<int:seller_id>/<int:room_id>/',
         Room_Amenities_View_Lc.as_view()),
    path('room_amenities_urd/<int:seller_id>/<int:room_id>/<int:pk>/',
         Room_Amenity_View_URD.as_view()),
    path('pending_reservations/<int:seller_id>/',Pending_Reservations_API.as_view()),
    path('accept_reservations/<int:seller_id>/<int:pk>/',Accept_Reservations.as_view())


]