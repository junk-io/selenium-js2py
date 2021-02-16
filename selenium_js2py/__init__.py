import textwrap

from .javascript import *
from .jquery import *

__version__ = "0.3.3"


def track():
    return textwrap.dedent("""
    ## 0.1.0
    ---
    
    * Initial Release
    * `JavaScriptObject`
    * `JQueryElement`
    * `JQueryResponse`
    * `S` (The `jquery` (`$`) function wrapper)
    
    ## 0.1.1
    ---
    * Removed string normalization before invoke in `JavaScriptObject.__getitem__`
    * Strings with dot-expressions (e.g., "name.attribute") were being wrapped
        as strings and not what the attribute represents
    
    ## 0.2.0
    ---
    
    * `_configureglobalopts`
    * `_resolveargnames`
    * `_resolveargs`
    * `_resolveexecargs`
    * `JavaScriptObject.get`
    * `JavaScriptObject.set`
    * `JavaScriptObject.run`
    * `JavaScriptObjectFactory`
    * Lazy executor arguments
    
    ## 0.3.0
    ---
    
    * `JavaScriptResponse`
    
    ## 0.3.1
    ---
    
    * Removed definition of `attr` from `JavaScriptResponse`
    
    ## 0.3.2
    ---
    
    * `JavaScriptResponse.__getattribute__` causing `RecursionError` in `JavaScriptResponse.__repr__`
    
    ## 0.3.3
    * Simplified and stabilized attribute access across all classes
    * `__repr__`s follow standard format
    
    
    """).strip("\n")
