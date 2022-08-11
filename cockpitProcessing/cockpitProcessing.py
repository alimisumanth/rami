# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 23-07-2022 04:59 PM
Created by: ASK
=============================================================================

Project Name: Rami

File Name: cockpitProcessing.py

Description:

Version:

Revision:

=============================================================================
"""

from multiprocessing import Process
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns


def compute(machine_id):
    df = pd.read_excel('QC-KPIs.xlsx', engine='openpyxl', sheet_name='Synth')

    df_new = df.groupby(['machine_id', 'StartDate'])[['Elapsed_Sec',
                                                      'Distance',
                                                      'ItemCount', 'Weight (Tons)',
                                                      'FuelConsumption', 'RepairCost']].sum().loc[machine_id, :]
    df_new.loc['Total'] = df_new.sum(axis=0)
    df_new.to_csv('outputdf.csv')
    return df_new


def cockpitDailyPlots(df):
    df.reset_index(inplace=True)
    df['StartDate'] = pd.to_datetime(df['StartDate']).dt.date
    print(df.head(7))
    for i in ['Weight (Tons)', 'Elapsed_Sec', 'ItemCount', 'Distance', 'FuelConsumption', 'RepairCost']:
        plt.figure(figsize=(16, 8))
        sns.barplot(x=df['StartDate'], y=df[i])
        plt.xticks(rotation=30)
        plt.savefig(os.path.join('static', 'output',  i + '.png'))


def cockpitWeeklyPlots(df, total):
    df.reset_index(inplace=True)
    df['StartDate'] = pd.to_datetime(df['StartDate']).dt.date
    for i in ['Weight (Tons)', 'Elapsed_Sec', 'ItemCount', 'Distance', 'FuelConsumption', 'RepairCost']:
        if i != 'Elapsed_Sec':
            val = (df[i].max()/total[i])*100
            data = [val, 100 - val]
            print(val, df[i].max(), total[i])
            label = ['max', '']
            explode = [0.1, 0]
        else:
            val = (total[i]/df[i].max())*100
            data = [abs(val), abs(100 - val)]
            print(val, df[i].max(), total[i])
            label = ['', 'max']
            explode = [0, 0.1]

        plt.figure(figsize=(16, 8))
        palette_color = sns.color_palette('bright')
        plt.pie(data, labels=label, colors=palette_color, explode=explode, autopct='%.0f%%')
        plt.savefig(os.path.join('static', 'output',  i + '.png'))


def focusbuttons(df):
    hover_text = {}
    fields = df.columns[1:]
    for i in fields:
        txt = []
        for j in range(df[i].shape[0] - 1):

            val = (df[i][j+1]-df[i][j])/df[i][j]
            if val > 0.40:
                print(f'From {df["StartDate"][j]} to {df["StartDate"][j + 1]} it increased {val} %')
                txt.append(
                    f'From {df["StartDate"][j]} to {df["StartDate"][j + 1]} it increased {round(val * 100, 2)} %')
            if val < -0.40:
                txt.append(
                    f'From {df["StartDate"][j]} to {df["StartDate"][j + 1]} it decreased {round(val * 100, 2)} %')
        hover_text[i] = ' '.join(txt)
    focus_text = zip(hover_text.keys(), hover_text.values())
    return focus_text