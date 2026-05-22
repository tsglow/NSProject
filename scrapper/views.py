from django.shortcuts import render
from django.http import JsonResponse
from scrapper.scrap import init
# Create your views here.

def index(request):    
    return render(request, 'scrapper/index.html')

async def get_data(request):
    articles = {'article' : init()}    
    return JsonResponse(articles)

def get_test(request):
    articles = {'article' : init()}    
    return JsonResponse(articles)