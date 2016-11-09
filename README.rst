======================
mooch - Simple payment
======================

Steps
=====

1. Install ``django-mooch`` using pip and add ``mooch`` to your
   ``INSTALLED_APPS``.

2. Add a moochers app::

    from django.conf import settings
    from django.conf.urls import include, url

    from mooch.banktransfer import BankTransferMoocher
    from mooch.postfinance import PostFinanceMoocher
    from mooch.stripe import StripeMoocher

    from myapp.models import Thing  # Inherit mooch.models.Payment


    moochers = [
        PostFinanceMoocher(
            model=Thing,
            pspid='thing',
            live=False,
            sha1_in=settings.POSTFINANCE_SHA1_IN,
            sha1_out=settings.POSTFINANCE_SHA1_OUT,
        ),
        StripeMoocher(
            model=Thing,
            publishable_key=settings.STRIPE_PUBLISHABLE_KEY,
            secret_key=settings.STRIPE_SECRET_KEY,
        ),
        BankTransferMoocher(
            model=Thing,
            autocharge=True,  # Mark all payments as successful.
        ),
    ]


    app_name = 'mooch'  # This is important
    urlpatterns = [
        url(r'', moocher.urls) for moocher in moochers
    ]

3. Include the moochers app / URLconf somewhere in your other URLconfs.

4. Add a payment page::

    def pay(request, id):
        instance = get_object_or_404(Thing.objects.all(), id=id)

        return render(request, 'pay.html', {
            'thing': instance,
            'moochers': [
                moocher.payment_form(request, instance) for moocher in moochers
            ],
        })

5. Maybe send a confirmation mail when charges happen (an example
   template for this is actually included with the project)::

    from mooch.mail import render_to_mail
    from mooch.signals import post_charge

    # The signal handler receives the moocher class, the payment and
    # the request.
    def send_mail(sender, payment, **kwargs):
        if isinstance(payment, Thing):
            # Moochers may be used more than once per website
            render_to_mail('mooch/thanks_mail', {
                'payment': payment,
            }, to=[payment.email]).send(fail_silently=True)

    post_charge.connect(send_mail)

   If you want to differentiate between moochers (for example to send
   a different mail for bank transfers, because the payment has not
   actually happened yet) set the ``sender`` argument when connecting
   as follows::

    # Some stuff you'll have to imagine... sorry.
    post_charge.connect(thank_you_mail, sender=PostFinanceMoocher)
    post_charge.connect(thank_you_mail, sender=StripeMoocher)
    post_charge.connect(please_pay_mail, sender=BankTransferMoocher)
