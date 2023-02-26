from django import forms
from .models import Post

# https://postimg.cc/LJ71v78k - скриншот дебагера


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ("text", "group")

        labels = {
            "text": "Текст поста",
            "group": "Группа",
        }
