from distutils.core import setup

setup(
    name='jsonflow',
    version='1.0',
    py_modules=['jsonflow.access', 'jsonflow.concurrent', 'jsonflow.config', 'jsonflow.core', 'jsonflow.decorators'],
    requires=['requests']
)
