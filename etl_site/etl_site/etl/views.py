# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

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
			return HttpResponseRedirect('/create-table')
    else:
		form = FileForm()

    return render(request,
    	'form.html',
    	{'form': form})

def create_table(request, table_instance):
    active_id = request.session.get('active_instance')
    sql_table = sql(table_model.objects.get(id=active_id))
    json_string = sql_table.get_json()
    return render(request, 'create-table.html', json_string)


