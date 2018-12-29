import os
import pandas as pd

PROJECT_ROOT_URL = os.path.dirname(os.path.realpath(__file__))
START_TIME_CACHE = PROJECT_ROOT_URL + "/.cache/START_TIME.txt"
TASK_NAME_CACHE = PROJECT_ROOT_URL + "/.cache/TASK_NAME.txt"
DATA_CENTER = PROJECT_ROOT_URL + "/.data/DATA_CENTER.csv"

FMT_DATE = '%Y-%m-%d'
FMT_TIME = '%H:%M:%S'
FMT_DATE_TIME = '%Y-%m-%d %H:%M:%S'

modified = False

try:
    with open(TASK_NAME_CACHE, 'r') as task_name_cache:
        task_keys = [task.strip() for task in task_name_cache.readlines()]
except FileNotFoundError:
    print("DEBUG: TASK_NAME_CACHE does not exist. Initializing.")
    task_keys = []

try:
    df = pd.read_csv(DATA_CENTER, header=0)
except FileNotFoundError:
    print("DEBUG: DATA_CENTER does not exist. Initializing.")
    with open(DATA_CENTER, 'w') as data_center:
        data_center.write('task_name,duration,start_date,start_time,end_date,end_time,message\n')
        data_center.flush()
    df = pd.read_csv(DATA_CENTER, header=0)

