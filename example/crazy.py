from restrict import *
import builtins
r = Restrictor()
restriction = Restriction(
    builtins, ['__import__', '__build_class__'], Access.BY_CASE
)
r.restrict(restriction)

with case(hash(id(restriction))) as ensured_call:
    collections = ensured_call(builtins.__import__, 'collections')
    Y = ensured_call(builtins.__build_class__, lambda: ..., 'Y')
    assert isinstance(Y, type)
    
print(collections.defaultdict(list))
try:
    import math
except CaseError:
    print('Case error on import')
    
try:
    class X:
        pass
except CaseError:
    print('Case error on build class')
