from hashlib import sha1
import locale
import logging

from django import http
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import get_language, to_locale
from django.utils.translation import ugettext_lazy as _

from mooch.base import BaseMoocher, csrf_exempt_m, require_POST_m
from mooch.signals import post_charge


logger = logging.getLogger('mooch.postfinance')


class PostFinanceMoocher(BaseMoocher):
    identifier = 'postfinance'
    title = _('Pay with PostFinance')

    def __init__(self, *, pspid, live, sha1_in, sha1_out, **kwargs):
        if any(x is None for x in (pspid, live, sha1_in, sha1_out)):
            raise ImproperlyConfigured(
                '%s: None is not allowed in (%r, %r, %r, %r)' % (
                    self.__class__.__name__, pspid, live, sha1_in, sha1_out))

        self.pspid = pspid
        self.live = live
        self.sha1_in = sha1_in
        self.sha1_out = sha1_out
        super().__init__(**kwargs)

    def get_urls(self):
        return [
            url(r'^postfinance_postsale/$',
                self.postsale_view,
                name='postfinance_postsale'),
        ]

    def payment_form(self, request, payment):
        postfinance = {
            # Add a random suffix, because PostFinance does not like
            # processing the same order ID over and over.
            'orderID': '%s-%s' % (payment.id.hex, get_random_string(4)),
            'amount': str(payment.amount_cents),
            'currency': 'CHF',
            'PSPID': self.pspid,
            'language': locale.normalize(
                to_locale(get_language())).split('.')[0],
            'EMAIL': payment.email,
        }

        postfinance['SHASign'] = sha1((''.join((
            postfinance['orderID'],
            postfinance['amount'],
            postfinance['currency'],
            postfinance['PSPID'],
            self.sha1_in,
        ))).encode('utf-8')).hexdigest()

        return render_to_string('mooch/postfinance_payment_form.html', {
            'moocher': self,
            'payment': payment,
            'postfinance': postfinance,
            'mode': 'prod' if self.live else 'test',

            'success_url': request.build_absolute_uri(str(self.success_url)),
            'failure_url': request.build_absolute_uri(str(self.failure_url)),
        }, request=request)

    @csrf_exempt_m
    @require_POST_m
    def postsale_view(self, request):
        try:
            parameters_repr = repr(request.POST.copy()).encode('utf-8')
            logger.info('IPN: Processing request data %s' % parameters_repr)

            try:
                orderID = request.POST['orderID']
                currency = request.POST['currency']
                amount = request.POST['amount']
                PM = request.POST['PM']
                ACCEPTANCE = request.POST['ACCEPTANCE']
                STATUS = request.POST['STATUS']
                CARDNO = request.POST['CARDNO']
                PAYID = request.POST['PAYID']
                NCERROR = request.POST['NCERROR']
                BRAND = request.POST['BRAND']
                SHASIGN = request.POST['SHASIGN']
            except KeyError:
                logger.error('IPN: Missing data in %s' % parameters_repr)
                return http.HttpResponseForbidden('Missing data')

            sha1_source = ''.join((
                orderID,
                currency,
                amount,
                PM,
                ACCEPTANCE,
                STATUS,
                CARDNO,
                PAYID,
                NCERROR,
                BRAND,
                self.sha1_out,
            ))

            sha1_out = sha1(sha1_source.encode('utf-8')).hexdigest()

            if sha1_out.lower() != SHASIGN.lower():
                logger.error('IPN: Invalid hash in %s' % parameters_repr)
                return http.HttpResponseForbidden('Hash did not validate')

            try:
                instance = self.model.objects.get(pk=orderID.split('-')[0])
            except self.model.DoesNotExist:
                logger.error('IPN: Instance %s does not exist' % orderID)
                return http.HttpResponseForbidden(
                    'Instance %s does not exist' % orderID)

            if STATUS in ('5', '9'):
                instance.charged_at = timezone.now()

            instance.payment_service_provider = self.identifier
            instance.transaction = parameters_repr
            instance.save()

            post_charge.send(
                sender=self.__class__,
                payment=instance,
                request=request,
            )

            return http.HttpResponse('OK')

        except Exception as e:
            logger.error('IPN: Processing failure %s' % e)
            raise
