"""global_sample_python URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import global_sample_python.views

urlpatterns = [
    path('', global_sample_python.views.order, name='order'),
    path('order_confirm', global_sample_python.views.order_confirm, name='order_confirm'),
    path('order_billingKey', global_sample_python.views.order_billingKey, name='order_billingKey'),
    path('result', global_sample_python.views.order_result, name='order_result'),
    path('auth', global_sample_python.views.authenticate, name='auth'),
    path('payBillkey', global_sample_python.views.payBillkey, name='payBillkey'),
    path('cancel', global_sample_python.views.cancel, name='cancel'),
]
