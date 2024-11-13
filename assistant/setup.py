from setuptools import setup, find_packages

setup(
    name='assgpt',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'openai',
        'bcrypt',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'assgpt=assgpt.main:main'
        ],
    },
)

