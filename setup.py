from setuptools import setup, find_packages

setup(
    name='paybrobot',
    version='0.1',
    packages=find_packages(),
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'paybrobot = my_chatbot.main:main'
        ]
    }
)