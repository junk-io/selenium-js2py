from functools import singledispatchmethod as overloaded
from time import sleep
from typing import Iterable, Union

from selenium.webdriver.remote.webelement import WebElement as Element

from . import DOMElement, InvokeOption
from . import JavaScriptExecutor, JavaScriptObject
from ._algae import noneoremptystr
from .javascript import JacketException

__all__ = [
    "JQueryElement",
    "JQueryResponse",
    "Q"
]


class JQueryElement(JavaScriptObject):
    
    def __init__(self, element: Element, jsexec: JavaScriptExecutor = None, **invopts):
        self._element = element
        jsexec = jsexec or element._parent
        super().__init__(
            "$(arguments[0])",
            jsexec,
            element,
            **{**invopts, InvokeOption.strobj: False})
    
    @property
    def element(self):
        return self._element
    
    def asdomelement(self):
        return DOMElement(self._obj, self._jsexec, **self._globalinvopts())
    
    def attr(self, name: str, value=None):
        args0, args1 = "arguments[0]", "arguments[1]"
        if value is None:
            return self._exec(f"""$({args0}).attr("{name}")""", False)
        else:
            self._exec(f"""$({args0}).attr("{name}", {args1})""", False, value)
    
    def click(self, wait: float = 0.0):
        self._exec("arguments[0].scrollIntoView(); arguments[0].click();", False)
        
        if wait > 0.0:
            sleep(wait)
    
    def screenshot(self, asbase64: bool = False):
        return self._obj.screenshot_as_base64 if asbase64 else self._obj.screenshot_as_png
    
    def screenshot_and_save(self, fp: str):
        return self._obj.screenshot(fp)


class JQueryResponse(JavaScriptObject):
    
    def __init__(self,
                 response: Union[Element, Iterable[Element]],
                 jsexec: JavaScriptExecutor = None,
                 exception=None, **invopts):
        
        if exception:
            _jsexec, _res = jsexec, []
            _exc = JacketException(exception) if isinstance(exception,
                                                            str) else exception
        else:
            if isinstance(response, Element):
                _jsexec = jsexec or response.parent
                _res = JQueryElement(response, jsexec, **invopts)
                _exc = None
            else:
                try:
                    elmts = iter(response)
                except Exception as exc:
                    _jsexec, _res, _exc = jsexec, [], exc
                else:
                    _res = []
                    
                    for elmt in elmts:
                        if not isinstance(elmt, Element):
                            _jsexec, _res = jsexec, []
                            _exc = TypeError("Expected `Element` or `Iterable[Element]` as a "
                                             "response.")
                            break
                        else:
                            _res.append(elmt)
                    else:
                        _jsexec = jsexec or _res[0].parent if _res else jsexec
                        _exc = None
                        
                        if len(_res) == 1:
                            _res = JQueryElement(_res[0], _jsexec, **invopts)
                        else:
                            _res = [JQueryElement(elmt, _jsexec, **invopts) for elmt in _res]
        
        self._raw = response
        self._exc = _exc
        
        super().__init__(
            "$(arguments[0])",
            _jsexec,
            response,
            **{**invopts, InvokeOption.strobj: False})
    
    def __bool__(self):
        return self._exc is None
    
    def __getattribute__(self, item):
        if ((exc := object.__getattribute__(self, "_exc")) and
                item != "__bool__"):
            
            raise exc
        
        return object.__getattribute__(self, item)
    
    def __repr__(self):
        return f"""{JQueryResponse.__name__}<{self.definition_root}>"""
    
    @property
    def exception(self):
        return self._exc
    
    @property
    def raw_response(self):
        return self._raw
    
    @property
    def response(self):
        return self._r
    
    @property
    def success(self):
        return self._exc is None
    
    def attr(self, name: str, value=None):
        args0, args1 = "arguments[0]", "arguments[1]"
        if value is None:
            return self._exec(f"""$({args0}).attr("{name}")""", False)
        else:
            self._exec(f"""$({args0}).attr("{name}", {args1})""", False, value)


class Q(JavaScriptObject, JavaScriptExecutor):
    
    def __init__(self, jsexec: JavaScriptExecutor, **invopts):
        super().__init__("$", jsexec, **{**invopts, InvokeOption.strobj: False})
    
    def __call__(self, jquery: str):
        return self.query(jquery)
    
    def __repr__(self):
        return f"""jquery function [{Q.__name__}]<$>"""
    
    def execute_script(self, script, *args):
        try:
            res = self._jsexec.execute_script(script, *args)
        except Exception as exc:
            return JQueryResponse([], self, exc)
        else:
            if isinstance(res, Element):
                return JQueryResponse(res, self)
            elif isinstance(res, list) and len(res) > 0:
                if isinstance(res[0], Element):
                    return JQueryResponse(res, self)
                else:
                    return res
            else:
                return res
    
    @overloaded
    def query(self, jquery: Union[str, Element, Iterable[Element]]):
        return JQueryResponse(jquery)
    
    @query.register
    def _(self, jquery: str):
        if jquery := noneoremptystr(jquery):
            return self.execute_script(f"""return $(arguments[0])""", jquery)
    
    @query.register
    def _(self, jquery: Element):
        return JQueryElement(jquery)
