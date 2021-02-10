import textwrap
from abc import ABC, abstractmethod
from functools import partial
from typing import Iterable, Union

from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element

from ._algae import enclosedby, findargs, noneoremptystr, setupargs

__all__ = [
    "InvokeOption",
    "JavaScriptExecutor",
    "JavaScriptObject"
]

class InvalidJavaScriptAttribute(Exception):
    pass

class JacketException(Exception):
    pass

class JavaScriptExecutor(ABC):
    """Abstract class for objects that execute javascript."""
    
    @abstractmethod
    def execute_script(self, script: str, *args):
        """Executes javascript

        Parameters:

        script
            The JavaScript to execute
        args
            Any applicable args to the `script`
        """
        pass


JSExecType = Union[JavaScriptExecutor, Driver]


class InvokeOption:
    cacheattr = "cacheattr"
    cacheattrs = "cacheattrs"
    cachefuncs = "cachefuncs"
    cacheprops = "cacheprops"
    iffunc = "iffunc"
    ifprop = "ifprop"
    overwrite = "overwrite"
    strobj = "strobj"
    
    @staticmethod
    def all():
        for opt in InvokeOption.__dict__:
            if not (opt.startswith("__") or callable(getattr(InvokeOption, opt))):
                yield opt
    
    @staticmethod
    def defaultglobal():
        return {
            InvokeOption.cacheattrs: False,
            InvokeOption.cachefuncs: True,
            InvokeOption.cacheprops: True,
            InvokeOption.overwrite : True
        }
    
    @staticmethod
    def defaultlocal():
        return {
            InvokeOption.cacheattr: False,
            InvokeOption.iffunc   : True,
            InvokeOption.ifprop   : True,
            InvokeOption.overwrite: True
        }
    
    @staticmethod
    def globalcacheall(overwrite: bool = True):
        return {
            InvokeOption.cacheattrs: True,
            InvokeOption.cachefuncs: True,
            InvokeOption.cacheprops: True,
            InvokeOption.overwrite : bool(overwrite)
        }
    
    @staticmethod
    def globalcachefuncs(overwrite: bool = True):
        return {
            InvokeOption.cacheattrs: True,
            InvokeOption.cachefuncs: True,
            InvokeOption.cacheprops: False,
            InvokeOption.overwrite : bool(overwrite)
        }
    
    @staticmethod
    def globalcacheprops(overwrite: bool = True):
        return {
            InvokeOption.cacheattrs: True,
            InvokeOption.cachefuncs: False,
            InvokeOption.cacheprops: True,
            InvokeOption.overwrite : bool(overwrite)
        }

    @staticmethod
    def globalsonly():
        return [
            InvokeOption.cacheattrs,
            InvokeOption.cachefuncs,
            InvokeOption.cacheprops,
            InvokeOption.overwrite,
        ]
    
    @staticmethod
    def initonly():
        return [
            InvokeOption.cacheattrs,
            InvokeOption.cachefuncs,
            InvokeOption.cacheprops,
            InvokeOption.overwrite,
            InvokeOption.strobj
        ]
    
    @staticmethod
    def localcacheall(overwrite: bool = True):
        return {
            InvokeOption.cacheattr: True,
            InvokeOption.iffunc   : True,
            InvokeOption.ifprop   : True,
            InvokeOption.overwrite: bool(overwrite)
        }
    
    @staticmethod
    def localcachefuncs(overwrite: bool = True):
        return {
            InvokeOption.cacheattr: True,
            InvokeOption.iffunc   : True,
            InvokeOption.ifprop   : False,
            InvokeOption.overwrite: bool(overwrite)
        }
    
    @staticmethod
    def localcacheprops(overwrite: bool = True):
        return {
            InvokeOption.cacheattr: True,
            InvokeOption.iffunc   : False,
            InvokeOption.ifprop   : True,
            InvokeOption.overwrite: bool(overwrite)
        }
    
    @staticmethod
    def localsonly():
        return [
            InvokeOption.cacheattr,
            InvokeOption.iffunc,
            InvokeOption.ifprop,
            InvokeOption.overwrite
        ]


