# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 08-08-2022 11:01 AM
Created by: ASK
=============================================================================

Project Name: Rami

File Name: forms.py

Description:

Version:

Revision:

=============================================================================
"""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class Users(UserCreationForm):
    """
    Users form is used to create new users which is used for authentication
    """
    class Metha:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
