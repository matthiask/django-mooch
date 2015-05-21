from decimal import Decimal

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
