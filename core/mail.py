from datetime import date
from django.core.mail import send_mail
from django.conf import settings

def send_password_reset_email(request, first_name, email, token):
    subject = 'Smart Watering'
    link = request.build_absolute_uri('/reset-password/') + token + '/'
    current_year = date.today().year
    expiration_time = settings.PASSWORD_RESET_TOKEN_EXPIRATION

    if expiration_time >= 60:
        expiration_time = settings.PASSWORD_RESET_TOKEN_EXPIRATION // 60

        if expiration_time == 1:
            expiration_time = f'{expiration_time} minuto'
        else:
            expiration_time = f'{expiration_time} minutos'
    else:
        if expiration_time == 1:
            expiration_time = f'{expiration_time} segundo'
        else:
            expiration_time = f'{expiration_time} segundos'

    message = f'Olá, {first_name if first_name else "usuário"}!\n\n'
    message += f'Espero que este e-mail encontre você bem.\n\n'
    message += f'Gostaria de ajudá-lo a redefinir a sua senha. Para isso, basta clicar no link abaixo:\n\n{link}\n\n'
    message += f'É importante lembrar que, por motivos de segurança, o link terá validade de apenas {expiration_time}.\n\n'
    message += f'Caso você não tenha solicitado a redefinição de senha, por favor, ignore este e-mail.\n\n'
    message += f'Agradecemos a sua confiança em nossa empresa.\n\nAtenciosamente,\n\n{current_year} © Smart Watering'

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception:
        return False

    return True
