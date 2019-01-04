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
            df = pd.DataFrame(index=range(1, 49), columns=['start', 'finish', 'title', 'description'])
            df['start'], df['finish'] = start, finish
            df.to_csv(today_record_path)

        # Read self.df from today's record. This will be the main object for us to work with.
        self.df = pd.read_csv(today_record_path, index_col=0)

        # Replace all NaNs with empty strings. This makes our life easier when dealing with updates.
        self.df.fillna('', inplace=True)

    def do_add(self, args):
        """`add <start-finish> <title> [<description>]`: add a record.

        Params:
        - `<title>`: title of the activity, must be registered (todo: finish this later).
        - `<start-finish>`: start and end of the activity, in HHMM-HHMM format (see shortcuts below), where
            1. HH in {'00', '01', ..., '23'} and MM in {'00', '30'}
            2. the first HHMM represents the start and the second HHMM represents the end, see example 0.
            3. shortcut 1: if <start-finish> is of the form HHMM, start is set to HHMM and finish is set to
                (start + 30min), see example 1.
            4. shortcut 2: if <start-finish> is of the form HHMM- (notice this dash), start is set to HHMM and
                finish is set to midnight of tomorrow; it has the same effect as HHMM-0000, see example 2.
            5. shortcut 3: if <start-finish> is of the form -HHMM (notice this dash), start is set to 0000,
                midnight of today, and finish is set to HHMM; it has the same effect as 0000-HHMM, see example 3.

        - `<description>`: optional, a sentence describing the activity, see example 4.

        Example:
            0. `add 1330-1430 read`     => start=1330, finish=1430, title='read', description=''
            1. `add 1500 break`         => start=1500, finish=1530, title='break', description=''
            2. `add 2300- sleep`        => start=2300, finish=0000, title='sleep', description=''
            3. `add -0800 sleep`        => start=0000, finish=0800, title='sleep', description=''
            4. `add 1530-1630 study Review Stat230` => start=1530, end=1630, title='study', description=`Review Stat230`
        """

        # Extract title and description
        arg_lst = args.split(' ', 2)
        if len(arg_lst) < 2:
            print("Error: missing argument. \nUsage: `add <start[-finish]> <title> [<description>]`: add a record.")
        elif len(arg_lst) == 2:
            title, description = arg_lst[1], ''
        else:
            title, description = arg_lst[1], arg_lst[2]

        # Extract start and finish
        time_args = arg_lst[0].split('-')
        if len(time_args) == 1:
            start = time_args[0] if time_args else '0000'
            finish = str(int(start[:2]) + 1) + '00' if start[-2:] == '30' else start[:2] + '30'
        elif len(time_args) == 2:
            start, finish = time_args[0], time_args[1] if time_args[1] else '2400'

        # Calculating which rows the activity affects.
        start_idx = int(start[:2]) * 2 + 1 + (start[2:] == '30')
        finish_idx = int(finish[:2]) * 2 + 1 + (finish[2:] == '30')

        # Updating each row. todo: figure out if there is a more elegant way to do this.
        for x in range(start_idx, finish_idx):

            # Skip if the row has existing data.
            if self.df.loc[x, 'title']:
                print(f"Time period {x} has existing data. Skipped.")
            else:
                self.df.loc[x, 'title'] = title
                self.df.loc[x, 'description'] = description


    def do_read(self, _):
        print(tabulate(self.df, headers=['id', 'start', 'finish', 'title', 'description'], tablefmt="grid"))

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
