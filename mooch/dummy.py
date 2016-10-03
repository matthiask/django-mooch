from django import http
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from mooch.base import BaseMoocher, require_POST_m
from mooch.mail import render_to_mail


class DummyMoocher(BaseMoocher):
    payment_service_provider = 'dummy'

    def get_urls(self):
        return [
            url('^confirm/$', self.confirm_view, name='dummy_confirm'),
        ]

    def payment_form(self, request, payment):
        return render_to_string('mooch/dummy_payment_form.html', {
            'payment': payment,
            'moocher': self,
        })

    @require_POST_m
    def confirm_view(self, request):
        instance = get_object_or_404(self.model, id=request.POST.get('id'))
        instance.payment_service_provider = self.payment_service_provider
        instance.transaction = repr(request.META.copy())
        instance.save()

        render_to_mail('mooch/thanks_mail', {
            'payment': instance,
        }, to=[instance.email]).send(fail_silently=True)

        return http.HttpResponseRedirect('/')  # TODO
