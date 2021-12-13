from django.contrib.auth import get_user_model
from django.db import models
# from pytils.translit import slugify


User = get_user_model()


class Post(models.Model):
    """Table of posts."""
    text = models.TextField(
        blank=False,  # при True - поле в формах необязательное
                      # тогда его проверит валидатор формы
        verbose_name='Статья',
        help_text='Начни здесь свой шедевр',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        to='Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выбери группу',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Выбери картинку',
    )
    # comments = models.ForeignKey(
    #     to='Comments',
    #     on_delete=models.SET_NULL,
    #     related_name='posts',
    #     blank=True,
    #     null=True,
    # )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self) -> str:
        return self.text[:20]

    # def __str__(self):
    #    preview = self.text[0:50]
    #    date = self.pub_date.date()
    #    return f'{preview}..., автор {self.author}, дата {date}'


class Group(models.Model):
    """Table of groups."""
    title = models.CharField(
        verbose_name='Заголовок', max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Метка ссылки', unique=True,
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title

    # Расширение встроенного метода save(): если поле slug не заполнено -
    # транслитерировать в латиницу содержимое поля text и
    # обрезать до ста знаков
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.text)[:100]
    #     super().save(*args, **kwargs)


class Comment(models.Model):
    """Table of comments under posts."""
    post = models.ForeignKey(
        to='Post', on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        blank=False,
        verbose_name='Комментарий',
        help_text='Оставь здесь комментарий',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        preview = self.text[0:15]
        date = self.created.date()
        return f'{preview}..., автор {self.author}, дата {date}'


class Follow(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Последователь',
    )
    author = models.ForeignKey(
        to=User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user and author can not be equal',
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='user can not subscribe twice',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на автора {self.author}'
