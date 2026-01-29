from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import User

@shared_task
def send_welcome_email_task(user_id):
    """
    Отправка приветственного письма продавцу.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    if user.role != "seller" or not user.is_active:
        return

    send_mail(
        subject="Добро пожаловать на наш сайт!",
        message=(
            f"Здравствуйте, {user.name or user.email}!\n\n"
            "Вы были назначены продавцом на нашем сайте. "
            "С уважением, Администратор."
        ),
        from_email="no-reply@site.com",
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def deactivate_inactive_sellers():
    """
    Деактивирует продавцов, которые не заходили 90 дней, и отправляет email уведомление.
    """
    threshold_date = timezone.now() - timedelta(days=90)
    
    inactive_sellers = User.objects.filter(
        role="seller",
        last_login__lt=threshold_date,
        is_active=True
    )

    for user in inactive_sellers:
        user.is_active = False
        user.save()
        
        send_mail(
            subject="Ваш аккаунт деактивирован",
            message="Вы не заходили 90 дней. Обратитесь к администратору для восстановления.",
            from_email="no-reply@site.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        print(f"User {user.email} deactivated and notified by email")
