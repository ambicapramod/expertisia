from django.shortcuts import render
from .forms import SearchForm
from django.shortcuts import redirect
import urllib
import bs4
import numpy as np
import time
import socket 
import re
from pandas import Series
from multiprocessing import Process,Lock
import math
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import JsonResponse
skill_set = {}

class ChartData(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request,format=None):
        
        labels = list(skill_set.keys())
        default_items = list(skill_set.values())
        data = {
                "labels": labels,
                "default": default_items,
        }
        return Response(data)
def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data) 

class Job(object):
	def __init__(self,title,link,location):
		self.title = title
		self.link = link
		self.location = location

def go_to_links(job_links):
	
	global skill_set
	counter=0
	for link in job_links:
		print (link)
		counter += 1
	
		try:
			req = urllib.request.Request(link)
			result = urllib.request.urlopen(req)
			html_page = str(result.read())
		except urllib.error.HTTPError:
			print ("Http error")
			continue 
		except urllib.error.URLError:
			print ("Url error")
			continue 
		except socket.error as error:
			print ("Connection closed")
			continue
		
		html_text = re.sub("[^a-z.+3]"," ",html_page.lower()) # Replace all the characters with the listed characters
	#print (html_text)
		for key in skill_set.keys():
			if key in html_text:
				
				skill_set[key] += 1
				
			
	print (skill_set)
	return skill_set
	

def search_form(request):
	return render(request,'search/search_form.html')
def search_query(request):
	global skill_set
	jobs_list =[]
	if request.method == 'GET':
		url='http://indeed.com/jobs?q='
		if 'job_title' in request.GET:
			job_title_st = request.GET['job_title']
			job_title_st = "+".join(job_title_st.split())
			url=url+job_title_st
			if 'location' in request.GET:
				l="&l="+request.GET['location']
				url = url+l
			if 'skills' in request.GET:
				for skl in request.GET['skills'].lower().split(","):
					skill_set[skl]=0



		print (url)
		# Fixed url for job posting containing data scientist
		# read the website 

		# Scrapping begins here !!!
		assembeled_request= urllib.request.Request(url)
		result = urllib.request.urlopen(assembeled_request)
		source = result.read()
		# pass the html code
		bs_tree = bs4.BeautifulSoup(source)
		# See how many jobs we found
		job_count_string = bs_tree.find(id = 'searchCount').contents[0]
		print (job_count_string)
		# Getting the last digit 
		job_count_string = job_count_string.split()[-1]
		print (job_count_string)
		job_count_digits = [int(d) for d in job_count_string if d.isdigit()]
		job_count = np.sum([digit*(10**exponent) for digit, exponent in 
							zip(job_count_digits[::-1], range(len(job_count_digits)))])
		print (job_count)
		num_pages = int(np.ceil(job_count/10.0))

		base_url = 'http://www.indeed.com'
		job_links = []
		job_titles = []   
		location = []
		for i in range(2): # do range(num_pages) if you want them all
			if i%10 == 0:
				print (num_pages-i)
			url = url+'&start=' + str(i*10)
			req = urllib.request.Request(url)
			result = urllib.request.urlopen(req)
			html_page = result.read()
			bs_tree = bs4.BeautifulSoup(html_page)
			job_link_area = bs_tree.find(id = 'resultsCol')
			job_postings = job_link_area.findAll('div')
			
			job_postings = [jp for jp in job_postings if not jp.get('class') is None
							and ''. join(jp.get('class')) == 'rowresult']
				
			job_ids = [jp.get('data-jk') for jp in job_postings]
			
			# Going after each link
			for id in job_ids:
				job_links.append(base_url + '/rc/clk?jk=' +id)        
			 
			for tag in job_postings:
				h2_tags = tag.findAll('h2')
				span_tags = tag.findAll('span', {"class":"location"})[0].string
				for h2 in h2_tags:
					a_tag = h2.findAll('a')
					job_titles.append([jp.get('title') for jp in a_tag if not jp.get('class') is None])
				location.append(span_tags)        
			time.sleep(1)
			print (job_links)
			print (job_titles)
			job_list = []
			for i in range(9):
				print (job_titles[i][0])
				job_list.append(Job(str(job_titles[i][0]),str(job_links[i]),str(location[i])))
			for jobb in job_list:
				print ("jobs in the list .............")
				print (jobb.title)
				print (jobb.location)
	#n = math.ceil(len(job_links)/3)			
	skl_set = go_to_links(job_links[:5])
	
	return render(request,'search/query_results.html',{'job_list':job_list,'skl_set':skl_set})

			
