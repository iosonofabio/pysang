# vim: fdm=indent
'''
author:     Fabio Zanini
date:       21/01/15
content:    Setup file for PySang
'''
import os
from setuptools import setup, find_packages

long_description = "Check out the README file for install instructions and more."

setup(name="PySang",
      version="0.3.7",
      description="Visualizer for Sanger chromatographs (ABI/AB1).",
      long_description=long_description,
      author="Fabio Zanini",
      author_email="fabio.zanini@tuebingen.mpg.de",
      license='Public domain',
      url='https://github.com/iosonofabio/pysang',
      packages=find_packages(exclude='tests'),
      package_data={'pysang': ['data/*.ab1']},
      entry_points = {'gui_scripts': ['pysang = pysang.gui:main']}
     )
