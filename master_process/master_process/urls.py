"""master_process URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from uuid import uuid4

from master_app.models import LapMessage
from master_app.views import pos_message
from master_process.constants import Constants

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pos_message/', pos_message),
]

settings.REDIS_DB.set(Constants.PROCESS_ID, str(uuid4()))
LapMessage.send_new_message_to_racers()
