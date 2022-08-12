# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 02-08-2022 07:47 AM
Created by: ASK
=============================================================================

Project Name: Rami

File Name: widgetKpiProcessing.py

Description:

Version:

Revision:

=============================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math


def wigetDailyPlots(column):
    df = pd.read_csv('outputdf.csv')
    average = df[column] / 8
    data = average[:8]
    df = df.iloc[:8, :]
    df['StartDate'] = df['StartDate'].apply(lambda x: x.split(' ')[0])
    result=[[df['StartDate'][j], data[j]] for j in range(df.shape[0])][::-1]
    result.insert(0, ['Date', 'Value'])
    return result


def wigetprocessing(kpi):
    df=pd.read_csv('outputdf.csv')
    average=df[kpi]/8
    data=average[:8]
    plt.figure(figsize=(16, 8))
    sns.barplot(x=df['StartDate'][0:8], y=data)
    plt.xticks(rotation=30)
    plt.savefig(os.path.join('static', 'output', 'Average ' + kpi + '.png'))
    return 'Average '+str(kpi)

def getColor(kpi):
    df = pd.read_csv('outputdf.csv')
    total = df[kpi][8]
    maxi= max(df[kpi][:8])*8
    percent=round((total/maxi)*100)
    if percent>=61:
        color='green'
    elif percent==60:
        color='orange'
    else:
        color='red'
    return color