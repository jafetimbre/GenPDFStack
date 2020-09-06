from setuptools import setup

setup(
    name='GenPDFStack',
    version='1.0',
    py_modules=['genPDFStack'],
    install_requires=[
        'Click',
        
    ],
    entry_points='''
        [console_scripts]
        genpdfstack=genPDFStack:main
    '''
)