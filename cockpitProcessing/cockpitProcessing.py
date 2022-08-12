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


def compute(machine_id):
    df = pd.read_excel('QC-KPIs.xlsx', engine='openpyxl', sheet_name='Synth')

    df_new = df.groupby(['machine_id', 'StartDate'])[['Elapsed_Sec',
                                                      'Distance',
                                                      'ItemCount', 'Weight (Tons)',
                                                      'FuelConsumption', 'RepairCost']].sum().loc[machine_id, :]
    df_new.loc['Total'] = df_new.sum(axis=0)
    df_new.to_csv('outputdf.csv')
    return df_new


def cockpitDailyPlots(columns):
    df = pd.read_csv('outputdf.csv')
    result={}
    df = df.iloc[:8, :]
    df['StartDate'] = df['StartDate'].apply(lambda x: x.split(' ')[0])
    for i in columns:
        data=[[df['StartDate'][j], df[i][j]] for j in range(df.shape[0])][::-1]
        data.insert(0, ['Date', 'Value'])
        result[i]=data
    return result


def cockpitWeeklyPlots(columns):
    df = pd.read_csv('outputdf.csv')
    result = {}
    total = df.iloc[8, :].to_dict()
    df = df.iloc[:8, :]
    df['StartDate'] = df['StartDate'].apply(lambda x: x.split(' ')[0])
    for i in columns:
        data = [['Max', abs(df[i].max())], ['Total', abs(total[i])]]
        data.insert(0, ['Measure', 'value'])
        result[i] = data
    return result


def focusbuttons(columns):
    df = pd.read_csv('outputdf.csv')
    df = df.iloc[:8, :]
    df['StartDate'] = df['StartDate'].apply(lambda x: x.split(' ')[0])
    hover_text = {}
    for i in columns:
        txt = []
        for j in range(df[i].shape[0] - 1):
            val = (df[i][j+1]-df[i][j])/df[i][j]
            if val > 0.40:
                txt.append(
                    f'From {df["StartDate"][j]} to {df["StartDate"][j + 1]} it increased {round(val * 100, 2)} %')
            if val < -0.40:
                txt.append(
                    f'From {df["StartDate"][j]} to {df["StartDate"][j + 1]} it decreased {round(val * 100, 2)} %')
        hover_text[i] = ' '.join(txt)
    focus_text = zip(hover_text.keys(), hover_text.values())
    return focus_text