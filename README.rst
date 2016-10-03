=====================
mooh - Simple payment
=====================

Usage
=====

1. Install ``django-mooch`` using pip.

2. Add the following settings::

    STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
    POSTFINANCE_PSPID = env('POSTFINANCE_PSPID')
    POSTFINANCE_LIVE = env('POSTFINANCE_LIVE')
    POSTFINANCE_SHA1_IN = env('POSTFINANCE_SHA1_IN')
    POSTFINANCE_SHA1_OUT = env('POSTFINANCE_SHA1_OUT')

3. Read the code, sorry.
