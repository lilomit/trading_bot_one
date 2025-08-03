# utils/time.py

def convert_interval_to_minutes(interval):
    interval = interval.upper()
    if interval.endswith('T'):
        return int(interval[:-1])
    elif interval == '1H':
        return 60
    elif interval == '1D':
        return 1440
    else:
        return 60


def convert_interval_to_pandas_freq(interval):
    interval = interval.upper()
    if interval.endswith('T'):
        return interval[:-1] + 'min'
    elif interval.endswith('H'):
        return interval[:-1] + 'h'
    elif interval.endswith('D'):
        return interval[:-1] + 'd'
    else:
        return interval