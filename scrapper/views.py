from django.shortcuts import render
from django.http import HttpResponse
from scrapper.scrap import scrap
# Create your views here.
def index(request):
    context = {'article' : scrap()}
    #print(context)
    template_name='scrapper/index.html'
    #return HttpResponse("let's scrap")
    return render(request, template_name, context)