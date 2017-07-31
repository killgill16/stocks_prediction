from __future__ import unicode_literals

from django.db import models

class StockInfo(models.Model):
	ticker = models.CharField(max_length = 20)
	name = models.CharField(max_length = 50)