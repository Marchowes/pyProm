from distutils.core import setup
from pyprom import __version__, __doc__

with open('requirements.txt') as f:
    requires = [line.strip() for line in f if line.strip()]
with open('test-requirements.txt') as f:
    tests_requires = [line.strip() for line in f if line.strip()]

setup(
    name='pyProm',
    version=__version__,
    keywords=['pyProm'],
    long_description=__doc__,
    description='Surface Network analysis.',
    author='Marc Howes',
    author_email='marc.h.howes@gmail.com',
    url='https://github.com/marchowes/pyProm',
    packages=['pyprom', 'pyprom/util'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    install_requires=requires,
    tests_require=tests_requires,
)