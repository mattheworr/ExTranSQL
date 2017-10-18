# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from wsgiref.util import FileWrapper
from pickle import dumps, loads

from .forms import FileForm
from .models import Table as table_model
from .helpers import sql_table as sql

# Create your views here.
def form(request):
	request.session.flush()
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
	request.session['sql_table'] = dumps(sql_table)
	return JsonResponse(sql_table.get_json())

def manage_table(request):
	if request.method == 'POST':
		loads(request.session.get('sql_table')).get_sql(
			request.POST['table_name'], 
			request.POST.getlist('column_name'), 
			request.POST.getlist('datatype'))
		return HttpResponseRedirect('/download/')

	return render(request,
		'manage-table.html')

def download(request):
	return render(request,
		'download.html')

def get_sql_file(request):
	active_id = request.session.get('active_instance')
	table_instance = table_model.objects.get(id=active_id)
	response = HttpResponseRedirect(table_instance.get_export_file())
	response['Content-Disposition'] = 'attachment; filename={0}.sql'.format(
		table_instance.get_table_name())
	return response

