# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 25-06-2022 01:28 PM
Created by: ASK
=============================================================================

Project Name: Rami

File Name: ramiXMLParser.py

Description:

Version:

Revision:

=============================================================================
"""
import xml.etree.ElementTree as ET


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


def ramiXMLParser(document):
    path = f'uploads/{document}'

    document = ET.parse(path)

    rootEle, vertical = getVertical(document)

    asset = [(i, i.attrib.get('items')) for i in rootEle.findall('asset')]

    items = [(i.text, list(i.attrib.values())[0]) for i in rootEle.find('asset').findall('Item')]

    devices = dict()

    for item in items:
        devices[item[0]] = item[1]

    return vertical, devices
