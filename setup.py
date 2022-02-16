from setuptools import setup

setup(
    name='spacecapsule',
    version='0.1.0',
    packages=['spacecapsule', 'resources'],
    install_requires=[
        'click', 'jinja2', 'kubernetes'
    ],
    entry_point={
        'console_scripts': [
            'spacecapsule = spacecapsule.__main__:main'
        ]
    })
