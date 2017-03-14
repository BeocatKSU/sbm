from setuptools import setup

setup(
    name='sbm',
    packages=['sbm'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy'
    ],
)
