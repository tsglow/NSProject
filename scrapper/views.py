import asyncio
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from scrapper.scrap import scrap
# Create your views here.

def index(request):    
    return render(request, 'scrapper/index.html')

async def get_data(request):
    articles = {'article' : scrap()}    
    return JsonResponse(articles)