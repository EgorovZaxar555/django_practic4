from django import forms
from django.core.validators import FileExtensionValidator

from .models import Student, Group

MAX_MB = 5

def validate_filesize(file):
    if file.size > MAX_MB * 1024 * 1024:
        raise forms.ValidationError(f"Размер файла не должен превышать {MAX_MB} МБ")


class StudentAvatarForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["avatar"]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*"})
        }
        help_texts = {"avatar": "Загрузите изображение (JPEG/PNG), до 5 МБ"}

    avatar = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
            validate_filesize
        ],
        label="Аватар"
    )


class StudentFilterForm(forms.Form):
    surname = forms.CharField(
        label="Часть фамилии",
        required=False,
    )
    group = forms.ModelChoiceField(
        label="Группа",
        queryset=Group.objects.all(),
        required=False,
    )
    group_name = forms.CharField(
        label="Часть названия группы",
        required=False,
    )