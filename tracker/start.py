from util.file_util import *
from datetime import datetime


def start(task_name):
    """ Handles the `start` command.
    Syntax: `start <task_name>`
    Function: start the timer.

    Precondition on argument `task_name`:
    - `task_name` is non-empty and is registered in global object task_keys as the the input validation has already been
    handled by the do_start() function in interpreter stage.
    """
    check_file_existence()
    check_existing_tracker()
    write_start_time_cache(task_name)


def check_file_existence():
    """Checks if START_TIME_CACHE exists. If not, create an empty START_TIME_CACHE."""
    if not file_exists(START_TIME_CACHE):
        print("DEBUG: START_TIME_CACHE does not exist. Initializing START_TIME_CACHE to empty.")
        clear_file(START_TIME_CACHE)


def check_existing_tracker():
    """Checks if an existing tracker exists. If yes, try to read info.
    If an exception is raised during the process, clear the START_TIME_CACHE."""
    if not file_is_empty(START_TIME_CACHE):
        # noinspection PyBroadException
        try:
            old_start_date, old_start_time, old_task_name = read_start_time_cache()
            print("WARNING: You have an existing tracker:",
                  f"\t Task Name: {old_task_name}",
                  f"\t Date-Time: {old_start_date} {old_start_time}",
                  "Do you want to keep this tracker? (y/n).", sep='\n')
            while True:
                response = input()
                if response == 'n':
                    print("You entered `n`. The existing record is discarded.")
                    break
                elif response == 'y':
                    print("You entered `y`.")  # todo: finish this
                    break
                else:
                    print("Sorry, I don't understand. Please try again.")

        except Exception:
            print("DEBUG: Existing START_TIME_CACHE is corrupted. Removed and initialized a new one.")

    clear_file(START_TIME_CACHE)


def write_start_time_cache(task_name):
    """ Given start_date, start_time, and task_name, write to cache file.
        Assumption on file format:
        - Line 1: start_date, '%Y-%m-%d' or YYYY-mm-dd
        - Line 2: start_time, '%H:%M:%S' or   HH:MM:SS
        - Line 3: task_name, a string
    """
    now = datetime.now()
    start_date, start_time = now.strftime(FMT_DATE), now.strftime(FMT_TIME)
    print(f"Starting task {task_name} at time {start_time}.")
    with open(START_TIME_CACHE, 'w') as f:
        f.write(start_date + '\n')
        f.write(start_time + '\n')
        f.write(task_name + '\n')
        f.flush()
    print("Data saved successfully. Enjoy!")
