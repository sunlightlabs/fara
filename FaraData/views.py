from django.shortcuts import render

def temp_home(request):
	return render(request, 'temp_home.html')

def instructions(request):
	return render(request, 'FaraData/instructions.html')