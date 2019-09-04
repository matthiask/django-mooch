from django.db import models
from mooch.models import Payment

class PaymentReal(Payment):
	test = models.TextField('test')