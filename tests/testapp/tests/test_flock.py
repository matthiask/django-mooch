from django.test import TestCase


from flock.models import Project


def _messages(response):
    return [m.message for m in response.context['messages']]


class FlockTest(TestCase):
    def test_project(self):
        Project.objects.create(
            funding_goal=2000,
        )

        self.assertIsNotNone(Project.objects.current())
