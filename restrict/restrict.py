from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial, wraps
from types import MethodType
from typing import Any, Callable, List, Optional


class RestrictionError(Exception):
    pass


class OwnerError(RestrictionError):
    pass


class CaseError(RestrictionError):
    pass


class Access(Enum):
    BY_OWNER = auto()
    BY_ALL = auto()
    BY_CASE = auto()


def _case_ensurer(f, *args, **kwargs):
    if isinstance(f, MethodType):
        f.__func__.EQ_W = True
    else:
        f.EQ_W = True
        
    ccode = kwargs.pop("ccode")
    cw = f(*args, **kwargs)
    return cw(ccode)


@contextmanager
def case(ccode):
    try:
        yield partial(_case_ensurer, ccode=ccode)
    finally:
        pass


class CaseWrapper:
    def __init__(self, f, args, kwargs, ccode):
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.ccode = ccode

    def __call__(self, ccode):
        if ccode == self.ccode:
            return self.f(*self.args, **self.kwargs)
        else:
            raise CaseError(
                f"Object requires {self.ccode}CCode but {ccode}CCode was given."
            )


@dataclass
class Restriction:
    cls: type
    methods: List[Callable]
    access: Access = Access.BY_OWNER

    def __post_init__(self):
        self.ccode = hash(id(self))


class Restrictor:
    def __init__(self):
        self._restrictions = {}

    def restrict(self, restriction):
        for method in restriction.methods:
            if not callable(method):
                method = getattr(restriction.cls, method)

            self._restrictions[method] = restriction
            setattr(restriction.cls, method.__name__, self(method))

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            rest = self._restrictions[f]
            if rest.access is Access.BY_ALL:
                return f(*args, **kwargs)
            elif rest.access is Access.BY_OWNER:
                try:
                    owner = args[0]
                except IndexError:
                    owner = None

                if isinstance(owner, rest.cls):
                    return f(*args, **kwargs)
                else:
                    raise OwnerError(
                        f"`{f.__name__}` is called but caller is restricted. Only owner can call `{f.__name__}`"
                    )
            elif rest.access is Access.BY_CASE:
                if hasattr(wrapper, "EQ_W") and wrapper.EQ_W:
                    wrapper.EQ_W = False
                    return CaseWrapper(f, args, kwargs, rest.ccode)
                else:
                    raise CaseError(
                        f"`{f.__name__} is case-restricted. You should call this method in a Case with ensuring the result."
                    )
            else:
                raise RestrictionError("Access method doesn't match")
        
        return wrapper
