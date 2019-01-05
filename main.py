import cmd
import os
from datetime import date

from config import *

import pandas as pd
from tabulate import tabulate

DEBUG = True

today_string = date.today().strftime('%Y-%m-%d,%A')
today_record_path = DATA_CENTER + f'/{today_string}.csv'


# noinspection PyAttributeOutsideInit,PyMethodMayBeStatic
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

        # Replace all NaNs with empty 'N/A'. This makes our life easier when dealing with updates and cats.
        self.df.fillna('N/A', inplace=True)

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
        self._modify(args, False)

    def do_set(self, args):
        """`set <start-finish> <title> [<description>]`: essentially same as add but instead of skipping when a time
        period has existing data, this overwrites it. Therefore, make sure you know what you are doing when using this
        command!"""
        # Extract title and description
        self._modify(args, True)

    def _modify(self, args, replace):
        """Helper function for do_add and do_set."""
        # Extract title and description
        arg_lst = args.split(' ', 2)
        if len(arg_lst) < 2:
            raise Exception("Error: missing argument."
                            "Usage: `add <start[-finish]> <title> [<description>]`: add a record.")
        elif len(arg_lst) == 2:
            title, description = arg_lst[1], ''
        else:
            title, description = arg_lst[1], arg_lst[2]

        # Extract start and finish
        time_args = arg_lst[0].split('-')
        if len(time_args) == 1:
            start = time_args[0] if time_args[0] else '0000'
            finish = str(int(start[:2]) + 1) + '00' if start[-2:] == '30' else start[:2] + '30'
        elif len(time_args) == 2:
            start, finish = time_args[0] if time_args[0] else '0000', time_args[1] if time_args[1] else '2400'
        else:
            raise Exception("Error: <start-finish> not in the correct format."
                            "Usage: `add <start[-finish]> <title> [<description>]`: add a record.")

        # Calculating which rows the activity affects.
        start_idx = int(start[:2]) * 2 + 1 + (start[2:] == '30')
        finish_idx = int(finish[:2]) * 2 + 1 + (finish[2:] == '30')

        # Updating each row. todo: figure out if there is a more elegant way to do this.
        for x in range(start_idx, finish_idx):
            x_start = str((x - 1) // 2).rjust(2, '0') + ':' + ('30' if (x - 1) % 2 == 1 else '00')
            x_end = str(int(x_start[:2]) + 1).rjust(2, '0') + ':00' if x_start[-2:] == '30' else x_start[:2] + ':30'

            # `add`: Skip if the row has existing data.
            if not replace:
                if self.df.loc[x, 'title'] != 'N/A':
                    print(f"Time period {x_start}-{x_end} has existing data. Skipped.")
                else:
                    self.df.loc[x, 'title'] = title
                    self.df.loc[x, 'description'] = description
                    print(f"Time period {x_start}-{x_end} has been updated: title={title}, description={description}")

            # `set`: Overwrite the rows.
            else:
                self.df.loc[x, 'title'] = title
                self.df.loc[x, 'description'] = description
                print(f"Time period {x_start}-{x_end} has been updated: title={title}, description={description}")

    def do_ls(self, _):
        """`ls`: view today's record."""
        print(tabulate(self.df, headers=['#', 'start', 'finish', 'title', 'description']))

    def do_write(self, _):
        """`write`: write current data to file."""
        self.df.to_csv(today_record_path)

    def do_cat(self, _):
        """`cat`: view today's summary"""
        data = self.df.groupby('title')['start'].nunique().apply(lambda x: x/2).sort_values(ascending=False)
        if 'N/A' in data.index:
            not_applicable = data['N/A']
            data = data.drop('N/A', axis=0)
            print(f"\nNot applicable: {not_applicable} hours.")
        print(tabulate([(x, hr) for x, hr in zip(data.index, data)], headers=['Activity', 'Hours'], numalign='right'))

    def do_bye(self, _):
        """`bye`: cy@"""
        print("Bye")
        return True

    def postloop(self):
        self.df.to_csv(today_record_path)
        print(f"Data written to {today_record_path}.")


if __name__ == '__main__':
    Interpreter().cmdloop()
