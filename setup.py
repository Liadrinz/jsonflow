from distutils.core import setup

setup(
    name='jsonflow',
    version='1.0',
    py_modules=['jsonflow.concurrent', 'jsonflow.config', 'jsonflow.core', 'jsonflow.util'],
    requires=['requests']
)
