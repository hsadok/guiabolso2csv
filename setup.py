# coding=utf-8
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='guiabolso2csv',
    version='0.2',
    description="GuiaBolso2csv is a simple Python program that can be used to"
                "download GuiaBolso transactions in a csv format.",
    long_description=readme,
    packages=find_packages(),
    url='https://github.com/hugombarreto/guiabolso2csv',
    download_url='https://github.com/hugombarreto/guiabolso2csv/archive/0.2.tar.gz',
    license='GPLv3',
    author='Hugo Sadok',
    author_email='hugo@sadok.com.br',
    keywords=['finance', 'guiabolso', 'excel', 'csv', 'xlsx'],
    entry_points={
        'console_scripts': [
            'guiabolso2csv=guiabolso2csv.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        'requests',
        'click',
        'unicodecsv',
        'openpyxl'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
)
