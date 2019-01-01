from datetime import datetime, timedelta
from util.file_util import *
from config import *


def collect_info(prompt, validation):
    while True:
        response = input(prompt).strip()
        if validation(response):
            return response
        else:
            print("Sorry, I don't understand. Please try again.")


def validation_date(date_text):
    if date_text:
        try:
            datetime.strptime(date_text, FMT_DATE)
        except ValueError:
            return False
    return True


def validation_time(time_text):
    try:
        datetime.strptime(time_text, FMT_TIME)
    except ValueError:
        return False
    return True


def add_record(task_name):
    """ Handles the `add_record` command.

    Syntax: `add_record <task_name>`
    Function: add an untracked record (more prompts to further collection info)

    Precondition on argument `message`:
    - `message` is an non-empty string as the the input validation has already been handled by the do_stop() function
    in interpreter stage.
    """
    start_date = collect_info("Enter start_date in YYYY-mm-dd format (empty => start_date = today): ",
                              validation_date)
    if not start_date:
        start_date = datetime.now().strftime(FMT_DATE)

    start_time = collect_info("Enter start_time in HH:MM:SS format: ", validation_time)

    start_date_as_date = datetime.strptime(start_date, FMT_DATE)
    start_date_time_as_datetime = datetime.strptime(start_date + ' ' + start_time, FMT_DATE_TIME)

    while True:
        end_date = collect_info("Enter end_date in YYYY-mm-dd format (empty => end_date = start_date): ",
                                validation_date)
        if not end_date:
            end_date = start_date
        end_date_as_date = datetime.strptime(end_date, FMT_DATE)
        if (start_date_as_date <= end_date_as_date) and \
                (end_date_as_date - timedelta(days=1) <= start_date_as_date <= end_date_as_date):
            break
        else:
            print("ERROR: end_date is more than 1 day after start_date or end_date is before start_date.",
                  "Please try again.", sep='\n')

    while True:
        end_time = collect_info("Enter end_time in HH:MM:SS format: ", validation_time)
        end_date_time_as_datetime = datetime.strptime(end_date + ' ' + end_time, FMT_DATE_TIME)
        if (start_date_time_as_datetime <= end_date_time_as_datetime) and \
            (end_date_time_as_datetime - timedelta(hours=24) <=
                start_date_time_as_datetime <= end_date_time_as_datetime):
            break
        else:
            print("ERROR: end_datetime is more than 24 hours after start_datetime or end_datetime is before "
                  "start_datetime.",
                  "Please try again.", sep='\n')

    while True:
        message = input("Enter your comment, press ENTER to finish: ")
        print(f"You entered: {message}. To confirm, type Y; to re-enter, type N.")
        response = input()
        if response == 'Y':
            break

    print("To confirm your input, type Y. To abort, type N.")
    print(f"start_date: {start_date}",
          f"start_time: {start_time}",
          f"end_date: {end_date}",
          f"end_time: {end_time}",
          f"message: {message}", sep='\n')
    while True:
        response = input()
        if response == 'N':
            return
        elif response == 'Y':
            break
        else:
            print("Sorry, I don't understand. Please try again.")

    duration = end_date_time_as_datetime - start_date_time_as_datetime

    h, m, s = str(duration).split(':')
    duration = int(h) * 60 + int(m)
    print(f"({start_time} to {end_time}) You have invested {duration} minutes in {task_name}.")

    write_time_data(task_name, duration, start_date, start_time, end_date, end_time, message)
    print("Data saved successfully. Take a break!")
