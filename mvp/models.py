import os
import stripe
from babel.numbers import get_currency_precision
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from djmoney.models.fields import MoneyField

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


def money_to_integer(money):
    return int(
        money.amount * (
            10 ** get_currency_precision(money.currency.code)
        )
    )

# Create your models here.


class Mvp(models.Model):
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

    # since projects usually consist of multiple repositories, we need to store the github project url
    # instead of the individual repository url
    github_project_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)

    code_score = models.PositiveSmallIntegerField(default=0)
    credit = MoneyField(max_digits=10, decimal_places=2,
                        default_currency='EUR', default=0)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.one_liner}"


class MvpImage(models.Model):
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
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp,
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
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, related_name='platforms')

    def __str__(self):
        return f"{self.name}"


class FailureReason(models.Model):
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp,
                                  related_name='failure_reasons')

    def __str__(self):
        return f"{self.name}"


class Industry(models.Model):
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp,
                                  related_name='industries')

    def __str__(self):
        return f"{self.name}"


class TechStack(models.Model):
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(Mvp,
                                  related_name='tech_stack')

    def __str__(self):
        return f"{self.name}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, related_name='services')

    def __str__(self):
        return f"{self.name}"


class Hosting(models.Model):
    name = models.CharField(max_length=100)
    mvps = models.ManyToManyField(
        Mvp, related_name='hosting')

    def __str__(self):
        return f"{self.name}"


@receiver(post_save, sender=Mvp)
def create_mvp_stripe_product(sender, instance, created, **kwargs):
    if created:
        product = stripe.Product.create(
            name=instance.name,
            description=instance.one_liner,
            url=instance.github_project_url,
            metadata={
                'id': instance.pk,
            }
        )

        price = stripe.Price.create(
            unit_amount=money_to_integer(instance.credit),
            currency="eur",
            product=product['id'],
        )

        instance.stripe_price_id = price['id']
        instance.stripe_product_id = product['id']
        instance.save()
