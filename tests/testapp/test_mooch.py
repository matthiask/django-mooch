from hashlib import sha1

from django.test import TestCase

from mooch.postfinance import PostFinanceMoocher
from testapp.models import Payment


def _messages(response):
    return [m.message for m in response.context["messages"]]


class Request:
    def build_absolute_uri(*arg):
        return ""


class MoochTest(TestCase):
    def test_postfinance_postsale(self):
        payment = Payment.objects.create(amount=100)
        ipn_data = {
            "orderID": "%s-random" % payment.id.hex,
            "currency": "CHF",
            "amount": "100.00",
            "PM": "Postfinance",
            "ACCEPTANCE": "xxx",
            "STATUS": "5",  # Authorized
            "CARDNO": "xxxxxxxxxxxx1111",
            "PAYID": "123456789",
            "NCERROR": "",
            "BRAND": "VISA",
            "SHASIGN": "this-value-is-invalid",
        }

        sha1_source = "".join(
            (
                ipn_data["orderID"],
                "CHF",
                "100.00",
                ipn_data["PM"],
                ipn_data["ACCEPTANCE"],
                ipn_data["STATUS"],
                ipn_data["CARDNO"],
                ipn_data["PAYID"],
                ipn_data["NCERROR"],
                ipn_data["BRAND"],
                "nothing",
            )
        )

        ipn_data["SHASIGN"] = sha1(sha1_source.encode("utf-8")).hexdigest()
        response = self.client.post("/postfinance_postsale/", ipn_data)

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.assertIsNotNone(payment.charged_at)

    def test_postfinance_payment_method(self):
        post_finance_moocher = PostFinanceMoocher(
            pspid="fake",
            live=False,
            sha1_in="fake",
            sha1_out="fake",
            payment_methods=None,
        )

        payment = Payment.objects.create(amount=100, email="fake@fake.com")

        request = Request()
        response = post_finance_moocher.payment_form(request, payment)
        self.assertTrue(
            '<input type="hidden" name="PMLIST" value="PostFinance Card;PostFinance e-finance">'
            in response
        )

        post_finance_moocher.payment_methods = ["PostFinance Card", "TWINT", "PAYPAL"]
        response = post_finance_moocher.payment_form(request, payment)
        self.assertTrue(
            '<input type="hidden" name="PMLIST" value="PostFinance Card;TWINT;PAYPAL">'
            in response
        )

    def test_banktransfer(self):
        payment = Payment.objects.create(amount=50)

        response = self.client.post("/banktransfer_confirm/", {"id": payment.id.hex})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

        payment.refresh_from_db()
        self.assertIsNotNone(payment.charged_at)
