import requests
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse

from collector.models import Innovation
from googleapiclient.discovery import build
import json

my_key = ''
my_cse_id = ''


# Define views here
class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Bad username or password.')
            return redirect('login')


class IndexView(View):

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user.username
            return render(request, 'index.html', {'user': user})
        return redirect('login')
