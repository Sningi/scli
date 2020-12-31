from setuptools import setup

setup(
    name='scli',
    version='0.1',
    py_modules=['scli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        scli=scli:cli
    ''',
)