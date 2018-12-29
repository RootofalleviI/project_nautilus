from datetime import datetime
from config import *
import os

fmt_date = '%Y-%m-%d'
fmt_time = '%H:%M:%S'
fmt_date_time = '%Y-%m-%d %H:%M:%S'

with open(TASK_NAME_CACHE, 'r+') as task_name_cache:
    task_keys = [task.strip() for task in task_name_cache.readlines()]


def file_is_empty(path):
    """ Returns True if the file is empty. """
    return os.stat(path).st_size == 0


def clear_file(path):
    """ Clears content for the given file. """
    open(path, 'w').close()


def read_start_time_cache(path=START_TIME_CACHE):
    """ Return start_date, start_time, and task_name.
    Assumption on file format:
    - Line 1: start_date, '%Y-%m-%d' or YYYY-mm-dd
    - Line 2: start_time, '%H:%M:%S' or   HH:MM:SS
    - Line 3: task_name, a string
    """
    with open(path, 'r') as f:
        start_info = (x.strip() for x in f.readlines())
    return start_info


def write_start_time_cache(start_date, start_time, task_name, path=START_TIME_CACHE):
    """ Given start_date, start_time, and task_name, write to cache file.
    Assumption on file format:
    - Line 1: start_date, '%Y-%m-%d' or YYYY-mm-dd
    - Line 2: start_time, '%H:%M:%S' or   HH:MM:SS
    - Line 3: task_name, a string
    """
    with open(path, 'w') as f:
        f.write(start_date + '\n')
        f.write(start_time + '\n')
        f.write(task_name + '\n')


def write_time_data(task_name, duration, start_date, start_time, end_date, end_time, message,
                    path=DATA_CENTER):
    """ Given relevant information, write to data center (CSV file).
    Assumption on file format (columns):
    task_name, duration, start_date, start_time, end_date, end_time, message
    """
    entry = "{}, {}, {}, {}, {}, {}, {}".format(task_name, duration, start_date, start_time,
                                                end_date, end_time, message)
    with open(path, 'a') as f:
        f.write(entry + '\n')


def start(task_name):
    if task_name not in task_keys:
        print("ERROR: Task name {} not found.".format(task_name))
        print("       Type `tasks` to see existing tasks.")
    else:
        validate_start(task_name)


def validate_start(task_name):
    try:
        if not file_is_empty(START_TIME_CACHE):
            old_start_date, old_start_time, old_task_name = read_start_time_cache()
            print("WARNING: You have an existing tracker:",
                  "\t Task Name: {}".format(old_task_name),
                  "\t Date-Time: {}".format(old_start_date, old_start_time),
                  "Do you want to keep this tracker? (Y/N).", sep='\n')
            while True:
                response = input()
                if response == 'Y':
                    pass
                elif response == 'N':
                    print("You entered: N. Tracker removed.")
                    break
                else:
                    print("Sorry, I don't understand. Please try again.")
            clear_file(START_TIME_CACHE)

    except FileNotFoundError:
        print("INFO: START_TIME_CACHE does not exist.",
              "      Creating empty START_TIME_CACHE file.", sep='\n')

    now = datetime.now()
    now_date, now_time = now.strftime(fmt_date), now.strftime(fmt_time)
    print("Starting task {} at time {}.".format(task_name, now_time))
    write_start_time_cache(now_date, now_time, task_name)
    print("Data saved successfully. Enjoy!")


def stop(message):
    try:
        start_date, start_time, task_name = read_start_time_cache()
        now = datetime.now()
        now_date, now_time = now.strftime(fmt_date), now.strftime(fmt_time)
        print("Stopping task {} at time {}.".format(task_name, now_time))
        start_date_time = start_date + ' ' + start_time
        end_date_time = now_date + ' ' + now_time
        duration = datetime.strptime(end_date_time, fmt_date_time) - \
            datetime.strptime(start_date_time, fmt_date_time)
        if len(str(duration)) != 8:
            raise ValueError()
        print("You have invested {} in {}.".format(duration, task_name))
        write_time_data(task_name, duration, start_date, start_time, now_date, now_time, message)
        clear_file(START_TIME_CACHE)
        print("Data saved successfully. Take a break!")

    except FileNotFoundError:
        print("ERROR: START_TIME_CACHE does not exist.",
              "       Operation aborted. Please start a new tracker.", sep='\n')

    except ValueError:
        print("ERROR: Tracker lasted for more than 24 hours!"
              "       Operation aborted. Please start a new tracker.", sep='\n')

    except Exception as e:
        print("THE FOLLOWING ERROR HAS BEEN THROWN:")
        print(e)
        print("PLEASE LOOK AT THE SOURCE CODE OR CONTACT THE DEVELOPER.")
