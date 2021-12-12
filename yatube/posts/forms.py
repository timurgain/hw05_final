from django.core.exceptions import ValidationError
from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)

    def clean_text(self):
        if self.cleaned_data['text'] == '':
            raise ValidationError(message='Пост не может быть пустым')
        return self.cleaned_data['text']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
