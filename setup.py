from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='photostation',
    version='0.1.4',
    description='A Python API to communicate with Photo Station running on Synology NAS.',
    long_description=long_description,
    url='https://github.com/skarppi/python-photostation',
    author='Juho Kolehmainen',
    author_email='juho.kolehmainen@iki.fi',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='synology dsm photo station web api',
    packages=['photostation'],
    install_requires=['requests>=1.2'],
)