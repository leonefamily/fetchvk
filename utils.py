# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 21:15:00 2022

@author: DGrishchuk
"""

from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from urllib.parse import urlparse
from zipfile import ZipFile
from pathlib import Path
import youtube_dl as yd
import requests
import inspect
import urllib
import wget

from settings import STATUS, DEFAULT_STATUS


class Tasks:
    avail = ['imgs_path', 'vids_path']

    def __init__(self, **kwargs):
        for key in kwargs:
            if key not in self.avail:
                raise AttributeError(f'{key} keyword is not supported')
            setattr(self, key, kwargs[key])
        self._set_empty()

    def _set_empty(self):
        for key in self.avail:
            if key not in _get_attrs(self):
                setattr(self, key, None)

    def __str__(self):
        return ', '.join([f'{attr}={val}' for attr, val
                          in _get_attrs(self).items() if attr != 'avail'])

    def __repr__(self):
        return ', '.join([f'{attr}={val}' for attr, val
                          in _get_attrs(self).items() if attr != 'avail'])

    def count(self):
        return len([k for k, v in _get_attrs(self).items() if k != 'avail' and v])


def files_count(path):
    if not Path(path).is_dir():
        _send_status(f'{path} is not a directory', 'errors')
        raise ValueError(f'{path} is not a directory')
    count = 0
    for f in Path(path).iterdir():
        if f.is_file():
            count += 1
    return count


def dirs_count(path):
    if not Path(path).is_dir():
        _send_status(f'{path} is not a directory', 'errors')
        raise ValueError(f'{path} is not a directory')
    count = 0
    for f in Path(path).iterdir():
        if f.is_dir():
            count += 1
    return count


def get_video(url, filename, pathname, un=None, pw=None):
    opts = {
        'outtmpl': f'{pathname}/{filename}.%(ext)s',
        'quiet': True
        }
    with yd.YoutubeDL(opts) as f:
        f.download([url])


def _get_attrs(o):
    attrs = inspect.getmembers(o, lambda a: not(inspect.isroutine(a)))
    return {a[0]: a[1] for a in attrs if not(a[0].startswith('__') and
                                             a[0].endswith('__'))}


def _reset_items_count(items, path):
    STATUS['item_num'] = 0
    STATUS['file_items_count'] = len(items)
    STATUS['current_file'] = path
    STATUS['has_updates'] = True


def _reset_files_count(path):
    STATUS['file_num'] = 0
    STATUS['folder_files_count'] = files_count(path)
    STATUS['current_folder'] = path
    STATUS['has_updates'] = True


def _reset_all_status():
    for key in STATUS:
        if key in DEFAULT_STATUS:
            STATUS[key] = DEFAULT_STATUS[key]
    STATUS['info'].clear()
    STATUS['warns'].clear()
    STATUS['errors'].clear()
    STATUS['has_updates'] = True


def _update_items_count():
    STATUS['last_update'] = dt.now()
    STATUS['item_num'] += 1
    STATUS['has_updates'] = True


def _update_files_count():
    STATUS['last_update'] = dt.now()
    STATUS['file_num'] += 1
    STATUS['has_updates'] = True


def _create_dir(maindir, subdir):
    spath = Path(maindir) / subdir
    if not spath.exists():
        spath.mkdir(parents=True, exist_ok=True)
    return spath


def _send_status(msg, level='info'):
    STATUS[level].append(f"{dt.now()} | {msg}\n")
    STATUS['has_updates'] = True


def download_items(source_path: str, save_path: str, kind: str='img') -> None:
    _reset_files_count(source_path)
    for html_p in Path(source_path).glob('*.html'):
        html_f = load_html_text(html_p)
        if kind == 'vid':
            items, path = get_all_videos_links(html_f)
        elif kind == 'img':
            items, path = get_all_images_links(html_f)
        else:
            raise ValueError(f'{kind} is not valid kind')
        _reset_items_count(items, html_p)
        spath = _create_dir(save_path, path)
        for item in items:
            download(item, str(spath), kind)
            _update_items_count()
        _update_files_count()


def load_html_text(path: str) -> str:
    with open(path, mode='r', encoding='windows-1251') as html:
        return html.read()


def is_valid(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_albums_names(soup, class_="ui_crumb"):
    alb_parts = []
    for part in soup.find_all(class_=class_):
        alb_parts.append(f'{part.contents[0]}')
    return '/'.join(alb_parts)


def get_all_images_links(html: str) -> tuple:
    soup = bs(html, "html.parser")
    urls = []
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        if is_valid(img_url):
            urls.append(img_url)
    return urls, get_albums_names(soup)


def get_all_videos_links(html: str) -> tuple:
    soup = bs(html, "html.parser")
    urls = []
    for el in soup.find_all('a', href=True):
        vid_url = el.attrs['href']
        needed = 'video' in vid_url and 'comments' not in vid_url
        if needed and is_valid(vid_url) and vid_url not in urls:
            urls.append(vid_url)
    return urls, get_albums_names(soup)


def download(url, pathname, kind='img'):
    tries = 0
    while True:
        tries += 1
        try:
            filename = url.split('/')[-1].split('?')[0]
            if kind == 'img':
                if (Path(pathname) / filename).exists():
                    _send_status(f'{filename} exists, skipping')
                    return
            elif kind == 'vid':
                if filename in [pathname.stem for pathname
                                in Path(pathname).glob('*')
                                if not str(pathname).endswith('.part')]:
                    _send_status(f'{filename} exists, skipping')
                    return
            if kind == 'img':
                wget.download(url, pathname)
            elif kind == 'vid':
                get_video(url, filename, pathname)
            _send_status(f'{filename} downloaded')
            break
        except (requests.HTTPError, urllib.error.HTTPError):
            _send_status(
                f'Error occured while downdloading, retry {tries}: {url}',
                'warns')
            if tries > 10:
                _send_status(f'Download of {url} failed', 'errors')
                break
        except Exception as e:
            _send_status(f'{url}: {e}', 'errors')
            break


def prepare_to_download(archive_path: str, save_path: str,
                        exclude: list = None):
    is_dir = Path(archive_path).is_dir()
    effective_path = Path(archive_path) if is_dir else Path(save_path)
    defaults = {
         'imgs_path': effective_path / 'photos/photo-albums',
         'vids_path': effective_path / 'video/video-albums'
         }
    if not is_dir:
        with ZipFile(archive_path, mode='r') as zf:
            zf.extractall(save_path)
    if exclude is None:
        t = Tasks(**defaults)
    else:
        t = Tasks(**{k: v for k, v in defaults.items() if k not in exclude})
    return t


def download_all(archive_path: str, save_path: str, exclude: list = None):
    _reset_all_status()
    _send_status(f'Reading and extracting {archive_path}...')
    t = prepare_to_download(archive_path, save_path, exclude)
    STATUS['folders_count'] = t.count()
    if t.imgs_path:
        _send_status(f'Downloading images {t.imgs_path}...')
        download_items(t.imgs_path, save_path, kind='img')
        STATUS['folder_num'] += 1
    if t.vids_path:
        _send_status(f'Downloading videos {t.vids_path}...')
        download_items(t.vids_path, save_path, kind='vid')
        STATUS['folder_num'] += 1


