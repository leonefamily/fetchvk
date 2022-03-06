# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 21:06:52 2022

@author: DGrishchuk
"""

from setuptools import setup


with open('requirements.txt') as f:
    reqs = f.read().strip().split('\n')

setup(
    name='fetchvk',
    version='0.2.0',
    description='Download items from VK servers',
    author='Dmitrii Grishchuk',
    author_email='leonefamily@seznam.cz',
    install_requires=reqs
)
