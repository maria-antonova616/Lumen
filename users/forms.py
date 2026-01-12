from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full bg-white text-black border border-gray-300 rounded-sm p-3 focus:outline-none focus:border-white focus:ring-2 focus:ring-gray-500 placeholder-gray-500 text-sm font-bold',
                'placeholder': self.fields[field_name].label
            })
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full bg-white text-black border border-gray-300 rounded-sm p-3 focus:outline-none focus:border-white focus:ring-2 focus:ring-gray-500 placeholder-gray-500 text-sm font-bold',
        'placeholder': 'Имя пользователя'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-white text-black border border-gray-300 rounded-sm p-3 focus:outline-none focus:border-white focus:ring-2 focus:ring-gray-500 placeholder-gray-500 text-sm font-bold',
        'placeholder': 'Пароль'
    }))
