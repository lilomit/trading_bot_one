import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import shutil
import pytest
import pandas as pd
from walkforward import walk_forward_validation

@pytest.fixture
def sample_data():
    rows = 40  # افزایش داده برای جلوگیری از failure
    data = {
        "Close": list(range(100, 100 + rows)),
        "Low": list(range(99, 99 + rows)),
        "High": list(range(101, 101 + rows)),
        "Signal": ['buy' if i % 5 == 0 else 'sell' if i % 7 == 0 else '' for i in range(rows)],
    }
    index = pd.date_range(start="2022-01-01", periods=rows, freq='1h')
    df = pd.DataFrame(data, index=index)
    return df

def test_save_results_creates_files(sample_data):
    results = walk_forward_validation(
        sample_data,
        strategy_func=lambda df, **kwargs: df,  # استراتژی تستی: فقط داده رو رد می‌کنه
        param_grid={
            "supertrend_period": [7],
            "rsi_period": [14],
            "rsi_buy_threshold": [30],
            "rsi_sell_threshold": [70],
            "supertrend_multiplier": [3]
        },
        n_splits=2,
        save_results_to_file=True,
        verbose=False
    )

    base_folder = "results"
    folders = [f for f in os.listdir(base_folder) if f.startswith("walkforward_")]
    assert folders, "هیچ فولدر خروجی walkforward ساخته نشده."

    output_folder = os.path.join(base_folder, sorted(folders)[-1])
    csv_path = os.path.join(output_folder, "walkforward_results.csv")
    json_path = os.path.join(output_folder, "walkforward_results.json")

    assert os.path.exists(csv_path), "فایل CSV ذخیره نشده."
    assert os.path.exists(json_path), "فایل JSON ذخیره نشده."

    df_csv = pd.read_csv(csv_path)
    assert not df_csv.empty, "فایل CSV خالی است."

    # پاکسازی بعد از تست
    shutil.rmtree(output_folder)