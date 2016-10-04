from django import http
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from mooch.base import BaseMoocher, require_POST_m
from mooch.signals import post_charge


class BankTransferMoocher(BaseMoocher):
    identifier = 'banktransfer'
    title = _('Pay by bank transfer')

    def __init__(self, *, autocharge, **kw):
        self.autocharge = autocharge
        super().__init__(**kw)

    def get_urls(self):
        return [
            url('^banktransfer_confirm/$',
                self.confirm_view,
                name='banktransfer_confirm'),
        ]

    def payment_form(self, request, payment):
        return render_to_string('mooch/banktransfer_payment_form.html', {
            'payment': payment,
            'moocher': self,
        }, request=request)

    @require_POST_m
    def confirm_view(self, request):
        instance = get_object_or_404(self.model, id=request.POST.get('id'))
        instance.payment_service_provider = self.identifier
        if self.autocharge:
            instance.charged_at = timezone.now()
        instance.save()

        post_charge.send(
            sender=self.__class__,
            payment=instance,
            request=request,
        )

        return http.HttpResponseRedirect(self.success_url)
