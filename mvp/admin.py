from django.contrib import admin
from .models import Mvp, CloudType, Platform, Industry, TechStack, Service, Hosting

# Register your models here.
admin.site.register(Mvp)
admin.site.register(CloudType)
admin.site.register(Platform)
admin.site.register(Industry)
admin.site.register(TechStack)
admin.site.register(Service)
admin.site.register(Hosting)
