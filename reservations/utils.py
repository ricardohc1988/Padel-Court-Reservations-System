import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def generate_code():
    """
    Generates a random 6-digit verification code.

    Returns:
        str: A 6-digit random code as a string.
    """
    return str(random.randint(100000, 999999))

def send_verification_email(user, code):
    """
    Sends an email with a verification code to the user.

    Args:
        user (User): The user object to whom the email is sent.
        code (str): The verification code to include in the email.
    """
    subject = 'Email Verification'
    from_email = settings.EMAIL_HOST_USER
    to = user.email

    html_content = render_to_string('emails/verification_email.html', {'code': code})
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def resend_verification_email(user, code):
    """
    Sends a new verification email with a new code to the user.

    Args:
        user (User): The user object to whom the email is sent.
        code (str): The new verification code to include in the email.
    """
    subject = 'Email Verification - New Code'
    from_email = settings.EMAIL_HOST_USER
    to = user.email

    html_content = render_to_string('emails/resend_verification_email.html', {'code': code})
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_reservation_confirmation_email(reservation):
    """
    Sends a confirmation email for a new reservation to the user.

    Args:
        reservation (Reservation): The reservation object for which the email is sent.
    """
    subject = 'New Reservation Confirmation'
    from_email = settings.EMAIL_HOST_USER
    to = reservation.user.email

    html_content = render_to_string('emails/reservation_confirmation_email.html', {
        'username': reservation.user.username,
        'reservation': reservation
    })
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_reservation_cancellation_email(reservation):
    """
    Sends an email notification for a cancelled reservation to the user.

    Args:
        reservation (Reservation): The reservation object that has been cancelled.
    """
    subject = 'Reservation Cancelled'
    from_email = settings.EMAIL_HOST_USER
    to = reservation.user.email

    html_content = render_to_string('emails/reservation_cancellation_email.html', {
        'username': reservation.user.username,
        'reservation': reservation
    })
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
