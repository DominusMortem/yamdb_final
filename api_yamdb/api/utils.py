from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def generate_confirmation_code(user):
    return default_token_generator.make_token(user)


def authenticate(confirmation_code, user):
    return default_token_generator.check_token(user, confirmation_code)


def send_email(user):
    confirmation_code = generate_confirmation_code(user)
    email = EmailMessage(
        'Authorization',
        f"Имя пользователя: {user}\n"
        f"Код подтверждения: {confirmation_code}",
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    email.send()
