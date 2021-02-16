from django.shortcuts import render

def home(request):
    return render(request, 'appname/home.html')
