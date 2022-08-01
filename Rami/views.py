from django.shortcuts import render
from django.core.files.storage import default_storage
from ramiXMLParser import ramiXMLParser
import random
import os
import pandas as pd
from cockpitProcessing.cockpitProcessing import cockpitDailyPlots, focusbuttons, compute, cockpitWeeklyPlots

instruments = {'WeighScale': 'Productivity', 'Counter': 'Productivity',
               'Odometer': 'Efficiency', 'Timer': 'Efficiency'}
kpis = {"Productivity": ["Total Throughput", "Mean Throughput "],
        "Efficiency": ["Total Fuel Efficiency", "Operational Fuel Efficiency",
                       "Total Distance", "Average Distance", "Average Fuel Efficiency"]}


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
            standard = {'Weight (Tons)': 'WeighScale', 'ItemCount': 'Counter', 'distance': 'Odometer'}
            attention = {'Elapsed_Sec': 'Timer'}
            return render(request, "cockpit.html", context={"kpi": kpi, 'standard': standard.items(),
                                                            'attention': attention.items(),
                                                            'focus_text': focus_text, 'display': True})
    return render(request, "cockpit.html", context={"kpi": kpi, 'display': display})


def index(request):
    return render(request, 'index.html')


def widgetkpi(request, instrument):
    if request.method == 'POST':
        okr = request.POST['OKR']
        kpi = request.POST['KPIs']
        tkpis = kpis[okr]
        context = {'instrument': instrument, 'okr': okr, 'kpi': tkpis, 'skpi': kpi}
        return render(request, 'widgetkpi.html', context)
    okr = instruments[instrument]
    kpi = kpis[okr]
    context = {'instrument': instrument, 'okr': okr, 'kpi': kpi}
    return render(request, 'widgetkpi.html', context)


def kpidef(request, instrument, kpi):
    definition = 'Distance travelled'
    values = '456'
    formulae = 'acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371'
    references = "https://www.meridianoutpost.com/resources/etools/calculators/calculator-latitude-longitude-distance" \
                 ".php? "

    if kpi.find('Distance') > 0:
        context = {"kpi": kpi, 'definition': definition, 'values': values,
                   'formulae': formulae, 'references': references}
    else:
        context = {"kpi": kpi}
    return render(request, 'kpidef.html', context)
