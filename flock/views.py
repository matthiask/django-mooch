from hashlib import sha1
import json
import locale
import logging
import requests

from django import http
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import get_language, to_locale, ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from flock.forms import DonationAmountForm, DonationDetailsForm
from flock.mail import render_to_mail
from flock.models import Project, Donation


logger = logging.getLogger('flock')


def donate_amount(request):
    project = Project.objects.current()

    if request.method == 'POST':
        form = DonationAmountForm(request.POST, project=project)
        if form.is_valid():
            donation = form.save()

            return redirect(
                'flock_donate_details',
                id=donation.id.hex,
            )

    else:
        form = DonationAmountForm(project=project)

    return render(request, 'flock/donate_amount_form.html', {
        'project': project,
        'form': form,
    })


def donate_details(request, id):
    donation = get_object_or_404(Donation, id=id)
    kw = {'instance': donation}

    try:
        kw['initial'] = json.loads(request.COOKIES['flock'])
    except:
        pass

    if request.method == 'POST':
        form = DonationDetailsForm(request.POST, **kw)

        if form.is_valid():
            donation = form.save()

            response = redirect(
                'flock_donate_payment_provider',
                id=donation.id.hex,
            )

            if form.cleaned_data.get('remember_my_name'):
                response.set_cookie(
                    'flock',
                    json.dumps({
                        'full_name': donation.full_name,
                        'email': donation.email,
                    }),
                )
            else:
                response.delete_cookie('flock')

            return response

    else:
        form = DonationDetailsForm(**kw)

    return render(request, 'flock/donate_amount_form.html', {  # XXX fix tpl.
        'project': donation.project,
        'form': form,
    })


def donate_payment_provider(request, id):
    donation = get_object_or_404(Donation, id=id)

    if donation.charged_at is not None:
        messages.info(
            request,
            _('This donation has already been processed. Thank you!'),
        )
        return redirect('flock_donate_amount')

    postfinance = {
        # Add a random suffix, because Postfinance does not like
        # processing the same order ID over and over.
        'donationID': '%s-%s' % (donation.id.hex, get_random_string(4)),
        'amount': str(donation.amount_cents),
        'currency': 'CHF',
        'PSPID': settings.POSTFINANCE_PSPID,
        'mode': 'prod' if settings.POSTFINANCE_LIVE else 'test',
        'locale': locale.normalize(
            to_locale(get_language())).split('.')[0],
    }

    postfinance['SHASign'] = sha1((''.join((
        postfinance['donationID'],
        postfinance['amount'],
        postfinance['currency'],
        postfinance['PSPID'],
        settings.POSTFINANCE_SHA1_IN,
    ))).encode('utf-8')).hexdigest()

    return render(request, 'flock/donate_payment_provider.html', {
        'donation': donation,
        'postfinance': postfinance,
        'host': request.build_absolute_uri('/'),
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,

        'thanks_url': request.build_absolute_uri(reverse('flock_thanks')),
    })


@csrf_exempt
@never_cache
@require_POST
def donate_stripe(request):
    donation = get_object_or_404(Donation, id=request.POST.get('id'))
    donation.transaction = repr(request.POST)
    donation.save()

    response = requests.post(
        'https://api.stripe.com/v1/charges',
        auth=(settings.STRIPE_SECRET_KEY, ''),
        data={
            'amount': donation.amount_cents,
            'source': request.POST.get('token'),
            'currency': 'CHF',
        },
        headers={
            'Idempotency-Key': donation.id.hex,
        },
        timeout=5,
    )

    donation.charged_at = timezone.now()
    donation.transaction = response.text
    donation.save()

    render_to_mail('flock/thanks_mail', {
        'donation': donation,
    }, to=[donation.email]).send(fail_silently=True)

    return http.HttpResponse('OK')


@csrf_exempt
def donate_postfinance_postsale(request):
    try:
        parameters_repr = repr(request.POST.copy()).encode('utf-8')
        logger.info('IPN: Processing request data %s' % parameters_repr)

        try:
            donationID = request.POST['orderID']
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
            donationID,
            currency,
            amount,
            PM,
            ACCEPTANCE,
            STATUS,
            CARDNO,
            PAYID,
            NCERROR,
            BRAND,
            settings.POSTFINANCE_SHA1_OUT,
        ))

        sha1_out = sha1(sha1_source.encode('utf-8')).hexdigest()

        if sha1_out.lower() != SHASIGN.lower():
            logger.error('IPN: Invalid hash in %s' % parameters_repr)
            return http.HttpResponseForbidden('Hash did not validate')

        try:
            donation = Donation.objects.get(pk=donationID.split('-')[0])
        except Donation.DoesNotExist:
            logger.error('IPN: Order %s does not exist' % donationID)
            return http.HttpResponseForbidden(
                'Order %s does not exist' % donationID)

        if STATUS in ('5', '9'):
            donation.charged_at = timezone.now()

        donation.transaction = parameters_repr
        donation.save()

        render_to_mail('flock/thanks_mail', {
            'donation': donation,
        }, to=[donation.email]).send(fail_silently=True)

        return http.HttpResponse('OK')

    except Exception as e:
        logger.error('IPN: Processing failure %s' % e)
        raise


@never_cache
@require_POST
def donate_banktransfer(request):
    donation = get_object_or_404(Donation, id=request.POST.get('id'))
    donation.transaction = repr(request.POST)
    donation.charged_at = timezone.now()
    donation.save()

    # TODO email verification before donation is counted towards total?

    render_to_mail('flock/thanks_mail', {
        'donation': donation,
    }, to=[donation.email]).send()

    messages.success(request, _(
        'You will receive an email within a few minutes containing details'
        ' about your donation. Thank you!'
    ))

    return redirect('flock_thanks')


def donate_thanks(request):
    return render(request, 'flock/donate_thanks.html', {})


def donate_fail(request):
    return render(request, 'flock/donate_fail.html', {})
