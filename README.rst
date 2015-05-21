===========================
flock - Simple crowdfunding
===========================

.. image:: https://travis-ci.org/matthiask/django-email-registration.png?branch=master
   :target: https://travis-ci.org/matthiask/django-email-registration


Usage
=====

This example assumes you are using a recent version of Django, jQuery and
Twitter Bootstrap.

1. Install ``django-flock`` using pip.

2. Add the following settings::

    STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
    POSTFINANCE_PSPID = env('POSTFINANCE_PSPID')
    POSTFINANCE_LIVE = env('POSTFINANCE_LIVE')
    POSTFINANCE_SHA1_IN = env('POSTFINANCE_SHA1_IN')
    POSTFINANCE_SHA1_OUT = env('POSTFINANCE_SHA1_OUT')

3. Add ``flock`` to ``INSTALLED_APPS`` and include
   ``flock.urls`` somewhere in your URLconf.

4. Presto.
