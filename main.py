import cmd
import os
from datetime import date

from config import *

import pandas as pd
from tabulate import tabulate
import numpy as np

DEBUG = True

today_string = date.today().strftime('%Y-%m-%d,%A')
today_record_path = DATA_CENTER + f'/{today_string}.csv'


# noinspection PyAttributeOutsideInit
class Interpreter(cmd.Cmd):
    intro = "Welcome to Project Nautilus V2.0! Type help or ? to list commands."
    prompt = "(project nautilus) "

    def preloop(self):
        """Runs before cmdloop()."""
        # Check if DATA_CENTER directory has been mkdir'ed. If not, mkdir it.
        if not os.path.exists(DATA_CENTER):
            os.makedirs(DATA_CENTER)

        # Check if today's record has been initialized. If not, initialize it.
        if not os.path.isfile(today_record_path):
            start = [':'.join(str(x).split()[-1].split(':')[:2]) for x in pd.timedelta_range(0, periods=48, freq="30T")]
            finish = start[1:] + ['00:00']
            df = pd.DataFrame(index=range(1, 49), columns=['start', 'finish', 'title', 'comment'])
            df['start'], df['finish'] = start, finish
            df.to_csv(today_record_path)

        # Read self.df from today's record. This will be the main object for us to work with.
        self.df = pd.read_csv(today_record_path, index_col=0)

        # Replace all NaNs with empty strings. This makes our life easier when dealing with updates.
        self.df.fillna('', inplace=True)

    def do_add(self, args):
        """`add <start> <finish> <title> [<description>]`: add a record.

        Params:
            - `start`: start of the activity, in HHMM format, HH in {'00', '01', ..., '23'} and MM in {'00', '30'}
            - `finish`: end of the activity, in HHMM format, HH in {'00', '01', ..., '23'} and MM in {'00', '30'}
            - `title`: title of the activity, must be registered (todo: finish this later).
            - `description`: optional, a sentence describing the activity.

        Example:
            - `add 0000 0800 sleep` => start=0000, finish=0800, title='sleep'
            - `add 1530 1630 study Review Stat230` => start=1530, end=1630, title='study', description=`Review Stat230`
        """

        # Handle input
        arg_lst = args.split(' ', 3)
        if len(arg_lst) < 3:
            print("Error: missing argument. \nUsage: `add <start> <finish> <title> [<description>]`: add a record.")
        elif len(arg_lst) == 3:
            start, finish, title = arg_lst
            description = ''
        else:
            start, finish, title, description = arg_lst

        # Calculating which rows the activity affects.
        start_idx = int(start[:2]) * 2 + 1 + (start[2:] == '30')
        finish_idx = int(finish[:2]) * 2 + 1 + (finish[2:] == '30')

        # Updating each row. todo: figure out if there is a more elegant way to do this.
        for x in range(start_idx, finish_idx):

            # Skip if the row has existing data.
            if self.df.loc[x, 'title']:
                print(f"The time period from {start} to {finish} has already been recorded.")
            else:
                self.df.loc[x, 'title'] = title
                self.df.loc[x, 'description'] = description


    def do_read(self, _):
        # print(tabulate(self.df, headers=['id', 'start', 'finish', 'category', 'title', 'description']))
        print(tabulate(self.df, headers=['id', 'start', 'finish', 'title']))
        print(self.df.dtypes)

    def do_cat(self, _):
        temp = self.df.groupby('title')['start'].nunique().apply(lambda x: str(x / 2) + "hour").sort_values(
            ascending=False)
        print(temp)

    def do_bye(self, _):
        print("Bye")
        return True

    def postloop(self):
        self.df.to_csv(today_record_path)
        print(f"Data written to {today_record_path}.")


if __name__ == '__main__':
    Interpreter().cmdloop()
