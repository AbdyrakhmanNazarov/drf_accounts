from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now

class User(AbstractUser):
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-date_joined",)

    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
        ('seller', 'Продавец'),
    ]

    username = None
    email = models.EmailField("Электронная почта", unique=True)
    name = models.CharField("Имя", max_length=50, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=50, null=True, blank=True)
    phone_number = PhoneNumberField("Номер телефона", null=True, blank=True)
    role = models.CharField("Роль пользователя", choices=ROLE_CHOICES, default="user")
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class OTPVerification(models.Model):
    email = models.EmailField("Электронная почта", null=True, blank=True)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def is_expired(self):
        return (now() - self.created_at).total_seconds() > 300

    def __str__(self):
        return f"{self.email} - {self.code}"
