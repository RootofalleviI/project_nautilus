from util.file_util import *


def add_task(task_name):
    """Handles the `add_task` command.
    Syntax: `add_task <task_name>`
    Function: register a new task in TASK_NAME_CACHE

    Precondition on argument `task_name`:
    - `task_name` is non-empty and whitespaces are stripped already.
    """
    task_name = task_name.lower()
    if task_name not in task_keys:
        task_keys.append(task_name)
        with open(TASK_NAME_CACHE, 'a') as f:
            f.write(task_name + '\n')
            f.flush()
        print("Task {} has been added.".format(task_name))
    else:
        print("Task {} has been added already.".format(task_name))


def rm_task(task_name):
    """Handles the `rm_task` command.
    Syntax: `rm_task <task_name>`
    Function: unregister an existing task from TASK_NAME_CACHE

    Precondition on argument `task_name`:
    - `task_name` is non-empty and whitespaces are stripped already.
    """
    task_name = task_name.lower()
    if task_name in task_keys:
        task_keys.remove(task_name)
        with open(TASK_NAME_CACHE, 'w') as f:
            for task in task_keys:
                f.write(task + '\n')
            f.flush()
        print("Task {} has been removed.".format(task_name))
    else:
        print("Task {} does not exist.".format(task_name))
