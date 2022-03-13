from django.forms import ModelForm
from django import forms
from .models import Post, Group, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image',)
        labels = {
            'text': _('Новая запись'),
        }
        help_texts = {
            'group': _('Выберите группу'),
            'text': _('*обязательное поле'),
        }

class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': _('Комментарий')}
        help_texts = {'text': _('Оставьте ваш комментарий')}