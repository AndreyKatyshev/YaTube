# from xml.etree.ElementTree import Comment
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст записи',
            'group': 'Группа',
            'image': 'лейбл картинка'
        }
        help_texts = {
            'text': 'Введите сюда то чем хотите поделиться с миром',
            'group': 'выбирите группу, но это не обязательно',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'лейбл Текст комментария'}
        help_texts = {'text': 'Напишите свой комментарий'}
