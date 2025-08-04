import os
from datetime import datetime

def create_output_folder(base_folder="results", strategy_name=None):
    """
    ساخت فولدر خروجی با نام استراتژی و زمان اجرا به شکل:
    results/strategyName_YYYYMMDD_HHMMSS
    اگر strategy_name داده نشه فقط فولدر با timestamp ساخته میشه.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{strategy_name}_{timestamp}" if strategy_name else timestamp
    folder_path = os.path.join(base_folder, folder_name)

    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def get_filepath(folder_path, filename):
    """
    مسیر کامل فایل داخل فولدر مشخص شده رو میسازه.
    """
    return os.path.join(folder_path, filename)