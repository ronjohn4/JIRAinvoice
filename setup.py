from setuptools import setup

setup(
   name='JIRAProjectInvoice',
   version='1.0',
   description='A useful module',
   author='MRon Johnson',
   author_email='ronjohn4@gmail.com',
   packages=['JIRAProjectInvoice'],  #same as name
   install_requires=[
        'certifi>=2017.7.27.1',
        'chardet>=3.0.4',
        'click>=6.7',
        'Flask>=0.12.2',
        'idna>=2.5',
        'itsdangerous>=0.24',
        'Jinja2>=2.9.6',
        'MarkupSafe>=1.0',
        'requests>=2.18.3',
        'urllib3>=1.22',
        'Werkzeug>=0.12.2'
    ], #external packages as dependencies
)