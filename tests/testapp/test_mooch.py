from decimal import Decimal
from hashlib import sha1

from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.six import assertRegex

#from flock.models import Donation, Project
from testapp.models import PaymentReal
from mooch.postfinance import PostFinanceMoocher
from django.db import models


def _messages(response):
    return [m.message for m in response.context['messages']]

def fake():
    return ""

class Request():
    def build_absolute_uri(*arg):
        return ""

class MoochTest(TestCase):
    def test_postfinance(self):

        self.assertIsNotNone(PostFinanceMoocher)
        post_finance_moocher = PostFinanceMoocher(
            pspid = "fake",
            live = False,
            sha1_in = "fake",
            sha1_out = "fake",
            payment_methods=None,
        )

        payment = PaymentReal.objects.create(
            amount = 100,
            email = "fake@fake.com",
        )

        request = Request()
        response = post_finance_moocher.payment_form(request, payment)
        self.assertTrue('<input type="hidden" name="PMLIST" value="PostFinance Card;PostFinance e-finance">' in response)

        post_finance_moocher.payment_methods = ["PostFinance Card", "TWINT", "PAYPAL"]
        response = post_finance_moocher.payment_form(request, payment)
        self.assertTrue('<input type="hidden" name="PMLIST" value="PostFinance Card;TWINT;PAYPAL">' in response)