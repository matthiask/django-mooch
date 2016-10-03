import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Payment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
    )
    charged_at = models.DateTimeField(
        _('charged at'),
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
    )
    payment_service_provider = models.CharField(
        _('payment service provider'),
        max_length=100,
        blank=True,
    )
    email = models.EmailField(
        _('email'),
        max_length=254,
    )
    transaction = models.TextField(
        _('transaction'),
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        verbose_name = _('payment')
        verbose_name_plural = _('donations')

    def __str__(self):
        return '%.2f' % self.amount

    @property
    def amount_cents(self):
        return int(self.amount * 100)
