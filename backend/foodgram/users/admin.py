from django.contrib import admin
from .models import User, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    """ Админ-зона подписок."""

    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user',)


admin.site.register(User)
admin.site.register(Subscription, SubscriptionAdmin)
