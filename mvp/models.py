import os
import stripe
from babel.numbers import get_currency_precision
from django.db import models
from django.dispatch import receiver
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
    name = models.CharField(max_length=100)
    one_liner = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # user describes their validation process
    validation = models.TextField(blank=True, null=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)

    # since projects usually consist of multiple repositories, we need to store the github project url
    # instead of the individual repository url
    github_project_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)

    credit = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', default=0)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(pre_save, sender=Mvp)
def create_mvp_stripe_product(sender, instance, **kwargs):
    if instance._state.adding:
        product = stripe.Product.create(
            name=instance.name,
            description=instance.one_liner,
            url=instance.github_project_url,
            metadata={
                'id': instance.pk,
            }
        )

        price = stripe.Price.create(
            unit_amount=money_to_integer(instance.price),
            currency="eur",
            product=product['id'],
        )

        instance.stripe_price_id = price['id']
        instance.stripe_product_id = product['id']
        instance.save()

