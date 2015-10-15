from setuptools import setup

setup(
    name='flowdock',
    version='0.1',
    py_modules=['main', 'flowdock'],
    install_requires=[
        'click~=5.1',
        'requests~=2.8.1'
    ],
    entry_points='''
        [console_scripts]
        flowdock=main:main
    ''',
)
