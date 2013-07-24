from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin')
def temp_home(request):
	return render(request, 'fara_feed/temp_home.html')

@login_required(login_url='/admin')
def instructions(request):
	return render(request, 'FaraData/instructions.html')

