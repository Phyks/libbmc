#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print('[libbmc] setuptools not found.')
    raise

with open('libbmc/__init__.py') as fh:
    for line in fh:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

try:
    from pip.req import parse_requirements
    from pip.download import PipSession
except ImportError:
    print('[libbmc] pip not found.')
    raise

# parse_requirements() returns generator of pip.req.InstallRequirement objects
parsed_requirements = parse_requirements("requirements.txt",
                                         session=PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
install_requires = [str(ir.req) for ir in parsed_requirements]

setup(
    name='libbmc',
    version=version,
    url='https://github.com/Phyks/libbmc/',
    author='Phyks (Lucas Verney)',
    author_email='phyks@phyks.me',
    license='MIT License',
    description='A python library to deal with scientific papers.',
    packages=['libbmc',
              'libbmc.citations', 'libbmc.papers', 'libbmc.repositories'],
    install_requires=install_requires
)
