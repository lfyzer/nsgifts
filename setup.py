from setuptools import setup, find_packages

setup(
    name='nsgifts-api',
    version='0.1.0',
    author='lfyzer',
    description='A Python wrapper for the NS.Gifts API.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lfyzer/nsgifts',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pydantic',
        "aiohttp",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