class JavaScriptObject:
    """A wrapper for a JavaScript object
    
    
        The object is wrapped in one of three ways:
        
            * `obj is not str`
            
                * Passed as argument to `JavaScriptExecutor`
            
            * `obj is str`
            
                Determined by `strobj` keyword
                
                * `strobj = True`, passed as argument
                * `strobj = False`, used as name of argument
                
        The object optionally supports a global caching scheme
        through optional keywords passed into the constructor
        
            * `cacheattrs`
            
                * Enables caching
                
            * `cacheprops`
            
                * Cache properties
                
            * `cachefuncs`
            
                * Cache functions
                
            * `overwrite`
            
                * Whether to overwrite attribute if previously
                        cached
                    
        When caching is enabled, `jsobject[attr]` returns the
        cached function of the attribute if it exists,
        if it does not exist, the attribute must
        be explicitly invoked via `jsobj.invoke`.
        
        
        Note, even if caching is disabled locally, invoke
        accepts analagous keywords for caching
        attributes individually.
            
            * `cacheattr`
            * `ifprop`
            * `iffunc`
            * `overwrite`
            
    """
    
    def __init__(self, obj, jsexec: JSExecType, *execargs, **invopts: bool):
        """Wraps the object and sets up global caching options
        
        Parameters:
            obj: The object to be wrapped
            
            jsexec: The `JavaScriptExecutor` to run scripts
            
            execargs: Arguments required by the object
                if it is a string with placeholder arguments
                
            invopts: Global invoke options:
                {`cacheattrs`, `cachefuncs`, `cacheprops`, `overwrite`, `strobj`}
        """
        
        self._obj = obj
        self._jsexec = jsexec
        self._execargs = execargs
        self._attrs = {}
        
        self._invopts = {
            InvokeOption.cacheattrs: invopts.get(InvokeOption.cacheattrs, False),
            InvokeOption.cacheprops: invopts.get(InvokeOption.cacheprops, True),
            InvokeOption.cachefuncs: invopts.get(InvokeOption.cachefuncs, True),
            InvokeOption.overwrite : invopts.get(InvokeOption.overwrite, True),
            InvokeOption.strobj    : invopts.get(InvokeOption.strobj, False),
        }
        
        for key, value in self._invopts.items():
            setattr(self, key, value)
        
        if isinstance(obj, str):
            if obj.isidentifier():
                if not self.strobj:
                    if obj := noneoremptystr(obj):
                        self._obj = obj
                    else:
                        self._obj = None
            else:
                if enclosedby(obj, '"') or enclosedby(obj, "'"):
                    self._obj = obj[1:-1]
                    
                self.strobj = True
    
    def __contains__(self, attr):
        return noneoremptystr(attr) in self._attrs
    
    def __getattr__(self, name):
        if name in self._attrs:
            return self._attrs[name]
        elif not name.isidentifier() or (name.startswith("__") and name.endswith("__")):
            raise InvalidJavaScriptAttribute(f"{name} must be invoked via `invoke` or ['{name}'].")
        
        return self.invoke(name)
    
    def __getitem__(self, name: str, *execargs):
        name = noneoremptystr(name)
        
        if name in self._attrs:
            return self._attrs[name]
        else:
            return self.invoke(name, *execargs)
    
    def __iter__(self):
        for prop in self.properties():
            yield prop
    
    def __repr__(self):
        return f"""{JavaScriptObject.__name__}<{self.definition_root}>"""
    
    @classmethod
    def new(cls,
            obj: str,
            name: str,
            jsexec: JSExecType,
            *ctorargs,
            **invopts: bool):
        """Creates a new JavaScript object and stores it in the global space of the executor
        
        Parameters:
            obj: The name of the JavaScript object
            
            name: The name of the variable to store the object
            
            jsexec: The `JavaScriptExecutor` to run scripts
            
            ctorargs: Arguments to be given to the constructor of the object
            
            invopts: Global invoke options:
                {`cacheattrs`, `cachefuncs`, `cacheprops`, `overwrite`}
        """
        if not ((name := noneoremptystr(name)) and name.isidentifier()):
            raise InvalidJavaScriptAttribute(f"Invalid identifier {name}.")
        elif not ((obj := noneoremptystr(obj)) and obj.isidentifier()):
            raise InvalidJavaScriptAttribute(f"Invalid object {obj}.")
        
        args = setupargs(lambda i: i, 0, len(ctorargs)) if ctorargs else ()
        
        if args:
            jsexec.execute_script(f"""{name} = new {obj}({",".join(args)})""", *ctorargs)
        else:
            jsexec.execute_script(f"""{name} = new {obj}()""")
        
        return cls(name, jsexec, **{**invopts, InvokeOption.strobj: False})
    
    @property
    def definition_root(self):
        """The way in which the object is passed to scripts"""
        if self._obj is None:
            return None
        elif isinstance(self._obj, str):
            if not self.__getattribute__(InvokeOption.strobj):
                return self._obj
            else:
                return "arguments[0]"
        else:
            return "arguments[0]"
    
    @property
    def javascript_executor(self):
        """The executor for the object"""
        return self._jsexec
    
    @property
    def object(self):
        """The wrapped object"""
        return self._obj
    
    def allattributes(self, *execargs):
        """All functions and properties of the object and its prototype(s)
        
        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = textwrap.dedent(f"""
        (() => {{
            let props = new Set();
            let current = {jsdef};
            
            do {{
                Object.getOwnPropertyNames(current).map(p => props.add(p));
            }} while ((current = Object.getPrototypeOf(current)));
            
            return [...props.keys()]
        }})();
        """).strip("\n")
        
        return self._exec(stmt, passobj, *execargs)
    
    def allfunctions(self, *execargs):
        """All functions of the object and its prototype(s)

        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = textwrap.dedent(f"""
        (() => {{
            let props = new Set();
            let current = {jsdef};

            do {{
                Object.getOwnPropertyNames(current).map(p => props.add(p));
            }} while ((current = Object.getPrototypeOf(current)));

            return [...props.keys()].filter(p => typeof({jsdef}[p]) === "function");
        }})();
        """).strip("\n")
        
        return self._exec(stmt, passobj, *execargs)
    
    def allproperties(self, *execargs):
        """All properties of the object and its prototype(s)

        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = textwrap.dedent(f"""
        (() => {{
            let props = new Set();
            let current = {jsdef};

            do {{
                Object.getOwnPropertyNames(current).map(p => props.add(p));
            }} while ((current = Object.getPrototypeOf(current)));

            return [...props.keys()].filter(p => typeof({jsdef}[p]) !== "function");
        }})();
        """).strip("\n")
        
        return self._exec(stmt, passobj, *execargs)
    
    def attributes(self, *execargs):
        """All functions and properties of the object

        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = f"""Object.getOwnPropertyNames({jsdef})"""
        
        return self._exec(stmt, passobj, *execargs)
    
    def clearcache(self):
        """Clears the attribute cache"""
        self._attrs.clear()
    
    def functions(self, *execargs):
        """All functions of the object

        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = f"""Object.getOwnPropertyNames({jsdef}).filter(p => typeof({jsdef}[p]) ===
        "function")"""
        
        return self._exec(stmt, passobj, *execargs)
    
    def properties(self, *execargs):
        """All properties of the object

        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
        """
        jsdef, passobj = self._define()
        stmt = f"""Object.getOwnPropertyNames({jsdef}).filter(p => typeof({jsdef})[p] !==
        "function")"""
        
        return self._exec(stmt, passobj, *execargs)
    
    def invoke(self,
               name: str = None,
               *execargs,
               attrargs: tuple = None,
               **invopts: bool):
        """Retrieves the value of the JavaScript attribute

        Parameters:
            name: Name of the JavaScript attribute
            
            attrargs: Supplied to the `name` if it represents a function

            execargs: Any extra arguments necessary to the executor

            invopts: Invocation options: {`cacheattr`, `iffunc`, `ifprop`, `overwrite`}

        Returns:
            A `Callable` if `name` is a function, unless `attr_args` is not
                `None`, then the result of calling the function with those arguments
                is returned. Otherwise, the value of the JavaScript object property.


        Raises:
            InvalidJavaScriptAttribute: `attrargs` is not `None` and `name` does
                not represent a function
        """
        prop = None
        
        if f := self.wrapfunction(name, *execargs):
            if attrargs is None:
                res = f
            elif isinstance(attrargs, tuple):
                res = f(*attrargs)
            else:
                res = f(attrargs)
        elif attrargs is not None:
            raise InvalidJavaScriptAttribute(f"No function named `{name}`.")
        elif prop := self.wrapproperty(name, *execargs, as_function=True):
            res = prop()
        else:
            return None
        
        if self._getopt(InvokeOption.cacheattr, InvokeOption.cacheattrs, **invopts):
            attr = None
            
            if f and self._getopt(InvokeOption.iffunc, InvokeOption.cachefuncs, **invopts):
                attr = f
            elif self._getopt(InvokeOption.ifprop, InvokeOption.cacheprops, **invopts):
                attr = prop
            
            overwrite = self._getopt(InvokeOption.overwrite, InvokeOption.overwrite, **invopts)
            
            if attr and name not in self._attrs or overwrite:
                self._attrs[name] = attr
        
        return res
    
    def populate(self, *execargs, **invopts: bool):
        """Populates a dictionary with the attributes of the object
        
        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
            
            invopts: Invocation options: {`iffunc`, `ifprop`}
        """
        iffunc = invopts.get(InvokeOption.iffunc, True)
        ifprop = invopts.get(InvokeOption.ifprop, True)
        
        if iffunc:
            attrs = self.attributes(*execargs) if ifprop else self.functions(*execargs)
        elif ifprop:
            attrs = self.properties(*execargs)
        else:
            attrs = self.attributes(*execargs)
        
        invopts = {
            InvokeOption.cacheattr: True,
            InvokeOption.iffunc   : iffunc,
            InvokeOption.ifprop   : ifprop,
            InvokeOption.overwrite: True
        }
        
        return {attr: self.invoke(attr, *execargs, **invopts) for attr in attrs}
    
    def populateall(self, *execargs, **invopts: bool):
        """Populates a dictionary with the attributes of the object and its prototype(s)
        
        Parameters:
            execargs: Any extra arguments required by the `JavaScriptExecutor`
            
            invopts: Invocation options: {`iffunc`, `ifprop`}
        """
        iffunc = invopts.get(InvokeOption.iffunc, True)
        ifprop = invopts.get(InvokeOption.ifprop, True)
        
        if iffunc:
            attrs = self.allattributes(*execargs) if ifprop else self.allfunctions(*execargs)
        elif ifprop:
            attrs = self.allproperties(*execargs)
        else:
            attrs = self.allattributes(*execargs)
        
        invopts = {
            InvokeOption.cacheattr: True,
            InvokeOption.ifprop   : iffunc,
            InvokeOption.iffunc   : ifprop,
            InvokeOption.overwrite: True
        }
        
        return {attr: self.invoke(attr, *execargs, **invopts) for attr in attrs}
    
    def tryinvoke(self,
                  name: str,
                  attrargs: tuple = None,
                  *execargs,
                  **invopts: bool):
        """Retrieves the value of the JavaScript attribute

        Parameters:
            name: Name of the JavaScript attribute

            attrargs: Supplied to the `name` if it represents a function

            execargs: Any extra arguments necessary to the executor

            invopts: Invocation options: {`cacheattr`, `iffunc`, `ifprop`, `overwrite`}

        Returns:
            A `Callable` if `name` is a function, unless `attr_args` is not
                `None`, then the result of calling the function with those arguments
                is returned. Otherwise, the value of the JavaScript object property
                or `None`
        """
        try:
            return self.invoke(name, *execargs, attrargs=attrargs, **invopts)
        except InvalidJavaScriptAttribute:
            pass
    
    def wrap(self, *execargs, **invopts: bool):
        """Wraps all JavaScript attributes of the object

        Parameters:
            execargs: Any arguments required by the `JavaScriptExecutor`

        Returns:
            A `callable` representation of the JavaScript function
            
        invopts: Invocation options: {`iffunc`, `ifprop`}

        Raises:
            InvalidJavaScriptAttribute: If this is a '*global*' object
            (`self.name` is `None`) and `name` is empty, `None` or whitespace
        """
        iffunc = invopts.get(InvokeOption.iffunc, True)
        ifprop = invopts.get(InvokeOption.ifprop, True)
        
        funcs, props = self.functions(*execargs), self.properties(*execargs)
        
        wfuncs = {f: self.wrapfunction(f, *execargs) for f in funcs} if iffunc else {}
        wprops = {p: self.wrapproperty(p, *execargs) for p in props} if ifprop else {}
        
        return {**wprops, **wfuncs}
    
    def wrapall(self, *execargs, **invopts: bool):
        """Wraps all JavaScript attributes of the object and its prototype(s)

        Parameters:
            execargs: Any arguments required by the `JavaScriptExecutor`

        Returns:
            A `callable` representation of the JavaScript function

        invopts: Invocation options: {`iffunc`, `ifprop`}

        Raises:
            InvalidJavaScriptAttribute: If this is a '*global*' object
            (`self.name` is `None`) and `name` is empty, `None` or whitespace
        """
        iffunc = invopts.get(InvokeOption.iffunc, True)
        ifprop = invopts.get(InvokeOption.ifprop, True)
        
        funcs, props = self.allfunctions(*execargs), self.allproperties(*execargs)
        
        wfuncs = {f: self.wrapfunction(f, *execargs) for f in funcs} if iffunc else {}
        wprops = {p: self.wrapproperty(p, *execargs) for p in props} if ifprop else {}
        
        return {**wprops, **wfuncs}
    
    def wrapfunction(self,
                     name: str,
                     *execargs,
                     argnames: Union[str, Iterable[str]] = None):
        """Wraps a JavaScript function with a Python function

        Parameters:
            name: Name of the JavaScript function
            
            execargs: Any arguments required by the `JavaScriptExecutor`

            argnames: A list of names for some or all of the arguments
                        of the produced function

        Returns:
            A `callable` representation of the JavaScript function

        Raises:
            InvalidJavaScriptAttribute: If this is a '*global*' object
            (`self.name` is `None`) and `name` is empty, `None` or whitespace
        """
        
        jsdef, passobj = self._define(name)
        stmt = f"""typeof({jsdef})"""
        res_type = self._exec(stmt, passobj, *execargs)
        
        if res_type == "function":
            arity = self._exec(f"""{jsdef}.length""", passobj, *execargs)
            
            if arity == 0:
                script = f"""return {jsdef}()"""
                if passobj:
                    return lambda: self._jsexec.execute_script(
                        script,
                        self._obj,
                        *self._execargs,
                        *execargs)
                else:
                    return lambda: self._jsexec.execute_script(script, *self._execargs, *execargs)
            else:
                if argnames:
                    if isinstance(argnames, str):
                        if argname := noneoremptystr(argnames):
                            names = [argname]
                        else:
                            names = []
                    else:
                        names = list(argnames)
                    
                    if len(names) >= arity:
                        names = names[:arity]
                    else:
                        n = len(names)
                        names += [f"arg{i + n}" for i in range(arity - n)]
                else:
                    names = [f"arg{i}" for i in range(arity)]
                
                argind = len(findargs(jsdef))
                arguments = [f"arguments[{i + argind}]" for i in range(arity)]
                argsstr = ", ".join(arguments)
                namesstr = ", ".join(names)
                
                if passobj:
                    lamb = f"""lambda jsexec, obj, execargs, {namesstr}: jsexec.execute_script(
                    \"\"\"return {jsdef}({argsstr})\"\"\", obj, *execargs, {namesstr}) """
                    
                    return partial(
                        eval(lamb),
                        self._jsexec,
                        self._obj,
                        self._execargs + execargs)
                else:
                    lamb = f"""lambda jsexec, execargs, {namesstr}: jsexec.execute_script(
                    \"\"\"return {jsdef}({argsstr})\"\"\", *execargs, {namesstr})"""
                    
                    return partial(eval(lamb), self._jsexec, self._execargs + execargs)
    
    def wrapproperty(self,
                     name: str,
                     *execargs, as_function: bool = False):
        """Wraps a JavaScript property

        Parameters:
            name: Name of the JavaScript function

            execargs: Any arguments required by the `JavaScriptExecutor`
            
            as_function: Whether to wrap the property as a nullary function
                            or Python `property`

        Returns:
            A `Callable` representation of the JavaScript property

        Raises:
            InvalidJavaScriptAttribute: If this is a '*global*' object
            (`self.name` is `None`) and `name` is empty, `None` or whitespace
        """
        
        jsdef, passobj = self._define(name)
        stmt = f"""typeof({jsdef})"""
        res_type = self._exec(stmt, passobj, *execargs)
        
        if res_type not in ("function", "undefined"):
            stmt = f"""return {jsdef}"""
            if passobj:
                lamb = lambda jsexec, obj, *args: jsexec.execute_script(f"{stmt}", obj, *args)
                f = partial(lamb, self._jsexec, self._obj, *self._execargs, *execargs)
                return f if as_function else property(fget=f)
            else:
                lamb = lambda jsexec, *args: jsexec.execute_script(f"""{stmt}""", *args)
                f = partial(lamb, self._jsexec, *self._execargs, *execargs)
                return f if as_function else property(fget=f)
    
    def _define(self, name=None):
        def stringify(oname, pobj):
            if not name:
                obj_ = oname, pobj
            elif name.isdecimal() or not name.isidentifier():
                obj_ = f"""{oname}["{name}"]""", pobj
            elif name.startswith("["):
                obj_ = f"""{oname}{name}""", pobj
            else:
                obj_ = f"""{oname}.{name}""", pobj
            
            return obj_
        
        name = noneoremptystr(name)
        
        if not isinstance(self._obj, str) or self.__getattribute__("strobj"):
            if self._obj is None:
                if not name:
                    raise InvalidJavaScriptAttribute("Expected attribute name.")
                elif name.isdecimal():
                    raise InvalidJavaScriptAttribute("Unexpected number.")
                
                obj = name, False
            else:
                if self._obj is None:
                    if not name:
                        raise InvalidJavaScriptAttribute("Expected attribute name.")
                obj = stringify("arguments[0]", True)
        else:
            obj = stringify(self._obj, False)
        
        return obj
    
    def _exec(self, stmt, passobj, *args):
        if passobj:
            return self._jsexec.execute_script(
                f"""return {stmt}""",
                self._obj,
                *self._execargs,
                *args)
        else:
            return self._jsexec.execute_script(
                f"""return {stmt}""",
                *self._execargs,
                *args)
    
    def _getopt(self, lcl, glbl, **opts):
        gopt = getattr(self, glbl)
        lopt = opts.get(lcl)
        
        return gopt if lopt is None else lopt

    def _globalinvopts(self):
        return {glbl: getattr(self, glbl) for glbl in InvokeOption.globalsonly()}
