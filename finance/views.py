from django.shortcuts import render

from .models import StockInfo
import json
from django.http import HttpResponse

from xml.dom.minidom import parse
import xml.dom.minidom
import urllib


import contextlib
import re
import selenium.webdriver as webdriver
import selenium.webdriver.support.ui as ui


import requests


def home(request):

	with contextlib.closing(webdriver.Chrome('/Users/paramvirgill/Desktop/chromedriver')) as driver:
	# with contextlib.closing(webdriver.Chrome()) as driver:	
		driver.get('https://www.bitmoji.com/account/index.html')
		wait = ui.WebDriverWait(driver, 70) # timeout after 10 seconds
		results = wait.until(lambda driver: driver.find_elements_by_class_name('gmail-floater'))
		if results:
			html_source = driver.page_source
			x_1 = 'render.bitstrips.com/render/'
			len1 = len(x_1)
			index1 = html_source.index(x_1)
			first_slice = len1+index1
			newstring = html_source[first_slice:first_slice+40]
			slash_index = [(m.start(0),m.end(0)) for m in re.finditer('/\d+.\d.+\w\d',newstring)]
			slash_index = slash_index[0]
			first_index = int(slash_index[0])+1
			last_index = int(slash_index[1])-3
			final_string = newstring[first_index:last_index]
			print final_string
			dictionary = {'final_string':final_string}
			template = 'stocksml/home.html'
			return render(request,template,dictionary) 

