from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import User
from .tasks import send_welcome_email_task, deactivate_inactive_sellers

class UserModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="Test",
            role="user",
            is_active=True
        )

    def test_create_user(self):
        self.assertEqual(self.user.email, "user@example.com")
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.role, "user")

    def test_create_seller_triggers_email_task(self):
        # Присваиваем роль seller
        self.user.role = "seller"
        self.user.save()

        # Тестируем, что Celery task можно вызвать без ошибок
        result = send_welcome_email_task.apply(args=[self.user.id])
        self.assertIsNone(result.get())  # функция возвращает None

    def test_deactivate_inactive_seller(self):
        # Создаем продавца, который не заходил 91 день
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
            name="Seller",
            role="seller",
            is_active=True,
        )
        seller.last_login = timezone.now() - timedelta(days=91)
        seller.save()

        # Вызываем задачу деактивации
        deactivate_inactive_sellers()

        seller.refresh_from_db()
        self.assertFalse(seller.is_active)
