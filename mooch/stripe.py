import requests

from django import http
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from mooch.base import BaseMoocher, csrf_exempt_m, require_POST_m
from mooch.signals import post_charge


class StripeMoocher(BaseMoocher):
    identifier = 'stripe'
    title = _('Pay with Stripe')

    def __init__(self, *, publishable_key, secret_key, **kwargs):
        if any(x is None for x in (publishable_key, secret_key)):
            raise ImproperlyConfigured(
                '%s: None is not allowed in (%r, %r)' % (
                    self.__class__.__name__, publishable_key, secret_key))

        self.publishable_key = publishable_key
        self.secret_key = secret_key = secret_key
        super().__init__(**kwargs)

    def get_urls(self):
        return [
            url(r'^stripe_charge/$',
                self.charge_view,
                name='stripe_charge'),
        ]

    def payment_form(self, request, payment):
        return render_to_string('mooch/stripe_payment_form.html', {
            'moocher': self,
            'payment': payment,
            'publishable_key': self.publishable_key,

            'LANGUAGE_CODE': getattr(request, 'LANGUAGE_CODE', 'auto'),
        }, request=request)

    @csrf_exempt_m
    @require_POST_m
    def charge_view(self, request):
        instance = get_object_or_404(self.model, id=request.POST.get('id'))
        instance.payment_service_provider = self.identifier
        instance.transaction = repr({
            key: values
            for key, values in request.POST.lists()
            if key != 'token'
        })
        instance.save()

        response = requests.post(
            'https://api.stripe.com/v1/charges',
            auth=(self.secret_key, ''),
            data={
                'amount': instance.amount_cents,
                'source': request.POST.get('token'),
                'currency': 'CHF',
            },
            headers={
                'Idempotency-Key': instance.id.hex,
            },
            timeout=5,
        )

        instance.charged_at = timezone.now()  # TODO handle 402 (card reject)
        instance.transaction = response.text
        instance.save()

        post_charge.send(
            sender=self.__class__,
            payment=instance,
            request=request,
        )

        return http.HttpResponse('OK')
