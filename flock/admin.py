from django.contrib import admin

from flock.models import Project, Reward, Donation


class RewardInline(admin.TabularInline):
    model = Reward
    extra = 0


admin.site.register(
    Project,
    list_display=('title', 'is_active', 'funding_goal', 'created_at'),
    inlines=[RewardInline],
)
admin.site.register(
    Donation,
    list_display=(
        'created_at', 'charged_at', 'amount', 'payment_service_provider',
        'full_name', 'email'),
)
