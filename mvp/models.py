import os
import stripe
from babel.numbers import get_currency_precision
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from djmoney.models.fields import MoneyField
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError
import uuid

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


def money_to_integer(money):
    return int(
        money.amount * (
            10 ** get_currency_precision(money.currency.code)
        )
    )

# Create your models here.


class Mvp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        IN_REVIEW = 'review', _('In Review')
        REJECTED = 'rejected', _('Rejected')
        ACCEPTED = 'accepted', _('Accepted')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='mvps')
    name = models.CharField(max_length=100)
    one_liner = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # user describes their validation process
    validation = models.TextField(blank=True, null=True)
    preview_image = models.ImageField(
        upload_to="preview_images", blank=True, null=True)

    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)

    peak_user_count = models.IntegerField(default=0)
    current_user_count = models.IntegerField(default=0)

    # business stuff
    peak_mrr = MoneyField(
        max_digits=12, decimal_places=2, default_currency='USD', default=0)
    current_mrr = MoneyField(
        max_digits=12, decimal_places=2, default_currency='USD', default=0)

    # since projects usually consist of multiple repositories, we need to store the github project url
    # instead of the individual repository url
    github_project_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)

    code_score = models.PositiveSmallIntegerField(default=0)
    credit = MoneyField(max_digits=10, decimal_places=2,
                        default_currency='EUR', default=0)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_REVIEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.one_liner}"

    class Meta:
        ordering = ('-created_at',)


class MvpImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mvp = models.ForeignKey(
        Mvp, on_delete=models.CASCADE, related_name='images')
    preview_image = models.ImageField(
        upload_to="mvp_images", blank=True, null=True)


class CloudType(models.Model):
    # class Type(models.TextChoices):
    #     IAAS = 'IAAS', _('Infrastructure as a Service')
    #     PAAS = 'PAAS', _('Platform as a Service')
    #     SAAS = 'SAAS', _('Software as a Service')
    #     OTHER = 'OTHR', _('Other')

    # name = models.CharField(
    #     max_length=4,
    #     choices=Type.choices,
    #     default=Type.SAAS,
    # )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp, null=True, blank=True,
                                  related_name='cloud_types')

    def __str__(self):
        return f"{self.name}"


class Platform(models.Model):
    # class Type(models.TextChoices):
    #     WEB = 'WEB', _('Web')
    #     IOS = 'IOS', _('iOS')
    #     ANDROID = 'AND', _('Android')
    #     OTHER = 'OTHR', _('Other')

    # name = models.CharField(
    #     max_length=4,
    #     choices=Type.choices,
    #     default=Type.OTHER,
    # )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, null=True, blank=True, related_name='platforms')

    def __str__(self):
        return f"{self.name}"


class FailureReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp, null=True, blank=True,
                                  related_name='failure_reasons')

    def __str__(self):
        return f"{self.name}"


class Industry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp, null=True, blank=True,
                                  related_name='industries')

    def __str__(self):
        return f"{self.name}"


class TechStack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp, null=True, blank=True,
                                  related_name='tech_stack')

    def __str__(self):
        return f"{self.name}"


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, null=True, blank=True, related_name='services')

    def __str__(self):
        return f"{self.name}"


class Hosting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, null=True, blank=True, related_name='hosting')

    def __str__(self):
        return f"{self.name}"


class MvpSuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='suggestions')
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.suggestion}"

# @receiver(post_save, sender=Mvp)
# def create_mvp_stripe_product(sender, instance, created, **kwargs):
#     if created:
#         product = stripe.Product.create(
#             name=instance.name,
#             description=instance.one_liner,
#             url=instance.github_project_url,
#             metadata={
#                 'id': instance.pk,
#             }
#         )

#         price = stripe.Price.create(
#             unit_amount=money_to_integer(instance.credit),
#             currency="eur",
#             product=product['id'],
#         )

#         instance.stripe_price_id = price['id']
#         instance.stripe_product_id = product['id']
#         instance.save()


@receiver(pre_save, sender=Mvp)
def send_mvp_in_review_mail(sender, instance, **kwargs):
    if instance.id is None:
        user = instance.user
        subject = 'Your MVP is in review!'

        message = {
            "from_email": getattr(settings, 'DEFAULT_FROM_EMAIL'),
            "subject": subject,
            "text": "Your submission for {instance.name} is in review",
            # TODO change email
            "to": [
                {
                    "email": 'beta@thriftmvp.com',
                    "type": "to"
                }
            ],
            "global_merge_vars": [{
                "name": "mvp_name",
                "content": instance.name
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
                {"template_name": "mvp-in-review", "template_content": [{}], "message": message})
            print(response)
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))


@receiver(pre_save, sender=Mvp)
def send_mvp_accepted_mail(sender, instance, **kwargs):
    if instance.id is None:
        return

    previous = Mvp.objects.get(id=instance.id)
    if previous.status != instance.status and instance.status == Mvp.Status.ACCEPTED:
        user = instance.user
        subject = 'Your MVP has been accepted!'

        url = f"{os.environ.get('FRONTEND_URL')}/listing/{instance.pk}/"

        message = {
            "from_email": getattr(settings, 'DEFAULT_FROM_EMAIL'),
            "subject": subject,
            "text": f"Your submission for {instance.name} has been accepted",
            # TODO change email
            "to": [
                {
                    "email": 'beta@thriftmvp.com',
                    "type": "to"
                }
            ],
            "global_merge_vars": [{
                "name": "mvp_name",
                "content": instance.name
            },
                {
                "name": "mvp_url",
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
                {"template_name": "mvp-approved", "template_content": [{}], "message": message})
            print(response)
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))


@receiver(pre_save, sender=Mvp)
def send_mvp_not_accepted_mail(sender, instance, **kwargs):
    if instance.id is None:
        return

    previous = Mvp.objects.get(id=instance.id)
    if previous.status != instance.status and instance.status == Mvp.Status.REJECTED:
        user = instance.user
        subject = 'Your MVP has been rejected'

        message = {
            "from_email": getattr(settings, 'DEFAULT_FROM_EMAIL'),
            "subject": subject,
            "text": f"Your submission for {instance.name} did not qualify for our listing",
            # TODO change email
            "to": [
                {
                    "email": 'beta@thriftmvp.com',
                    "type": "to"
                }
            ],
            "global_merge_vars": [{
                "name": "mvp_name",
                "content": instance.name
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
                {"template_name": "mvp-rejected", "template_content": [{}], "message": message})
            print(response)
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))
