from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from accounts.models import UserProfile
from babel.numbers import get_currency_precision
import stripe


def money_to_integer(money):
    return int(
        money.amount * (
            10 ** get_currency_precision(money.currency.code)
        )
    )


def create_stripe_price(instance, interval):
    price = stripe.Price.create(
        unit_amount=money_to_integer(instance.credit),
        currency=instance.credit.currency.code.lower(),
        recurring={"interval": 'month', 'interval_count': interval},
        product=instance.membership.stripe_product_id,
    )

    return price


class Membership(models.Model):
    class Tier(models.TextChoices):
        PREMIUM = 'premium', _('Premium')

    tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        default=Tier.PREMIUM,
    )
    stripe_product_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.tier


class MembershipPlan(models.Model):
    class Interval(models.TextChoices):
        ONE_MONTH = 'one_month', _('One month')
        SIX_MONTHS = 'six_months', _('Six months')
        ONE_YEAR = 'one_year', _('One year')


    interval = models.CharField(
        max_length=20,
        choices=Interval.choices,
        default=Interval.ONE_MONTH,
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    credit = MoneyField(max_digits=7, decimal_places=2, default_currency='EUR')
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.membership} - {self.name}"


class Subscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = 'trialing', _('Trialing')
        ACTIVE = 'active', _('Active')
        CANCELLED = 'canceled', _('Canceled')
        PAST_DUE = 'past_due', _('Past Due')
        UNPAID = 'unpaid', _('Unpaid')
        INCOMPLETE = 'incomplete', _('Incomplete')
        INCOMPLETE_EXPIRED = 'incomplete_expired', _('Incomplete Expired')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INCOMPLETE,
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="subscriptions")
    membership_plan = models.ForeignKey(
        MembershipPlan, on_delete=models.CASCADE, related_name="subscriptions")
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.membership_plan}"


@receiver(pre_save, sender=Membership)
def membership_updated(sender, instance, *args, **kwargs):
    # create stripe Product
    if not instance.stripe_product_id:
        product = stripe.Product.create(
            name="%s" % (instance.tier))
        instance.stripe_product_id = product.id
    else:
        pass

    # # create stripe Price
    # if not instance.price_id:
    #     one_month = MembershipPlan.objects.create()
    #     price = create_stripe_price(instance, 1)
    #     instance.price_id = price.id


@receiver(pre_save, sender=MembershipPlan)
def membership_plan_updated(sender, instance, *args, **kwargs):
    # create stripe Price
    if not instance.stripe_price_id:
        if instance.interval == MembershipPlan.Interval.ONE_MONTH:
            price = create_stripe_price(instance, 1)
            instance.stripe_price_id = price.id
        elif instance.interval == MembershipPlan.Interval.SIX_MONTHS:
            price = create_stripe_price(instance, 6)
            instance.stripe_price_id = price.id
        elif instance.interval == MembershipPlan.Interval.ONE_YEAR:
            price = create_stripe_price(instance, 12)
            instance.stripe_price_id = price.id
            