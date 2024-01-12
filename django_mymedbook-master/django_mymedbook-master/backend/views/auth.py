from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core import exceptions
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template import loader

from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

def validate_password(password, user=None):
    try:
        password_validation.validate_password(password, user)
    except exceptions.ValidationError as e:
        raise ValidationError({'detail': '\n'.join(e.messages)})

class PasswordReset(APIView):
    subject_template_name='registration/password_reset_subject.txt'
    email_template_name='registration/password_reset_email.html'

    def send_mail(self, context, to_email):
        subject = loader.render_to_string(self.subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, None, [to_email])
        email_message.send()

    def post(self, request):
        UserModel = get_user_model()

        try:
            user = UserModel._default_manager.get(email=request.data.get('email'), is_active=True)
        except UserModel.DoesNotExist:
            raise ValidationError('User not found')

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
            'password_reset_confirm': '/password/reset.html'
        }

        self.send_mail(context, user.email)

        return Response({'message': 'OK'})

class PasswordResetConfirm(APIView):
    def post(self, request, uidb64, token):
        UserModel = get_user_model()

        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError('Utente non trovato')

        if not default_token_generator.check_token(user, token):
            raise ValidationError('Token scaduto')

        new_password = request.data.get('new_password')
        user.plaintext_password = new_password
        validate_password(new_password, user)
        user.set_password(new_password)
        user.save()

        return Response({'message': 'OK'})
