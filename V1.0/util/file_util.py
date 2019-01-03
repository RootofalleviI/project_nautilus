import os
from config import *


def file_exists(file_path):
    """Returns True if the file exists. """
    return os.path.isfile(file_path)


def file_is_empty(file_path):
    """Returns True if the file is empty. """
    return os.stat(file_path).st_size == 0


def clear_file(file_path):
    """ Clears content for the given file. """
    open(file_path, 'w').close()


def read_start_time_cache(file_path=START_TIME_CACHE):
    """ Return start_date, start_time, and task_name.
    Assumption on file format:
    - Line 1: start_date, '%Y-%m-%d' or YYYY-mm-dd
    - Line 2: start_time, '%H:%M:%S' or   HH:MM:SS
    - Line 3: task_name, a string
    """
    with open(file_path, 'r') as f:
        start_info = (x.strip() for x in f.readlines())
    return start_info


def write_time_data(task_name, duration, start_date, start_time, end_date, end_time, message, path=DATA_CENTER):
    """ Given relevant information, write to database (CSV file).
    Assumption on file format (columns): task_name, duration, start_date, start_time, end_date, end_time, message
    """
    entry = "{},{},{},{},{},{},{}".format(task_name, duration, start_date, start_time, end_date, end_time, message)
    with open(path, 'a') as f:
        f.write(entry + '\n')
        f.flush()
    global df_modified
    df_modified = True

