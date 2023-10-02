from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from accounts.models import User as Customer
from accounts.models import Room_Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ["username",'email','first_name','last_name','phone_number']


class CustomerChangeForm(UserChangeForm):
    password = None
    class Meta:
        model = Customer
        fields = ["username",'email','first_name','last_name','phone_number']


class Room_Reservation_Form(forms.ModelForm):
    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Room_Reservation
        fields = ["name", "phone_number", 'check_in_date', "check_out_date"]

    def clean_check_out_date(self):
        check_in_date = self.cleaned_data.get('check_in_date')
        check_out_date = self.cleaned_data.get('check_out_date')
        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise ValidationError("Check-out date must be greater than the check-in date.")

        return check_out_date

    def clean_check_in_date(self):
        current_date = timezone.now().date()
        check_in_date = self.cleaned_data.get('check_in_date')
        if check_in_date < current_date:
            raise ValidationError("Check in date must be greater then current date")
        return check_in_date


class Customer_Forgot_Password_mail_Form(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        mail = self.cleaned_data['email']
        obj = Customer.objects.filter(email=mail, is_seller=False, is_verified=True).exists()
        if not obj:
            raise ValidationError("Email does not exist")
        return mail


class Customer_OTP_Form(forms.Form):
    otp = forms.IntegerField()


class CustomerResetPassChangeForm(forms.Form):
    newpassword1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    newpassword2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_date = super().clean()
        pass1 = self.cleaned_data['newpassword1']
        pass2 = self.cleaned_data['newpassword2']

        if pass1 != pass2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_date
