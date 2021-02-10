import setuptools

setuptools.setup(
    name='jacket',
    version='0.1.0',
    packages=setuptools.find_packages(),
    url='https://github.com/CMU-CREATE-Lab/unearthtime',
    author='junki',
    description='A Selenium-based tool for wrapping and interacting with JavaScript objects',
    data_files=[('', ['LICENSE'])],
    install_requires=[
        'selenium'
    ]
)