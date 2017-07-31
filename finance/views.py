from django.shortcuts import render
from yahoo_finance import Share
import matplotlib.pyplot as plt, mpld3
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import datetime as dt
import numpy as np
from sklearn.svm import SVR
import csv
from .models import StockInfo
import json
from django.http import HttpResponse

from xml.dom.minidom import parse
import xml.dom.minidom
import urllib

import json
from django.utils import timezone
from googlefinance import getQuotes

import requests


def load_stocks(file_path):
	reader = csv.DictReader(open(file_path))
	for row in reader:
		stock = StockInfo(ticker=row['Ticker'], name=row['Name'])
		stock.save()

def get_stocks(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		stocks = StockInfo.objects.filter(name__icontains = q)[:20]        
		results = []
		for stock in stocks:
			stock_json = {}
			stock_json['label'] = stock.name
			stock_json['value'] = stock.ticker
			results.append(stock_json)
		data = json.dumps(results)
	else:
		data = 'fail'    
	return HttpResponse(data)


def home(request):
	
	template = 'stocksml/home.html'
	return render(request,template) 

def main(request):
	q = request.GET.get('q') 
	stocks = StockInfo.objects.filter(ticker__icontains = q) 
	if stocks:
		for stock in stocks:
			stock_name = stock.name
	else:
		stock_name = q	
	requestURL = 'http://feeds.finance.yahoo.com/rss/2.0/headline?s='+q+'&region=US&lang=en-US'
	DOMTree = xml.dom.minidom.parse((urllib.urlopen(requestURL)))
	items = DOMTree.getElementsByTagName("item")
	
	'''		NEWS 	'''
	new = []
	for item in items:
		i=0
		news = {}
		title = item.getElementsByTagName('title')[i]
		title = title.childNodes[i].data
		news['title'] = title.replace("[$$]","")

		date = item.getElementsByTagName('pubDate')[i]
		date = date.childNodes[i].data
		news['date'] = date[:-6]

		link = item.getElementsByTagName('link')[i]
		link =  link.childNodes[i].data
		news['link'] = link

		desc =item.getElementsByTagName('description')[i]
		desc = desc.childNodes[i].data
		news['desc'] = desc.replace('<b>',"").replace('</b>',"")
		new.append(news)	

	''' 	END NEWS 	'''		
	

	now = timezone.localtime(timezone.now())
	style.use('ggplot')
	plt.figure(figsize=(15,7))
	start = dt.datetime(2016,4,9)
	end = dt.datetime(now.year,now.month,now.day) 
	df = web.DataReader(q, 'yahoo', start, end)
	length = len(df)
	latest_data = df[-1:]
	latest_data_dic = {'Open':latest_data['Open'].tolist()[0],'High':latest_data['High'].tolist()[0],'Low':latest_data['Low'].tolist()[0],'Volume':latest_data['Volume'].tolist()[0],'Close':latest_data['Close'].tolist()[0],'Adj_Close':latest_data['Adj Close'].tolist()[0]}
	dates_panda = pd.to_datetime(df.index, format='%Y-%m-%d')

	dates_panda = dates_panda.insert(len(dates_panda),pd.to_datetime(`now.year`+'-'+`now.month`+'-'+`now.day`,format='%Y-%m-%d'))
	
	best_dates = range(0,length+1)
	prices = []
	prices = df['Adj Close'].tolist()	
	last_value=0.0


	if '.' in q:
		print 'I am here'
		strip_q_index = q.index('.')
		new_q = q[:strip_q_index]
		request1 = requests.get('https://www.google.com/finance/info?q='+new_q)
		request1 = request1.content
		request1 = request1.replace('\n','')[4:].strip(']')		
		request_json = json.loads(request1)
		final_data = request_json['l']
		last_value = final_data.encode('utf-8').replace(",","")
		
		prices.insert(length,float(last_value))
	else:
		request1 = requests.get('https://www.google.com/finance/info?q='+q)
		request1 = request1.content.replace('\n','')[4:].strip(']')
		request_json = json.loads(request1)
		final_data = request_json['l']
		last_value = final_data.encode('utf-8').replace(",","")
		prices.insert(length,float(last_value))

		
	'''ML ALGORITHM FROM HERE'''

	best_dates = np.reshape(best_dates,(len(best_dates), 1))
	# print 'best_dates',len(best_dates)  
	svr_rbf = SVR(kernel= 'rbf', C= 1e3, gamma= 0.1)  #changed from 0.1 
	svr_rbf.fit(best_dates, prices)
	plt.scatter(dates_panda, prices, color= 'black', label= 'Data')
	plt.plot(dates_panda, svr_rbf.predict(best_dates), color= 'red', label= 'RBF model')
	predict_value = svr_rbf.predict(length+1)[0]
	# score = svr_rbf.score(best_dates, prices)
	# print predict_value
	# print score


	'''END OF ML ALGO'''
	plt.xlabel('Date')
	plt.ylabel('Price')
	plt.legend()    
	fig = plt.gcf()
	plot = mpld3.fig_to_html(fig)
	context = {'plot':plot, 'predict_value':predict_value,'stock_name':stock_name,'news':new,'latest_data_dic':latest_data_dic}
	template = 'stocksml/index.html'

	return render(request,template,context)

