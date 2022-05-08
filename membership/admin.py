import imp
from django.contrib import admin
from .models import Membership, MembershipPlan, Subscription

# Register your models here.
admin.site.register(Membership)
admin.site.register(MembershipPlan)
admin.site.register(Subscription)