# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 25-06-2022 01:28 PM
Created by: ASK
=============================================================================

Project Name: Rami

File Name: parse.py

Description:

Version:

Revision:

=============================================================================
"""
import xml.etree.ElementTree as ET

device_codes = {"Appliances": "AP", "Buildings": "BU", "Boiler": "BO", "Heating": "HE", "Lighting": "LI",
                "Motors": "MO", "RoboticArms": "RA", "RollerBelts": "RB", "SecurityDevices": "SD", "New": "NW",
                "Trucks": "TR", "Berths": "BE", "QuayCranes": 'QC'}


def getVertical(obj):
    """
        Method Name : getVertical
        Description : This method is used to get the root element object and the vertical of the document
        Parameters  : Obj - XML object
        Returns     : root- root element object, vertical - vertical of the document
        Raises      : None
    """

    root = obj.getroot()
    vertical = root.attrib.get('vertical')
    return root, vertical


def parse():
    path = f'uploads/rami.xlsx'

    document = ET.parse(path)

    rootEle, vertical = getVertical(document)

    asset = [(i, i.attrib.get('items')) for i in rootEle.findall('asset')]

    items = [(i.text, list(i.attrib.values())[0]) for i in rootEle.find('asset').findall('Item')]

    devices = dict()

    for item in items:
        devices[item[0]] = item[1]

    return vertical, devices


def getLabels(devices):
    count = {}
    for i in set(devices):
        count[i] = 0
    label = []
    for i in devices:
        count[i] = int(count[i]) + 1
        label.append(f"{device_codes[i]}{(3 - len(str(count[i]))) * '0'}{count[i]}")
    return label
