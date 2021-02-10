from setuptools import find_packages, setup

setup(
    name='selenium_js2py',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/junk-io/selenium-js2py',
    author='junki',
    description='A Selenium-based tool for wrapping and interacting with JavaScript objects',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    data_files=[('', ['LICENSE'])],
    install_requires=[
        'selenium'
    ]
)
