from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name="selenium_js2py",
    version="0.3.3",
    packages=find_packages(),
    url="https://github.com/junk-io/selenium-js2py",
    author="junki",
    description="A Selenium-based tool for wrapping and interacting with JavaScript objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    data_files=[("", ["LICENSE", "README.md"])],
    install_requires=[
        "selenium"
    ]
)
