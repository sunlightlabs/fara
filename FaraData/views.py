from django.shortcuts import render

def temp_home(request):
	return render(request, 'temp_home.html')