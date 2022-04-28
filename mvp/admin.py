from django.contrib import admin
from .models import Mvp, CloudType, Platform, Industry, TechStack, Service, Hosting, FailureReason


class CloudTypeTabular(admin.TabularInline):
    model = CloudType.mvps.through
    extra = 1


class PlatformTabular(admin.TabularInline):
    model = Platform.mvps.through
    extra = 1


class IndustryTabular(admin.TabularInline):
    model = Industry.mvps.through
    extra = 1


class TechStackTabular(admin.TabularInline):
    model = TechStack.mvps.through
    extra = 1


class ServiceTabular(admin.TabularInline):
    model = Service.mvps.through
    extra = 1


class HostingTabular(admin.TabularInline):
    model = Hosting.mvps.through
    extra = 1


class FailureReasonTabular(admin.TabularInline):
    model = FailureReason.mvps.through
    extra = 1


class MVPAdmin(admin.ModelAdmin):
    inlines = (CloudTypeTabular, PlatformTabular, IndustryTabular,
               TechStackTabular, ServiceTabular, HostingTabular, FailureReasonTabular)


# Register your models here.
admin.site.register(Mvp, MVPAdmin)
admin.site.register(CloudType)
admin.site.register(Platform)
admin.site.register(Industry)
admin.site.register(TechStack)
admin.site.register(Service)
admin.site.register(Hosting)
admin.site.register(FailureReason)
