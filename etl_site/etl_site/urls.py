"""etl_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from etl import views as etl_views
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', admin.site.urls),
    url(r'^$', etl_views.form),
    url(r'^ajax/create-table/$', etl_views.create_table),
    url(r'^manage-table/$', etl_views.manage_table),
    url(r'^download/$', etl_views.download),
    url(r'^ajax/get-sql/$', etl_views.get_sql_file),
]
