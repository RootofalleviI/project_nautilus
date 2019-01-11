import cmd
import os
from datetime import date

import plotly.offline as py
import plotly.graph_objs as go

from config import *

import pandas as pd
from tabulate import tabulate


TRIAL = True
DEBUG = True

if DEBUG:
    today_string = '2019-01-01,Tuesday'
else:
    today_string = date.today().strftime('%Y-%m-%d,%A')
today_record_path = SRC_DATA + f'/{today_string}.csv'
today_summary_path = ETL_DATA + f'/{today_string}.csv'

# noinspection PyAttributeOutsideInit,PyMethodMayBeStatic
class Interpreter(cmd.Cmd):
    intro = "Welcome to Project Nautilus V2.0! Type help or ? to list commands."
    prompt = "(project nautilus) "

    def preloop(self):
        """Runs before cmdloop()."""
        # Check if SRC_DATA directory has been mkdir'ed. If not, mkdir it.
        if not os.path.exists(SRC_DATA):
            os.makedirs(SRC_DATA)

        # Check if ETL_DATA directory has been mkdir'ed. If not, mkdir it.
        if not os.path.exists(ETL_DATA):
            os.makedirs(ETL_DATA)

        # Check if TASK_NAME file exists. If not, prompt the user to create it and quit.
        if not TRIAL and not os.path.isfile(ACTIVITY_CACHE):
            print("ACTIVITY_CACHE does not exist!")  # todo: finish this
            return False
        else:
            self.activities = {}
            with open(ACTIVITY_CACHE, 'r') as f:
                for line in f:
                    lst = line.split(':')
                    assert len(lst) == 2, ValueError("ACTIVITY_CACHE is corrupted: two colons in a line.")
                    self.activities[lst[0]] = [x.strip(' \n').lower() for x in lst[1].split(',')]

        # Check if today's record has been initialized. If not, initialize it.
        if not os.path.isfile(today_record_path):
            start = [':'.join(str(x).split()[-1].split(':')[:2]) for x in pd.timedelta_range(0, periods=48, freq="30T")]
            finish = start[1:] + ['00:00']
            df = pd.DataFrame(index=range(1, 49), columns=['start', 'finish', 'category', 'title', 'description'])
            df['start'], df['finish'] = start, finish
            df.to_csv(today_record_path)

        # Read self.df from today's record. This will be the main object for us to work with.
        self.df = pd.read_csv(today_record_path, index_col=0)

        # Replace all NaNs with empty 'N/A'. This makes our life easier when dealing with updates and cats.
        self.df.fillna('N/A', inplace=True)

        self.data_category = None

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

    # noinspection PyUnboundLocalVariable
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

        if not TRIAL:
            assert self.activity_exists(title), ValueError("Activity does not exist.")

        # Figure out category
        for c, activities in self.activities.items():
            if title in activities:
                category = c

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
                    self.df.loc[x, 'category'] = category
                    print(f"Time period {x_start}-{x_end} has been updated: category={category}, title={title}, "
                          f"description={description}")

            # `set`: Overwrite the rows.
            else:
                self.df.loc[x, 'title'] = title
                self.df.loc[x, 'description'] = description
                self.df.loc[x, 'category'] = category
                print(f"Time period {x_start}-{x_end} has been updated: category={category}, title={title}, "
                      f"description={description}")

    def do_act(self, _):
        """`act`: view all registered activities."""
        for k, v in self.activities.items():
            print(k, ':', v)

    def do_ls(self, args):
        """`ls`: view today's record."""
        if args:
            assert args in self.activities.keys(), ValueError("ls: Unknown category.")
            self._ls_category(args)
        else:
            print(tabulate(self.df, headers=['#', 'start', 'finish', 'category', 'title', 'description']))

    def _ls_category(self, category):
        """view today's record on a specified category."""
        data = self.df[self.df['category'] == category]
        print(tabulate(data, headers=['#', 'start', 'finish', 'category', 'title', 'description']))

    def do_write(self, _):
        """`write`: write current data to file."""
        self.df.to_csv(today_record_path)

    def do_summarize(self, _):
        """`summarize`: summarize time usage to file."""
        data = self.df.groupby(['category', 'title'])['start'].nunique() \
            .sort_values(ascending=False).apply(lambda x: x/2)
        data.to_csv(today_summary_path)
        print(tabulate([(x, hr) for x, hr in zip(data.index, data)],
                       headers=['Activity', 'Hour(s)'], numalign='right', tablefmt='grid'))

    def do_cat(self, args):
        """`cat`: view today's summary"""
        if args:
            if args == '--all':
                for k in self.activities.keys():
                    self._cat_category(k)
            else:
                assert args in self.activities.keys(), ValueError("cat: Unknown category.")
                self._cat_category(args)
        else:
            self.data_category = self.df.groupby('category')['start'].nunique()\
                .sort_values(ascending=False).apply(lambda x: x/2)
            if 'N/A' in self.data_category.index:
                not_applicable = self.data_category['N/A']
                data_category = self.data_category.drop('N/A', axis=0)
                print(f"\nNot applicable: {not_applicable} hours.")
            print(tabulate([(x, hr) for x, hr in zip(self.data_category.index, self.data_category)],
                           headers=['Category', 'Hour(s)'], numalign='right', tablefmt='grid'))

    def _cat_category(self, category):
        """view today's summary on a specified category"""
        print(f"> Data on {category}:")
        data = self.df[self.df['category'] == category].groupby(['category', 'title'])['start'].nunique()\
            .sort_values(ascending=False).apply(lambda x: x/2)
        print(tabulate([(x, hr) for x, hr in zip(data.index, data)],
                       headers=['Activity', 'Hour(s)'], numalign='right', tablefmt='grid'))

    def do_bye(self, _):
        """`bye`: cy@"""
        print("Bye")
        return True

    def activity_exists(self, activity):
        """Check if the activity is recorded in self.activities (or ACTIVITY_CACHE)."""
        return activity in [x for sublist in self.activities.values() for x in sublist]

    def postloop(self):
        self.df.to_csv(today_record_path)
        print(f"Data written to {today_record_path}.")

    def do_plot(self, args):
        # todo: ask someone for color palette
        if not self.data_category:
            self.do_cat('')
        labels = list(self.data_category.index)
        values = self.data_category
        trace = go.Pie(
            labels=labels, values=values,
            textinfo='label+value',
            hoverinfo='label+value+percent',
            textfont={'size': 20}
        )
        py.plot([trace], filename='basic_pie_chart.html', auto_open=True)





if __name__ == '__main__':
    Interpreter().cmdloop()
