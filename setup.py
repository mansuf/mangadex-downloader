import pathlib
from setuptools import setup
import sys

__VERSION__ = 'v0.0.3'

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name = 'mangadex-downloader',         
  packages = ['mangadex_downloader'],   
  version = __VERSION__,
  license='The Unlicense',     
  description = 'Download manga from Mangadex through Python',
  long_description= README,
  long_description_content_type= 'text/markdown',
  author = 'Rahman Yusuf',              
  author_email = 'danipart4@gmail.com',
  url = 'https://github.com/trollfist20/mangadex-downloader',  
  download_url = 'https://github.com/trollfist20/mangadex-downloader/archive/%s.tar.gz' % (__VERSION__),
  keywords = ['mangadex', 'mangadex download'], 
  install_requires=[           
          'bs4',
          'download'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',  
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: The Unlicense (Unlicense)',  
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ],
)
