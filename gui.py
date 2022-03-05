# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 17:44:27 2022

@author: DGrishchuk
"""

from pathlib import Path
import PySimpleGUI as sg
import threading
import logging

from settings import STATUS
from utils import download_all


def update_info(window):
    if STATUS['has_updates']:
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
            value=(
                f'Current folder: {STATUS["current_folder"]}\n'
                f'Current file: {STATUS["current_file"]}')
            )
        STATUS['has_updates'] = False


def main_thread(window, archive_path, save_path):
    download_all(archive_path, save_path)
    window.write_event_value('-THREAD-', 'Everything done')


def gui():
    sg.theme('Light Blue 1')

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
        [sg.HorizontalSeparator()],
        [sg.Multiline(size=(5, 20), autoscroll=True, expand_x=True,
                      key='-OUTPUT-')],
        [sg.HorizontalSeparator()],
        [sg.Button('Start', key='-START-'),
         sg.Checkbox('Close when done', k='-E-', enable_events=True)]
        ]

    window = sg.Window('FetchVK', layout, icon='icon.ico')

    try:
        while True:
            event, values = window.read(timeout=500)
            update_info(window)
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
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
                    logging.info(f'{archive_path} is not a zip archive')
                    continue
                if not archive_path.exists():
                    logging.info(f'{archive_path} does not exist')
                    continue
                if not save_path.exists():
                    logging.info(f'{save_path} does not exist')
                    continue
                mt = threading.Thread(target=main_thread,
                                      args=(window, archive_path, save_path,),
                                      daemon=True)
                mt.start()
                window['-AP-'].update(disabled=True)
                window['-SP-'].update(disabled=True)
                window['-F-'].update(disabled=True)
                window['-FPB-'].update(disabled=True)
                window['-APB-'].update(disabled=True)
                window['-SPB-'].update(disabled=True)
                window['-START-'].update(disabled=True)
            elif event == '-THREAD-':
                logging.info(values[event])
                mt.join()
                if values['-E-']:
                    break
                else:
                    window['-AP-'].update(disabled=False)
                    window['-SP-'].update(disabled=False)
                    window['-F-'].update(disabled=False)
                    window['-FPB-'].update(disabled=False)
                    window['-APB-'].update(disabled=False)
                    window['-SPB-'].update(disabled=False)
                    window['-START-'].update(disabled=False)
    except Exception as e:
        logging.info(e)
    finally:
        window.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(message)s',
                        level=logging.INFO)
    gui()
