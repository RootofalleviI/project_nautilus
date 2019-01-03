import cmd
import os
from datetime import date
from pathlib import Path
import pandas as pd
from tabulate import tabulate
import numpy as np


HOME = str(Path.home())
PROJECT_ROOT_URL = HOME + '/.nautilus'
DATA_CENTER = PROJECT_ROOT_URL + "/.data/daily"

DEBUG = True

today_as_str = date.today().strftime('%Y-%m-%d,%A')
today_record_path = DATA_CENTER + f'/{today_as_str}.csv'

class Interpreter(cmd.Cmd):

    intro = "Welcome to Project Nautilus V2.0! Type help or ? to list commands."
    prompt = "(project nautilus) "

    def preloop(self):
        """Make sure relevant directories have been mkdir'ed."""
        if not os.path.exists(DATA_CENTER):
            os.makedirs(DATA_CENTER)
        if not os.path.isfile(today_record_path):
            start = [format_time(x) for x in list(pd.timedelta_range(0, periods=48, freq="30T"))]
            finish = start[1:] + ['00:00']
            columns = ['start', 'finish', 'category', 'title', 'description']
            df = pd.DataFrame(index=range(1, 49), columns=columns)
            df['start'], df['finish'] = start, finish
            df.to_csv(today_record_path)
        self.df = pd.read_csv(today_record_path, index_col=0)
        self.df.fillna('None', inplace=True)

    def do_add(self, args):
        """`add <start> <finish> <title> <description>"""
        arg_lst = args.split(' ', 3)
        if len(arg_lst) != 4:
            print("Error: Wrong number of arguments. \nUsage: `add <start> <finish> <title> <description>")
        start, finish, title, description = arg_lst
        start_idx = int(start[:2]) * 2 + 1 + (start[2:] == '30')
        finish_idx = int(finish[:2]) * 2 + 1 + (finish[2:] == '30')
        for x in range(start_idx, finish_idx):
            if self.df.loc[x,'title'] != 'None':
                print("title assigned.")
            else:
                self.df.loc[x,'title'] = title
            if self.df.loc[x,'description'] != 'None':
                print("desc assigned")
            else:
                self.df.loc[x,'description'] = description
        print(self.df)
        print(self.df.dtypes)

    def do_read(self, _):
        print(tabulate(self.df, headers=['id', 'start', 'finish', 'category', 'title', 'description']))
        print(self.df.dtypes)

    def do_bye(self, _):
        print("Bye")
        return True

def format_time(i):
    return ':'.join(str(i).split()[-1].split(':')[:2])

if __name__ == '__main__':
    Interpreter().cmdloop()
