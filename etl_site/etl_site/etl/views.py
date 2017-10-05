# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import FileForm
from .models import Table as table_model

# Create your views here.
def form(request):
    if request.method == 'POST':
		form = FileForm(request.POST, request.FILES)
		if form.is_valid():
			table_instance = table_model(raw_file=request.FILES['raw_file'])
			table_instance.save()
			return HttpResponseRedirect('/success')
    else:
		form = FileForm()

    return render(request,
    	'form.html',
    	{'form': form}
    )

def success(request):
    return render(
		request,
		'success.html'
    )