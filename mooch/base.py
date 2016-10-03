from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)


class BaseMoocher(object):
    #: The model instance used for mooching
    model = None

    identifier = None
    title = _('Pay')

    success_url = '/'
    failure_url = '/'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def urls(self):
        return self.get_urls()

    def get_urls(self):
        return []

    def payment_form(self):
        pass
