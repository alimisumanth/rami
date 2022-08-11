from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from ramiXMLParser import ramiXMLParser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import Users
import random
import os
import pandas as pd
from widgetKpiProcessong.widgetKpiProcessing import wigetprocessing, getColor
from cockpitProcessing.cockpitProcessing import cockpitDailyPlots, focusbuttons, compute, cockpitWeeklyPlots

instruments = {'WeighScale': 'Productivity', 'Counter': 'Productivity',
               'Odometer': 'Efficiency', 'Timer': 'Efficiency', 'FuelMeter': 'Efficiency',
               'AssetMetric': 'Accounts', 'AssetStatus': 'AssetTracker'}

kpis = {"Productivity": ["Total Throughput", "Average Throughput"],
        "Efficiency_odo": ["Total Distance", "Average Distance"],
        "Efficiency_fuel": ["Total Fuel Efficiency", "Average Fuel Efficiency"],
        "Efficiency_Time": ["Total Time", "Average Time"],
        'Accounts': ['Total RepairCost', 'Average RepairCost'],
        'AssetTracker': ["AssetLifetime", 'AssetFailures', 'AssetRepairs']}


def signUp(request):
    """
    This method is used for registering a new user
    """
    if request.method == 'POST':
        userForm = Users(request.POST)
        if userForm.is_valid():
            username = userForm.cleaned_data['username']
            userForm.save()
            messages.info(request, f'user {username} created')
            return redirect('login')
        else:
            messages.error(request, userForm.errors)
            return redirect('register')
    return render(request, 'registration.html')


def signin(request):
    """
    This method is used for user login
    """
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Username or Password is invalid')
            return redirect('login')
        else:
            login(request, user)
        request.session['user'] = username
        return render(request, 'index.html', context={'user': user})
    return render(request, 'login.html')


def signOut(request):
    """This method is used for logging out """
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')


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
            request.session['time'] = time
            if time == 'day':
                df.drop('Total', axis=0, inplace=True)
                cockpitDailyPlots(df)
            else:
                total = df.loc['Total'].to_dict()
                df.drop('Total', axis=0, inplace=True)
                cockpitWeeklyPlots(df, total)

            focus_text = focusbuttons(df)
            if request.session['user'] == 'Alun':
                standard = {'RepairCost': 'AssetMetric'}
                context = {'display': True, 'standard': standard.items()}
                return render(request, "cockpit.html", context)
            standard = {'Weight (Tons)': 'WeighScale', 'ItemCount': 'Counter', 'Distance': 'Odometer',
                        'FuelConsumption': 'FuelMeter'}
            attention = {'Elapsed_Sec': 'Timer'}
            return render(request, "cockpit.html", context={"kpi": kpi, 'standard': standard.items(),
                                                            'attention': attention.items(),
                                                            'focus_text': focus_text, 'display': True})
    return render(request, "cockpit.html", context={"kpi": kpi, 'display': display})


@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')


def widgetkpi(request, instrument):
    if request.method == 'POST':
        okr = request.POST['OKR']
        kpi = request.POST['KPIs']
        time = request.session['time']
        if instrument == 'Odometer':
            tkpis = kpis['Efficiency_odo']
        elif instrument == 'FuelMeter':
            tkpis = kpis['Efficiency_fuel']
        elif instrument == 'Timer':
            tkpis = kpis['Efficiency_Time']
        else:
            tkpis = kpis[okr]
        skpi = kpi
        kpi_ = None
        if kpi.find('Total') >= 0:
            kpi = kpi.replace('Total ', '')
            if instrument == 'WeighScale' and kpi == 'Throughput':
                graph = "Weight (Tons)"
                kpi_ = "Weight (Tons)"
            elif instrument == 'Counter' and kpi == 'Throughput':
                graph = 'ItemCount'
                kpi_ = 'ItemCount'
            elif instrument == 'Odometer':
                graph = 'Distance'
                kpi_ = 'Distance'
            elif instrument == 'Timer':
                graph = 'Elapsed_Sec'
                kpi_ = 'Elapsed_Sec'
            elif instrument == 'FuelMeter':
                graph = 'FuelConsumption'
                kpi_ = 'FuelConsumption'
            elif instrument == 'AssetMetric' and kpi == 'RepairCost':
                graph = 'RepairCost'
                kpi_ = 'RepairCost'
        if kpi.find('Average') >= 0:
            kpi = kpi.replace('Average ', '')
            if kpi == 'Throughput' and instrument == 'WeighScale':
                kpi_ = 'Weight (Tons)'
            elif kpi == 'Throughput' and instrument == 'Counter':
                kpi_ = 'ItemCount'
            elif kpi == 'Distance':
                kpi_ = 'Distance'
            elif kpi == 'Fuel Efficiency':
                kpi_ = 'FuelConsumption'
            elif kpi == 'RepairCost':
                kpi_ = 'RepairCost'
            elif kpi == 'Time':
                kpi_ = 'Elapsed_Sec'
            if time == 'day':
                graph = wigetprocessing(kpi_)
            else:
                df = pd.read_csv('outputdf.csv')
                data = df[kpi_][8] / 8
                color = getColor(kpi_)

                context = {'instrument': instrument, 'okr': okr, 'kpi': tkpis, 'skpi': skpi, 'data': data,
                           'color': color}
                return render(request, 'widgetkpi.html', context)
        color = getColor(kpi_)
        context = {'instrument': instrument, 'okr': okr, 'kpi': tkpis, 'skpi': skpi, 'graph': graph, 'color': color}
        return render(request, 'widgetkpi.html', context)
    okr = instruments[instrument]
    if instrument == 'Odometer':
        kpi = kpis['Efficiency_odo']
    elif instrument == 'FuelMeter':
        kpi = kpis['Efficiency_fuel']
    elif instrument == 'Timer':
        kpi = kpis['Efficiency_Time']
    else:
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
