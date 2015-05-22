from decimal import Decimal
from hashlib import sha1

from django.core import mail
from django.test import TestCase
from django.utils import timezone


from flock.models import Project, Donation


def _messages(response):
    return [m.message for m in response.context['messages']]


class FlockTest(TestCase):
    def test_project(self):
        self.assertIsNone(Project.objects.current())

        p = Project.objects.create(
            funding_goal=2000,
        )

        self.assertIsNotNone(Project.objects.current())

        d = p.donation_set.create(
            amount=500,
        )

        self.assertEqual(
            p.donation_total,
            0,
        )

        d.charged_at = timezone.now()
        d.save()

        # @cached_property
        self.assertEqual(
            p.donation_total,
            0,
        )

        p = Project.objects.get()
        self.assertEqual(
            p.donation_total,
            500,
        )

        self.assertEqual(
            p.funding_percentage,
            25,
        )

        self.assertEqual(
            p.available_rewards,
            [],
        )

    def test_donate_cents(self):
        d = Donation.objects.create(
            project=Project.objects.create(
                funding_goal=2000,
            ),
            amount=Decimal('5.55'),
        )

        self.assertEqual(d.amount, Decimal('5.55'))
        self.assertEqual(d.amount_cents, 555)

    def test_donation_views(self):
        Project.objects.create(
            funding_goal=2000,
            default_amount=50,
        )

        self.assertContains(
            self.client.get('/'),
            '<form',
            1,
        )

        response = self.client.post('/', {
            'amount': '50.00',
        })

        d = Donation.objects.get()
        url = 'http://testserver/details/%s/' % d.id.hex

        self.assertRedirects(
            response,
            url,
        )

        response = self.client.post(url, {
            'full_name': 'Hans Muster',
            'email': 'hans@example.com',
            'remember_my_name': '',
        })

        url = 'http://testserver/psp/%s/' % d.id.hex
        self.assertRedirects(
            response,
            url,
        )

        response = self.client.get(url)

        self.assertContains(
            response,
            '<input type="hidden" name="SHASign"',
            1,
        )
        self.assertContains(
            response,
            'StripeCheckout.configure(',
            1,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

        self.assertIsNone(d.charged_at)

        response = self.client.post('/banktransfer/', {
            'id': d.id.hex,
        })

        d.refresh_from_db()
        self.assertIsNotNone(d.charged_at)

        self.assertRedirects(
            response,
            'http://testserver/thanks/',
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        response = self.client.get(url, follow=True)

        self.assertRedirects(
            response,
            'http://testserver/',
        )

        self.assertListEqual(
            _messages(response),
            ['This donation has already been processed. Thank you!'],
        )

    def test_rewards(self):
        p = Project.objects.create(
            funding_goal=2000,
        )

        r1 = p.rewards.create(
            title='Dein Name erscheint',
            available_times=10,
            donation_amount=100,
        )
        r2 = p.rewards.create(
            title='Abendessen',
            available_times=1,
            donation_amount=1000,
        )
        r3 = p.rewards.create(
            title='Danke-Mail',
            available_times=None,
            donation_amount=1,
        )

        self.assertListEqual(
            p.available_rewards,
            [r3, r1, r2],
        )

        response = self.client.get('/')
        self.assertContains(
            response,
            'type="radio"',
            3 + 1,  # + no reward
        )

        response = self.client.post('/', {
            'amount': '50',
            'reward': '',
        })

        self.assertEqual(response.status_code, 302)

        response = self.client.post('/', {
            'amount': '50',
            'reward': r1.id,
        })

        self.assertContains(
            response,
            'The selected reward requires a minimal donation of 100.00.',
            1,
        )

        p.donation_set.create(
            amount=1500,
            selected_reward=r2,
            charged_at=None,
        )

        response = self.client.post('/', {
            'amount': '1500',
            'reward': r2.id,
        })

        self.assertEqual(response.status_code, 302)

        p.donation_set.create(
            amount=1500,
            selected_reward=r2,
            charged_at=timezone.now(),
        )

        response = self.client.post('/', {
            'amount': '1500',
            'reward': r2.id,
        })

        self.assertContains(
            response,
            'This reward is not available anymore. Sorry!',
            1,
        )

        response = self.client.post('/', {
            'amount': '10',
            'reward': r3.id,
        })

        self.assertEqual(response.status_code, 302)

    def test_remember_my_name(self):
        Project.objects.create(
            funding_goal=2000,
        )

        response = self.client.post('/', {
            'amount': '10',
        })

        d = Donation.objects.get()
        url = 'http://testserver/details/%s/' % d.id.hex

        self.assertRedirects(
            response,
            url,
        )

        response = self.client.post(url, {
            'full_name': 'Hans Muster',
            'email': 'hans@example.com',
            'remember_my_name': '1',
        })

        c = str(response.cookies)
        self.assertIn(
            'Set-Cookie: flock=',
            c,
        )
        self.assertIn(
            r'\"full_name\": \"Hans Muster\"',
            c,
        )

        self.assertIn(
            r'\"email\": \"hans@example.com\"',
            c,
        )

        self.assertIn(
            '; Path=/',
            c,
        )

        response = self.client.get(url)
        self.assertContains(
            response,
            'value="Hans Muster"',
            1,
        )
        self.assertContains(
            response,
            'value="hans@example.com"',
            1,
        )

        response = self.client.post(url, {
            'full_name': 'Hans Muster',
            'email': 'hans@example.com',
            'remember_my_name': '',
        })

        c = str(response.cookies)
        self.assertIn(
            'Set-Cookie: flock=;',
            c,
        )

    def test_postfinance_postsale(self):
        Project.objects.create(
            funding_goal=2000,
        )

        self.client.post('/', {
            'amount': '100',
        })
        donation = Donation.objects.get()
        self.client.post('/details/%s/' % donation.id.hex, {
            'full_name': 'Hans Muster',
            'email': 'hans@example.com',
        })

        ipn_data = {
            'orderID': '%s-random' % donation.id.hex,
            'currency': 'CHF',
            'amount': '100.00',
            'PM': 'Postfinance',
            'ACCEPTANCE': 'xxx',
            'STATUS': '5',  # Authorized
            'CARDNO': 'xxxxxxxxxxxx1111',
            'PAYID': '123456789',
            'NCERROR': '',
            'BRAND': 'VISA',
            'SHASIGN': 'this-value-is-invalid',
        }

        sha1_source = ''.join((
            ipn_data['orderID'],
            'CHF',
            '100.00',
            ipn_data['PM'],
            ipn_data['ACCEPTANCE'],
            ipn_data['STATUS'],
            ipn_data['CARDNO'],
            ipn_data['PAYID'],
            ipn_data['NCERROR'],
            ipn_data['BRAND'],
            'nothing',
        ))

        ipn_data['SHASIGN'] = sha1(sha1_source.encode('utf-8')).hexdigest()
        response = self.client.post('/postfinance/', ipn_data)

        self.assertEqual(
            response.status_code,
            200,
        )

        donation.refresh_from_db()
        self.assertIsNotNone(donation.charged_at)
