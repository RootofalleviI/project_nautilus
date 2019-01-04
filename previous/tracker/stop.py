from util.file_util import *
from datetime import datetime


def stop(message):
    """ Handles the `stop` command.

    Syntax: `start <message>`
    Function: stop the timer.

    Precondition on argument `message`:
    - `message` is an non-empty string as the the input validation has already been handled by the do_stop() function in
    interpreter stage.
    """
    # noinspection PyBroadException
    try:
        start_date, start_time, task_name = read_start_time_cache()
        now = datetime.now()
        end_date, end_time = now.strftime(FMT_DATE), now.strftime(FMT_TIME)
        print(f"Stopping task {task_name} at time {end_time}.")

        start_date_time = start_date + ' ' + start_time
        end_date_time = end_date + ' ' + end_time
        duration = datetime.strptime(end_date_time, FMT_DATE_TIME) - datetime.strptime(start_date_time, FMT_DATE_TIME)

        if len(str(duration)) > 8:
            raise ValueError()

        h, m, s = str(duration).split(':')
        duration = int(h) * 60 + int(m)
        print(f"({start_time} to {end_time}) You have invested {duration} minutes in {task_name}.")

        write_time_data(task_name, duration, start_date, start_time, end_date, end_time, message)
        clear_file(START_TIME_CACHE)
        print("Data saved successfully. Take a break!")

    except FileNotFoundError:
        print("ERROR: START_TIME_CACHE does not exist. Please start a new timer.")

    except ValueError:
        start_date_time = end_date_time = ''
        print(f"({start_date_time} to {end_date_time}) ERROR: Timer lasted for more than 24 hours! Operation aborted. "
              "Please start a new timer.")

    except Exception:
        print("ERROR: No timer is running or START_TIME_CACHE is corrupted. Please start a new timer.")
