from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .tasks import send_welcome_email_task

@receiver(post_save, sender=User)
def send_welcome_email_to_seller(sender, instance, created, **kwargs):
    """
    Отправка приветственного письма через Celery, когда роль пользователя стала seller.
    """
    if instance.role == "seller" and instance.is_active:
        send_welcome_email_task.delay(instance.id)
