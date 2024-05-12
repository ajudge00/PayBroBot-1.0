from setuptools import setup, find_packages

setup(
    name='paybrobot',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'setuptools~=65.5.0',
        'bcrypt~=4.1.3',
        'pip~=23.3.1',
        'mock~=5.1.0',
        'pillow~=10.3.0',
        'certifi~=2024.2.2',
        'telebot~=0.0.5',
        'requests~=2.31.0',
        'urllib3~=2.2.1',
        'idna~=3.7',
    ],
    entry_points={
        'console_scripts': [
            'paybrobot = paybrobot.app:main'
        ]
    }
)
