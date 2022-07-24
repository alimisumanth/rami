from django.shortcuts import render
from django.core.files.storage import default_storage
from ramiXMLParser import ramiXMLParser
import random
import os
import pandas as pd
from cockpitProcessing.cockpitProcessing import cockpitDailyPlots, focusbuttons, compute, cockpitWeeklyPlots


def ramiParser(request):
    if request.method == 'POST':
        file = request.FILES['rami']
        with default_storage.open('uploads/' + file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        vertical, res = ramiXMLParser.parse(file.name)
        summary = [f'Number of {i} = {res[i]}' for i in res]
        devices = []
        imgs = [str(i)[:-4] for i in os.listdir('static/images')]
        new_device = []
        for i in res:
            if i not in imgs:
                new_device.append(i)
                continue
            for j in range(int(res[i])):
                devices.append(i)
        random.shuffle(devices)
        labels = ramiXMLParser.getLabels(devices)
        devices = zip(devices, labels)

        return render(request, 'rami.html', context={'devices': devices, 'vertical': vertical, 'summary': summary,
                                                     'new_device': ','.join(new_device)})


def ramikpi(request, kpi):
    display = False
    if request.method == 'POST':
        time = request.POST['time']
        if str(kpi).startswith('QC'):
            df = compute(kpi)
            if time == 'day':
                df.drop('Total', axis=0, inplace=True)
                cockpitDailyPlots(df)
            else:
                total = df.loc['Total'].to_dict()
                df.drop('Total', axis=0, inplace=True)
                cockpitWeeklyPlots(df, total)
            focus_text = focusbuttons(df)
            standard = {'Weight (Tons)': 'Weigh Scale', 'ItemCount': 'Counter', 'distance': ' Odometer'}
            attention = {'Elapsed_Sec': 'Timer '}
            return render(request, "cockpit.html", context={"kpi": kpi, 'standard': standard.items(),
                                                            'attention': attention.items(),
                                                            'focus_text': focus_text, 'display': True})
    return render(request, "cockpit.html", context={"kpi": kpi, 'display': display})


def index(request):
    return render(request, 'index.html')


def widgetkpi(request):
    return render(request, 'widgetkpi.html')


def kpidef(request, kpi):
    return render(request, 'kpidef.html', context={"kpi": kpi})

