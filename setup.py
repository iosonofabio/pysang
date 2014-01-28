import os
#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="PySang",
      version="0.3.2",
      description="Visualizer for Sanger chromatographs (ABI/AB1).",
      long_description=read("README"),
      author="Fabio Zanini",
      author_email="fabio.zanini@tuebingen.mpg.de",
      license='Public domain',
      packages=find_packages(exclude='tests'),
      package_data={'pysang': ['data/*.ab1']},
      #install_requires=['matplotlib', 'biopython'],
      entry_points = {'gui_scripts': ['pysang = pysang.gui:main']}
     )
