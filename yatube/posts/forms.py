from django import forms
from django.core.validators import ValidationError

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise ValidationError('Введите текст!')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(),
            }
        labels = {
            'text': 'Текст'}
