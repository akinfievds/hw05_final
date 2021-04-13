from django.forms import ModelForm, Select, Textarea

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Название сообщества',
            'text': 'Содержимое записи',
            'image': 'Изображение записи'
        }
        widgets = {
            'group': Select(attrs={
                'placeholder': 'При необходимости, укажите сообщество'
            }),
            'text': Textarea(attrs={
                'placeholder': 'Текст записи'
            })
        }
        error_messages = {
            'text': {'required': ('Недопустимая длина сообщения')}
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': Textarea(attrs={'placeholder': 'Текст комментария'})
        }
