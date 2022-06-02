import os
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework import serializers
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError


class CustomPasswordResetSerializer(PasswordResetSerializer):
    # def get_email_options(self):
    #     return {
    #         'from_email': 'noreply@{}'.format(Site.objects.get_current().domain),
    #         'html_email_template_name': 'registration/password_reset_email.html',
    #         'subject_template_name': 'registration/password_reset_subject.txt',
    #     }

    def save(self, **kwargs):
        User = get_user_model()
        request = self.context.get('request')
        current_site = get_current_site(request)
        email = request.data['email']
        token_generator = kwargs.get('token_generator',
                                     default_token_generator)

        user = User.objects.filter(email=email)

        if not user.exists():
            raise serializers.ValidationError({'email': 'User does not exist'})

        user = user.first()

        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        url = f"{os.environ.get('FRONTEND_URL')}/password/reset/{str(user.pk)}/{token_generator.make_token(user)}"

        message = {
            "from_email": getattr(settings, 'DEFAULT_FROM_EMAIL'),
            "subject": "Reset your ThriftMVP password",
            "text": "A password reset has been requested for your account.",
            # TODO change email
            "to": [
                {
                    "email": user.email,
                    "type": "to"
                }
            ],
            "global_merge_vars": [{
                "name": "test",
                "content": "test content"
            },
                {
                "name": "password_reset_url",
                "content": url
            },
                {
                "name": "name",
                "content": f"{user.first_name} {user.last_name}"
            }]
        }

        try:
            mailchimp = MailchimpTransactional.Client(
                os.environ.get('MAILCHIMP_TRANSACTIONAL_API_KEY'))
            response = mailchimp.messages.send_template(
                {"template_name": "reset-password", "template_content": [{}], "message": message})
            print(response)
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))

        # self.reset_form.save(**opts)


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        self.reset_form.save(**opts)
