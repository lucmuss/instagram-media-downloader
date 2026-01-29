"""
Setup-Konfiguration für Instagram Media Downloader
"""

from setuptools import setup, find_packages
from pathlib import Path

# README für long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='instagram-media-downloader',
    version='2.0.0',
    author='skymuss',
    author_email='',
    description='Professionelles CLI-Tool zum Herunterladen von Instagram-Medien (Saved, Liked, Own)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lucmuss/instagram-media-downloader',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'tqdm>=4.66.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'instagram-downloader=instagram_downloader.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
