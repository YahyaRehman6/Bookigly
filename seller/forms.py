from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from accounts.models import User as Seller
from accounts.models import *
from django.core.exceptions import ValidationError

class SellerCreationForm(UserCreationForm):
    """
    Creating a form to create a account of seller
    """
    class Meta:
        model = Seller
        fields = ['hotel_name','username','email','phone_number','hotel_address']


class Seller_Forgot_Password_Mail_Form(forms.Form):
    """
    In this we get an email and verify that this email (exist or valid) or not
    """

    email = forms.EmailField()

    def clean_email(self):
        mail = self.cleaned_data['email']
        obj = Seller.objects.filter(email=mail, is_seller=True, is_verified=True).exists()
        if not obj:
            raise ValidationError("Email does not exist")
        return mail

class Seller_OTP_Form(forms.Form):
    """
    Get otp from seller
    """
    otp = forms.IntegerField()


class SellerResetPassChangeForm(forms.Form):
    """
    Form for reset password after otp verification form email , and validate it
    """
    newpassword1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    newpassword2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):

        cleaned_date = super().clean()
        pass1 = self.cleaned_data['newpassword1']
        pass2 = self.cleaned_data['newpassword2']

        if pass1 != pass2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_date


class HotelImagesForm(forms.ModelForm):
    class Meta:
        model = Hotel_Images
        fields = ['image']


class SellerChangeForm(UserChangeForm):
    password = None
    class Meta:
        model = Seller
        fields = ['hotel_name','username','email','phone_number','hotel_address']


class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number']

class AmenityForm(forms.ModelForm):
    amenity = forms.CharField(required=False)
    class Meta:
        model = Room_Amenities
        fields = ['amenity']


class RoomImagesForm(forms.ModelForm):
    class Meta:
        model = Room_Images
        fields = ['image']




class Seller_Forgot_Password_Mail_Form(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        mail = self.cleaned_data['email']
        obj = Seller.objects.filter(email=mail, is_seller=True, is_verified=True).exists()
        if not obj:
            raise ValidationError("Email does not exist")
        return mail


class Seller_OTP_Form(forms.Form):
    otp = forms.IntegerField()


class Seller_Reset_Pass_Change_Form(forms.Form):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_date = super().clean()
        pass1 = self.cleaned_data['new_password1']
        pass2 = self.cleaned_data['new_password2']

        if pass1 != pass2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_date



class CheckBox(forms.Form):
    accept = forms.BooleanField()