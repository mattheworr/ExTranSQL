# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import FileForm

# Create your views here.
def form(request):
    if request.method == 'POST':
		form = FileForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/success/')
    else:
		form = FileForm()

    return render(request,
    	'form.html',
    	{'form': form}
    )

def process(request):
    return render(
    	request,
    	'success.html'
    )