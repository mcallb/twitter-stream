from setuptools import find_packages
from setuptools import setup


setup(
    name='beer_alert',
    version='0.0.0',
    packages=find_packages(exclude=['tests']),
    author='Me',
    entry_points={
        'console_scripts': [
            'beer_alert = beer_alert.beer_alert:main'
        ]
    }
)