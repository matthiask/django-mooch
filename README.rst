======================
mooch - Simple payment
======================

Steps
=====

1. Install ``django-mooch`` using pip and add ``mooch`` to your
   ``INSTALLED_APPS``.

2. Add the following settings::

    STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
    POSTFINANCE_PSPID = env('POSTFINANCE_PSPID')
    POSTFINANCE_LIVE = env('POSTFINANCE_LIVE')
    POSTFINANCE_SHA1_IN = env('POSTFINANCE_SHA1_IN')
    POSTFINANCE_SHA1_OUT = env('POSTFINANCE_SHA1_OUT')

3. Add a moochers app::

    from django.conf.urls import include, url

    from mooch.postfinance import PostfinanceMoocher
    from mooch.stripe import StripeMoocher

    from myapp.models import Thing  # Inherit mooch.models.Payment


    postfinance_moocher = PostfinanceMoocher(model=Thing)
    stripe_moocher = StripeMoocher(model=Thing)

    moochers = [postfinance_moocher, stripe_moocher]


    app_name = 'mooch'  # This is important
    urlpatterns = [
        url(r'^postfinance/', include(postfinance_moocher.urls)),
        url(r'^stripe/', include(stripe_moocher.urls)),
    ]

4. Include the moochers app / URLconf somewhere in your other URLconfs.

5. Add a payment page::

    def pay(request, id):
        instance = get_object_or_404(Thing.objects.all(), id=id)

        return render(request, 'pay.html', {
            'thing': instance,
            'moochers': [
                moocher.payment_form(request, instance) for moocher in moochers
            ],
        })
