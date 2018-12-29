from config import *
from datetime import date, timedelta
from dateutil import relativedelta
from tabulate import tabulate

today = date.today()
col_names = ['Task Name', 'Time (min)', 'Start Date', 'Start Time', 'End Date', 'End Time',
             'Message']


def lscat(cmd: str, args: str) -> None:
    """ Handles `ls` and `cat` commands.
    - `ls`: print all relevant records on a specified task in a specified time period.
    - `cat`: print a summary on a specified task in a specified time period.

    :param cmd: specifies the command, either `ls` or `cat`.
    :param args: length <= 2, specifies relevant task or time period.
    :return: None
    """
    if modified:
        global df
        df = pd.read_csv(DATA_CENTER, header=0)

    time_flag = task_flag = None
    args = args.split()
    if len(args) > 2:
        print("ERROR: Too many options")
    for arg in args:
        if arg in task_keys:
            task_flag = arg
        elif arg in ['--today', '--week', '--month', '--year']:
            time_flag = arg
        else:
            print("ERROR: Unknown argument")
            return

    local_df = df

    if time_flag:
        start, end = resolve_time(time_flag)
        local_df = local_df.loc[(start <= local_df['end_date']) & (local_df['end_date'] < end)]
    else:
        start, end = local_df.loc[0, 'start_date'], str(today)

    if task_flag:
        local_df = local_df.loc[local_df['task_name'] == task_flag]
    else:
        task_flag = "all tasks"

    if cmd == 'ls':
        print("Listing all records on {} from {} to {}".format(task_flag, start, end))
        print(tabulate(local_df, headers=col_names, numalign='left'))
        return

    else:
        print("Summarizing records on {} from {} to {}".format(task_flag, start, end))
        num_records = len(local_df)
        sum_duration = local_df['duration'].sum()
        hours, minutes = sum_duration // 60, sum_duration % 60
        print(tabulate([
            ["Total number of records:", num_records],
            ["Total time investment:", "{}h {}min".format(hours, minutes)]
        ]))


def resolve_time(time_flag):
    """ Given a time_flag, returns the appropriate start and end date for dataframe selection.

    :param time_flag: one of {`--today`, `--week`, `--month`, `--year`}.
    :return: two strings of format YYYY-MM-DD denoting start and end dates.
    """
    start = end = None
    if time_flag == '--today':
        start = str(today)
        end = str(today + relativedelta.relativedelta(days=1))
    elif time_flag == '--week':
        start = str(today - timedelta(days=today.weekday()))
        end = str(today + timedelta(days=-today.weekday(), weeks=1))
    elif time_flag == '--month':
        start = str(today.replace(day=1))
        end = str(today.replace(day=1) + relativedelta.relativedelta(months=1))
    elif time_flag == '--year':
        start = str(today.replace(month=1, day=1))
        end = str(today.replace(month=1, day=1) + relativedelta.relativedelta(years=1))
    return start, end
