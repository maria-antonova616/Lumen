from django import forms
from django.core.exceptions import ValidationError
from .models import ClientChoice, Gallery, GalleryInvite
from users.models import CustomUser
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class GallerySettingsForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = [
            'title', 'expires_at', 'total_selection_limit', 'max_selection_count', 'is_active',
            'is_common_likes', 'clients_see_others', 'viewers_see_likes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none focus:ring-2 focus:ring-white'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none focus:ring-2 focus:ring-white', 'type': 'datetime-local'}),
            'total_selection_limit': forms.NumberInput(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none focus:ring-2 focus:ring-white'}),
            'max_selection_count': forms.NumberInput(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none focus:ring-2 focus:ring-white'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'is_common_likes': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'clients_see_others': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'viewers_see_likes': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }
        labels = {
            'is_common_likes': 'Включить режим "Общие лайки"',
            'clients_see_others': 'Клиенты видят лайки друг друга',
            'viewers_see_likes': 'Зрители видят счетчик лайков'
        }
class GalleryAccessForm(forms.ModelForm):
    users_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Gallery
        fields = ['is_public']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }
class InviteCreateForm(forms.ModelForm):
    class Meta:
        model = GalleryInvite
        fields = ['role', 'usage_limit']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'w-full bg-white text-black border border-gray-300 p-2.5 rounded-sm focus:outline-none'})
        }
class PhotoUploadForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'hidden', 'id': 'file-upload', 'accept': 'image/*'}),
        label="Фотографии", required=True
    )
class ClientChoiceForm(forms.ModelForm):
    class Meta:
        model = ClientChoice
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'w-full bg-white text-black border border-gray-300 p-2 rounded-sm', 'placeholder': 'Например: кадрировать...'})
        }
