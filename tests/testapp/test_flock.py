from decimal import Decimal

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
        p = Project.objects.create(
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

        self.assertListEqual(
            p.available_rewards,
            [r1, r2],
        )

        response = self.client.get('/')
        self.assertContains(
            response,
            'type="radio"',
            3,
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
