from hashlib import sha1
import locale
import logging

from django import http
from django.conf import settings
from django.conf.urls import url
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import get_language, to_locale

from mooch.base import BaseMoocher, csrf_exempt_m, require_POST_m
from mooch.mail import render_to_mail


logger = logging.getLogger('mooch.postfinance')


class PostfinanceMoocher(BaseMoocher):
    def __init__(self, **kwargs):
        self.pspid = settings.POSTFINANCE_PSPID
        self.live = settings.POSTFINANCE_LIVE
        self.sha1_in = settings.POSTFINANCE_SHA1_IN
        self.sha1_out = settings.POSTFINANCE_SHA1_OUT
        super().__init__(**kwargs)

    def get_urls(self):
        return [
            url(r'^postsale/$', self.postsale_view,
                name='postfinance_postsale'),
        ]

    def payment_form(self, request, payment):
        postfinance = {
            # Add a random suffix, because Postfinance does not like
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
            'payment': payment,
            'postfinance': postfinance,
            'mode': 'prod' if self.live else 'test',

            'thanks_url': request.build_absolute_uri('/'),  # TODO
            'fail_url': request.build_absolute_uri('/'),  # TODO
        })

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

            instance.payment_service_provider = 'postfinance'
            instance.transaction = parameters_repr
            instance.save()

            render_to_mail('mooch/thanks_mail', {
                'instance': instance,
            }, to=[instance.email]).send(fail_silently=True)

            return http.HttpResponse('OK')

        except Exception as e:
            logger.error('IPN: Processing failure %s' % e)
            raise