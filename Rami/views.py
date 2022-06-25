from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from ramiXMLParser import ramiXMLParser
import random

def ramiParser(request):
    if request.method == 'POST':
        file = request.FILES['rami']
        with default_storage.open('uploads/' + file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        vertical, res = ramiXMLParser.ramiXMLParser(file.name)
        devices=[]
        for i in res:
            for j in range(int(res[i])):
                devices.append(i)
        random.shuffle(devices)
        return render(request, 'rami.html', context={'res': devices, 'vertical': vertical})


def index(request):

    return render(request,'index.html')
