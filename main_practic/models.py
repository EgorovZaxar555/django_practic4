import os
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class User(AbstractUser):

    @property
    def is_student(self) -> bool:
        return hasattr(self, 'student_profile')

    @property
    def is_teacher(self) -> bool:
        return hasattr(self, 'teacher_profile')

    def __str__(self):
        return self.get_full_name() or self.username


class Group(models.Model):
    name = models.CharField('Название группы', max_length=100)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.name


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    uid = uuid.uuid4().hex
    today = datetime.now().strftime("%Y/%m/%d")
    return f"avatars/{today}/{uid}{ext}"


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Пользователь',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='students',
        verbose_name='Группа',
    )
    avatar = models.ImageField(upload_to=avatar_upload_to, default='avatars/default.jpg')
    enrollment_year = models.PositiveIntegerField('Год поступления', null=True, blank=True)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'Студент: {self.user.username}'


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name='Пользователь',
    )
    department = models.CharField('Кафедра', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return f'Преподаватель: {self.user.username}'


def _delete_file(path):
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass


@receiver(post_delete, sender=Student)
def _student_avatar_delete_file(sender, instance, **kwargs):
    if instance.avatar and instance.avatar.name != "avatars/default.jpg":
        _delete_file(instance.avatar.path)


@receiver(pre_save, sender=Student)
def _student_avatar_replace_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Student.objects.get(pk=instance.pk)
    except Student.DoesNotExist:
        return
    new_file = instance.avatar
    if old.avatar and old.avatar != new_file and old.avatar.name != "avatars/default.jpg":
        _delete_file(old.avatar.path)