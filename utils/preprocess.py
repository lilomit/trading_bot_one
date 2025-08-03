# utils/preprocess.py

import pandas as pd

def ensure_datetime_index(df):
    """
    مطمئن می‌شود که ایندکس دیتافریم از نوع datetime است.
    اگر نباشد، تبدیل می‌کند و ردیف‌هایی که مقدار Close ندارند حذف می‌شوند.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=['Close'])
    return df