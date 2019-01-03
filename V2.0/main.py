import cmd
import os
from datetime import date, time, datetime, timedelta
from pathlib import Path
import pandas as pd


HOME = str(Path.home())
PROJECT_ROOT_URL = HOME + '/.nautilus'
DATA_CENTER = PROJECT_ROOT_URL + "/.data/daily"

DEBUG = True


class Interpreter(cmd.Cmd):

    intro = "Welcome to Project Nautilus V2.0! Type help or ? to list commands."
    prompt = "(project nautilus) "

    def preloop(self):
        """Make sure relevant directories have been mkdir'ed."""
        if not os.path.exists(DATA_CENTER):
            os.makedirs(DATA_CENTER)

    def do_init(self, _):
        """`init`: initialize today's record."""
        today = date.today()
        today_as_str = today.strftime('%Y-%m-%d,%A')
        file_path = DATA_CENTER + f'/{today_as_str}.csv'

        if os.path.isfile(file_path):
            debug("File exists.")
            print("Today's record has been initialized already.")
        else:
            debug(f"Initializing {file_path}")
            init_record(file_path)
            print("Today's record has been initialized successfully.")

    def do_add(self, args):
        """`add <start> <finish> <title> <description>"""
        arg_lst = args.split(' ', 3)
        print(arg_lst)

    def do_bye(self, _):
        print("Bye")
        return True

def debug(s):
    if DEBUG:
        print(f"DEBUG: {s}")


def format_time(timeindex):
    return ':'.join(str(timeindex).split()[-1].split(':')[:2])


def init_record(file_path):
    start = [format_time(x) for x in list(pd.timedelta_range(0, periods=48, freq="30T"))]
    finish = start[1:] + ['00:00']
    columns = ['start', 'finish', 'category', 'title', 'description']
    df = pd.DataFrame(index=range(1, 49), columns=columns)
    df['start'], df['finish'] = start, finish
    df.to_csv(file_path)



if __name__ == '__main__':
    Interpreter().cmdloop()
