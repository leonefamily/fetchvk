# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 20:41:03 2022

@author: DGrishchuk
"""

from datetime import datetime as dt, timedelta as td

STATUS = {
    'has_updates': False,
    'current_folder': '',
    'current_file': '',
    'folders_count': 0,
    'folder_files_count': 0,
    'file_items_count': 0,
    'folder_num': 0,
    'file_num': 0,
    'item_num': 0,
    'warns': [],
    'errors': [],
    'info': [],
    'done': [],
    'notice': [],
    'verbose': True,
    'username': None,
    'password': None,
    'last_update': dt.now(),
    'ping_every': td(seconds=120),
    'ping': True
    }

COLORS = {
    'warns': 'orange',
    'errors': 'red',
    'info': 'black',
    'done': 'green',
    'notice': 'gray',
    }

DEFAULT_STATUS = {k: v for k, v in STATUS.items() if k not in ['verbose',
                                                               'username',
                                                               'password']}
