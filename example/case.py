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
