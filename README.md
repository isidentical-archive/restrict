# Restrict
Restrict python methods 

# Example 1
```py
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

```
Output
```
defaultdict(<class 'list'>, {})
Case error on import
Case error on build class
```
# Example 2
```py
from restrict import *


class TaskManager:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task: str, *items):
        self.tasks[task] = items

    def pop_task(self):
        return self.tasks.popitem()

    def get_tasks(self, task: str):
        return self.tasks[task]

    def add(self, x1, x2):
        return x1 + x2


restrictor = Restrictor()

```
### By Case
```py
restriction = Restriction(
    TaskManager, ["add_task", "pop_task", TaskManager.get_tasks, "add"], Access.BY_CASE
)
restrictor.restrict(restriction)
t = TaskManager()
try:
    t.add(3, 2)
except CaseError:
    print("A case error just occured")

with case(hash(id(restriction))) as ensured_call:
    z = ensured_call(t.add, 3, 2)
    assert z == 5
```
Output
```
A case error just occured
```
### By Owner
```
restrictor = Restrictor()
restriction = Restriction(
    TaskManager, ["add_task", "pop_task", TaskManager.get_tasks, "add"], Access.BY_OWNER
)
restrictor.restrict(restriction)
t = TaskManager()
t.add_task("a", "b")
y = t.add(3, 2)
assert y == 5
try:
    z = TaskManager.add(object(), 3, 2)
    assert z == 5
except OwnerError as exc:
    print("An owner error just occured")
```
Output
```
An owner error just occured
```
