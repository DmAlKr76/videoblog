from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings


# Подписка
class Subscribe(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created',)

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)


# Пользователь
class User(AbstractUser):
    following = models.ManyToManyField('self', through=Subscribe, related_name='followers', symmetrical=False)
    ignore = models.BooleanField('Бан', default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# Динамически добавляем поля в модель
User.add_to_class('following', models.ManyToManyField('self', through=Subscribe, related_name='followers'))


# Профиль пользователя
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField('Аватар', upload_to='video/avatar/%Y/%m/%d/', null=True, blank=True)
    birthdate = models.DateField('День рождения', blank=True, null=True)

    def __str__(self):
        return "Профиль пользователя %s" % self.user

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


# Видеоконтент
class Video(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='video_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video = models.FileField(upload_to='media/%Y/%m/%d/')
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    url = models.URLField()
    created = models.DateField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='video_liked', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Video, self).save(*args, **kwargs)

    def __str__(self):
        return self.title, self.created, self.users_like

    class Meta:
        verbose_name = 'Видео'
        ordering = ('-created',)


# Комментарии
class Comment(models.Model):
    comment_of_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Комментарии пользователя')
    comment_to_video = models.ForeignKey(Video, on_delete=models.CASCADE, verbose_name='Комментарии к публикации')
    comment_text = models.CharField('Текст комментария', max_length=255)
    comment_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.comment_of_user, self.comment_created

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-comment_created',)
