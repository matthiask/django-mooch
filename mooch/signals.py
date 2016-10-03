from django.dispatch import Signal


post_charge = Signal(providing_args=['payment', 'request'])
