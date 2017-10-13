# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from .forms import FileForm
from .models import Table as table_model
from .helpers import sql_table as sql

# Create your views here.
def form(request):
	if request.method == 'POST':
		form = FileForm(request.POST, request.FILES)
		if form.is_valid():
			table_instance = table_model(raw_file=request.FILES['raw_file'])
			table_instance.save()
			request.session['active_instance'] = table_instance.get_id()
			return HttpResponseRedirect('/manage-table/')
	else:
		form = FileForm()

	return render(request,
		'form.html',
		{'form': form})

def create_table(request):
	active_id = request.session.get('active_instance')
	sql_table = sql(table_model.objects.get(id=active_id))
	return JsonResponse(sql_table.get_json())

def manage_table(request):
	return render(request,
		'manage-table.html')
	'''
	if request.method == 'POST':
		form = FileForm(request.POST, request.FILES)
		if form.is_valid():
			table_instance = table_model(raw_file=request.FILES['raw_file'])
			table_instance.save()
			request.session['active_instance'] = table_instance.get_id()
			return HttpResponseRedirect('/manage-table/')
	else:
		form = FileForm()

	return render(request,
		'form.html',
		{'form': form})
	'''

def download(request):
	pass