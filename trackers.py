from datetime import datetime
from config import *
from util.file_util import *

def add_task(task_name):
    task_name = task_name.lower()
    if task_name == '':
        print("ERROR: missing argument.")
        return
    if task_name not in task_keys:
        task_keys.append(task_name)
        with open(TASK_NAME_CACHE, 'a') as f:
            f.write(task_name + '\n')
            f.flush()
        print("New task {} has been added.".format(task_name))
    else:
        print("Task {} has been added already.".format(task_name))


def rm_task(task_name):
    task_name = task_name.lower()
    if task_name == '':
        print("ERROR: missing argument.")
        return
    if task_name in task_keys:
        task_keys.remove(task_name)
        with open(TASK_NAME_CACHE, 'w') as f:
            for task in task_keys:
                f.write(task + '\n')
            f.flush()
        print("Existing task {} has been removed.".format(task_name))
    else:
        print("Task {} does not exist.".format(task_name))


def add_record(task_name):
    pass