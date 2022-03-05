# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 21:15:00 2022

@author: DGrishchuk
"""

from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from zipfile import ZipFile
from pathlib import Path
import requests
import logging
import urllib
import wget

from settings import STATUS


def files_count(path):
    if not Path(path).is_dir():
        raise ValueError(f'{path} is not a directory')
    count = 0
    for f in Path(path).iterdir():
        if f.is_file():
            count += 1
    return count


def dirs_count(path):
    if not Path(path).is_dir():
        raise ValueError(f'{path} is not a directory')
    count = 0
    for f in Path(path).iterdir():
        if f.is_dir():
            count += 1
    return count


def download_images(source_path, save_path):
    STATUS['current_folder'] = source_path
    STATUS['folder_files_count'] = files_count(source_path)
    STATUS['file_num'] = 0
    STATUS['has_updates'] = True
    for html_p in Path(source_path).glob('*.html'):
        html_f = load_html_text(html_p)
        imgs, path = get_all_images(html_f)
        STATUS['item_num'] = 0
        STATUS['file_item_count'] = len(imgs)
        STATUS['current_file'] = html_p
        STATUS['has_updates'] = True
        spath = Path(save_path) / path
        if not spath.exists():
            spath.mkdir(parents=True, exist_ok=True)
        for img in imgs:
            download(img, str(spath))
            STATUS['item_num'] += 1
            STATUS['has_updates'] = True
        STATUS['file_num'] += 1
        STATUS['has_updates'] = True


def load_html_text(path):
    with open(path, mode='r', encoding='windows-1251') as html:
        return html.read()


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(html):
    soup = bs(html, "html.parser")
    urls = []
    alb_parts = []
    for part in soup.find_all(class_="ui_crumb"):
        alb_parts.append(f'{part.contents[0]}')
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        if is_valid(img_url):
            urls.append(img_url)
    STATUS['file_items_count'] = len(urls)
    return urls, '/'.join(alb_parts)


def download(url, pathname):
    tries = 0
    while True:
        tries += 1
        try:
            try:
                filename = url.split('/')[-1].split('?')[0]
                # logging.info(f'{Path(pathname) / filename}')
                if (Path(pathname) / filename).exists():
                    logging.info(f'{filename} exists, skipping')
                    return
                else:
                    pass
            except Exception:
                pass
            fname = wget.download(url, pathname)
            logging.info(f'{fname} downloaded')
            break
        except (requests.HTTPError, urllib.error.HTTPError):
            logging.info(
                f'Error occured while downdloading, retry {tries}: {url}')
            if tries > 10:
                logging.info(f'Download of {url} failed')
                break
        except Exception as e:
            logging.error(f'{url}: {e}, {type(e)}')
            break


def download_all(archive_path, save_path):
    logging.info(f'Reading and extracting {archive_path}...')
    if not Path(archive_path).is_dir():
        with ZipFile(archive_path, mode='r') as zf:
            zf.extractall(save_path)
        imgs_path = Path(save_path) / 'photos' / 'photo-albums'
    else:
        imgs_path = Path(archive_path) / 'photos' / 'photo-albums'
    STATUS['folders_count'] += 1  # !!! TODO dirs_count
    logging.info(f'Downloading images {imgs_path}...')
    download_images(imgs_path, save_path)
    STATUS['has_updates'] += 1
    STATUS['folder_num'] += 1
