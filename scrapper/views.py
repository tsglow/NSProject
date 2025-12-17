from django.shortcuts import render
from django.http import HttpResponse
from scrapper.scrap import scrap
import datetime
# Create your views here.
def index(request):
    #datetime.datetime.strptime(i.pubDate, '%Y-%m-%d %H:%M:%S'
    context = {'article' : scrap()}
    #print(context)
    template_name='scrapper/index.html'
        #return HttpResponse("let's scrap")
    return render(request, template_name, context)