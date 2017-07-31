from django.contrib import admin

from .models import *

class StockInfoAdmin(admin.ModelAdmin):
	list_display = ("ticker", "name")
	search_fields = ("ticker","name")	

admin.site.register(StockInfo,StockInfoAdmin)