# `selenium-js2py`

A tool for wrapping and interacting with ***JavaScript*** objects returned from a browser console. It is flexible in how these objects can be represented and intelligent enough to know how to retrieve its attributes.

## Installation

```
> pip install -U selenium-js2py
> pip install -U git+https://github.com/junk-io/selenium-js2py.git#egg=selenium-js2py
> pip install -U git+https://github.com/junk-io/selenium-js2py.git@v0.1.0#egg=selenium-js2py
```

## Quick Example

```python
>>> from selenium.webdriver import Chrome, ChromeOptions
>>> from selenium_js2py import JavaScriptObject as jsobj
>>>
>>> options = ChromeOptions()
>>> options.add_argument("--headless")
>>> chrome = Chrome("path_to_chromedriver", options=options)
>>> 
>>> strobj = jsobj('"string"', chrome)
>>>
>>> strobj.definition_root
'arguments[0]'
>>>
>>> strobj1.properties()
['0', '1', '2', '3', '4', '5', 'length']
>>>
>>> strobj1["0"]
's'
>>>
>>> strobj1.functions()
[]
>>> allfuncs = strobj1.allfunctions()
>>> len(allfuncs)
56
>>>
>>> strobj1["startsWith"]("str")
True
>>> strobj1.invoke("startsWith")("str")
True
>>> strobj1.invoke("startsWith", attrargs="str")
True
>>> strobj1.startsWith("str")
True
```
