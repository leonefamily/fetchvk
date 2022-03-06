# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 17:44:27 2022

@author: DGrishchuk
"""

from datetime import datetime as dt
from pathlib import Path
import PySimpleGUI as sg
import threading
import traceback
import logging
import time

from settings import STATUS, COLORS
from utils import download_all, _send_status

HIDEABLE = ['-AP-', '-SP-', '-F-', '-FPB-',
            '-APB-', '-SPB-', '-START-', '-PHOTO-', '-VIDEO-']

EXCLUDE_MAP = {
    '-VIDEO-': 'vids_path',
    '-PHOTO-': 'imgs_path',
    }


def _disabled(window, state=True):
    for key in HIDEABLE:
        window[key].update(disabled=state)


def _exclude_acts(values):
    return [EXCLUDE_MAP[k] for k, v in values.items() if k in EXCLUDE_MAP and not v]


def update_info(window, force=False):
    if STATUS['has_updates'] or force:
        window['-FOLDERS-'].update(current_count=STATUS['folder_num'],
                                   max=STATUS['folders_count'])
        window['-FO-'].update(
            value=f'Folders: {STATUS["folder_num"]} / {STATUS["folders_count"]}')
        window['-FILES-'].update(current_count=STATUS['file_num'],
                                 max=STATUS['folder_files_count'])
        window['-FI-'].update(
            value=f'Files: {STATUS["file_num"]} / {STATUS["folder_files_count"]}')
        window['-ITEMS-'].update(current_count=STATUS['item_num'],
                                 max=STATUS['file_items_count'])
        window['-IT-'].update(
            value=f'Items: {STATUS["item_num"]} / {STATUS["file_items_count"]}')
        window['-INFO-'].update(
            value=(f'Current folder: {STATUS["current_folder"]}\n'
                   f'Current file: {STATUS["current_file"]}')
            )
        if STATUS['verbose']:
            color_print_info('info', window)
            color_print_info('notice', window)
        color_print_info('done', window)
        color_print_info('warns', window)
        color_print_info('errors', window)
        STATUS['has_updates'] = False


def color_print_info(key, window, max_len=30):
    if len(STATUS[key]) > max_len:
        sg.cprint(
            f'........Omittied {len(STATUS[key]) - max_len} messages........',
            text_color='orange')
    sg.cprint(''.join(STATUS[key][-max_len:]),
              text_color=COLORS[key], end='')
    STATUS[key].clear()


def main_thread(window, archive_path, save_path, exclude):
    download_all(archive_path, save_path, exclude)
    window.write_event_value('-THREAD-', '')


def not_dead():
    STATUS['ping'] = True
    while STATUS['ping']:
        if (dt.now() - STATUS['last_update']) > STATUS['ping_every']:
            _send_status('Program is not frozen, processing')
        time.sleep(STATUS['ping_every'].total_seconds())


def generate_layout():
    layout = [
        [sg.T('Input paths to directories and press Start')],
        [sg.I('', key='-AP-', expand_x=True),
         sg.FileBrowse('Choose VK archive', key='-APB-', size=(20, 1)),
         sg.FolderBrowse('Choose VK folder', target='-AP-', key='-FPB-',
                         size=(20, 1), visible=False, enable_events=True)],
        [sg.T('', expand_x=True),
         sg.Checkbox('Archive is a folder', k='-F-', enable_events=True)],
        [sg.I('', key='-SP-', expand_x=True),
         sg.FolderBrowse('Choose save path', key='-SPB-', size=(20, 1))],
        [sg.T('Folders:', size=12, key='-FO-'),
         sg.PBar(1, size=(1, 10), expand_x=True, key='-FOLDERS-')],
        [sg.T('Files:', size=12, key='-FI-'),
         sg.PBar(1, size=(1, 10), expand_x=True, key='-FILES-')],
        [sg.T('Items:', size=12, key='-IT-'),
         sg.PBar(1, size=(1, 10), expand_x=True, key='-ITEMS-')],
        [sg.T('', key='-INFO-')],
        [sg.Multiline(size=(20, 10), autoscroll=True, expand_x=True,
                      key='-OUTPUT-')],
        [sg.Frame('What to download',
                  [[sg.Checkbox('Photo', k='-PHOTO-', default=True),
                    sg.Checkbox('Video', k='-VIDEO-', default=True)]],
                  expand_x=True)],
        [sg.Button('Start', key='-START-'),
         sg.Checkbox('Close when done', k='-E-', enable_events=True),
         sg.Checkbox('Verbose', k='-V-', enable_events=True, default=True)]
        ]
    return layout


def gui():
    sg.theme('Light Blue 1')
    window = sg.Window('fetchvk', generate_layout(), icon='icon.ico')
    sg.cprint_set_output_destination(window, '-OUTPUT-')
    window.read(timeout=0)
    update_info(window, force=True)
    try:
        while True:
            event, values = window.read(timeout=500)
            update_info(window)
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == '-V-':
                STATUS['verbose'] = not STATUS['verbose']
            elif event == '-F-':
                window['-APB-'].update(visible=not values[event])
                window['-FPB-'].update(visible=values[event])
            elif event == '-SPB-':
                window['-SP-'].update(values[event])
            elif event == '-APB-' or event == '-FPB-':
                window['-AP-'].update(values[event])
            elif event == '-START-':
                archive_path = Path(values['-AP-'])
                save_path = Path(values['-SP-'])
                if archive_path.suffix != '.zip' and not values['-F-']:
                    _send_status(f'{archive_path} is not a zip archive', 'errors')
                    continue
                if not archive_path.exists():
                    _send_status(f'{archive_path} does not exist', 'errors')
                    continue
                if not save_path.exists():
                    _send_status(f'{save_path} does not exist', 'errors')
                    continue
                exclude = _exclude_acts(values)
                if len(exclude) == len(EXCLUDE_MAP):
                    _send_status('At least one has to be chosen', 'errors')
                    continue
                mt = threading.Thread(target=main_thread,
                                      args=(window, archive_path, save_path,
                                            exclude if exclude else None,),
                                      daemon=True)
                nd = threading.Thread(target=not_dead, daemon=True)
                mt.start(), nd.start()
                _disabled(window, state=True)
            elif event == '-THREAD-':
                _send_status('Everything is done!', 'done')
                mt.join(), nd.join()
                if values['-E-']:
                    break
                else:
                    _disabled(window, state=False)
            elif event == '-INTERRUPT-':
                _send_status('Programm is interrupted', 'warns')
                mt.join(), nd.join()
                if values['-E-']:
                    break
                else:
                    _disabled(window, state=False)
    except Exception:
        _send_status(traceback.format_exc(), 'errors')
    finally:
        if 'mt' in locals():
            mt.join()
        if 'nd' in locals():
            nd.join()
        window.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(message)s',
                        level=logging.INFO)
    gui()
