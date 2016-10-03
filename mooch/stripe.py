import requests

from django import http
from django.conf import settings
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from mooch.base import BaseMoocher, csrf_exempt_m, require_POST_m
from mooch.mail import render_to_mail


class StripeMoocher(BaseMoocher):
    def __init__(self, **kwargs):
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.secret_key = settings.STRIPE_SECRET_KEY
        super().__init__(**kwargs)

    def get_urls(self):
        return [
            url(r'^charge/$', self.charge_view, name='stripe_charge'),
        ]

    def payment_form(self, request, payment):
        return render_to_string('mooch/stripe_payment_form.html', {
            'payment': payment,
            'publishable_key': self.publishable_key,

            'LANGUAGE_CODE': request.LANGUAGE_CODE,
        })

    @csrf_exempt_m
    @require_POST_m
    def charge_view(self, request):
        instance = get_object_or_404(self.model, id=request.POST.get('id'))
        instance.payment_service_provider = 'stripe'
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

        render_to_mail('mooch/thanks_mail', {
            'instance': instance,
        }, to=[instance.email]).send(fail_silently=True)

        return http.HttpResponse('OK')
